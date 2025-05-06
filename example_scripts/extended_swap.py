# from example_scripts.debug_swap import JSON_RPC_BASE
from gmx_python_sdk.scripts.v2.utils.exchange import execute_with_oracle_params
from gmx_python_sdk.scripts.v2.utils.hash_utils import hash_data
from utils import _set_paths

_set_paths()

from eth_utils import to_checksum_address
from web3 import Web3
from hexbytes import HexBytes

from gmx_python_sdk.scripts.v2.gmx_utils import (
    ConfigManager,
    contract_map,
    convert_to_checksum_address,
    create_connection,
    get_datastore_contract,
    get_exchange_router_contract,
    get_estimated_swap_output,
    order_type,
    decrease_position_swap_type,
)
from gmx_python_sdk.scripts.v2.gas_utils import get_execution_fee, get_gas_limits
from gmx_python_sdk.scripts.v2.order.create_swap_order import SwapOrder
from gmx_python_sdk.scripts.v2.order.order_argument_parser import OrderArgumentParser
from gmx_python_sdk.scripts.v2.get.get_oracle_prices import OraclePrices
from gmx_python_sdk.scripts.v2.get.get_markets import Markets
from gmx_python_sdk.scripts.v2.keys import create_hash_string

import os
import logging
import time

JSON_RPC_BASE = "https://virtual.arbitrum.rpc.tenderly.co/94ce29a3-cca4-4d0e-9d83-24e6a16a4cbb"

# Create the ORDER_LIST key directly
ORDER_LIST = create_hash_string("ORDER_LIST")


# Extend the SwapOrder class with new methods
class EnhancedSwapOrder(SwapOrder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def create_order_and_get_key(self):
        """Create a swap order and return the order key"""
        user_wallet_address = self.config.user_wallet_address

        self.determine_gas_limits()
        if not self.debug_mode:
            self.check_for_approval()

        # Calculate execution fee
        gas_price = self._connection.eth.gas_price
        execution_fee = int(
            get_execution_fee(self._gas_limits, self._gas_limits_order_type, gas_price) * self.execution_buffer
        )

        # Build order parameters
        order_typez = order_type["market_swap"]

        # Get minimum output amount from estimation
        estimated_output = self.estimated_swap_output(
            Markets(self.config).info[self.swap_path[0]], self.collateral_address, self.initial_collateral_delta_amount
        )
        min_output_amount = int(
            estimated_output["out_token_amount"] - estimated_output["out_token_amount"] * self.slippage_percent
        )

        # Setup order arguments
        callback_gas_limit = 0
        decrease_position_swap_typez = decrease_position_swap_type["no_swap"]
        should_unwrap_native_token = True
        referral_code = HexBytes("0x0000000000000000000000000000000000000000000000000000000000000000")
        eth_zero_address = convert_to_checksum_address(self.config, "0x0000000000000000000000000000000000000000")
        ui_ref_address = convert_to_checksum_address(self.config, "0x0000000000000000000000000000000000000000")
        gmx_market_address = "0x0000000000000000000000000000000000000000"  # Not important for swap
        acceptable_price = 0  # Not important for swap

        arguments = (
            (
                user_wallet_address,
                user_wallet_address,  # cancellation_receiver
                eth_zero_address,
                ui_ref_address,
                gmx_market_address,
                self.collateral_address,
                self.swap_path,
            ),
            (
                0,  # size_delta
                self.initial_collateral_delta_amount,
                0,  # mark_price
                acceptable_price,
                execution_fee,
                callback_gas_limit,
                int(min_output_amount),
                0,  # valid_from_time
            ),
            order_typez,
            decrease_position_swap_typez,
            self.is_long,
            should_unwrap_native_token,
            False,  # auto_cancel
            referral_code,
        )

        # Build transaction
        value_amount = execution_fee
        if self.collateral_address != "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1":
            multicall_args = [
                HexBytes(self._send_wnt(value_amount)),
                HexBytes(self._send_tokens(self.collateral_address, self.initial_collateral_delta_amount)),
                HexBytes(self._create_order(arguments)),
            ]
        else:
            # Send start token and execute fee if token is ETH
            value_amount = self.initial_collateral_delta_amount + execution_fee
            multicall_args = [
                HexBytes(self._send_wnt(value_amount)),
                HexBytes(self._create_order(arguments)),
            ]

        # Submit transaction and get receipt
        tx_hash = self._submit_transaction(
            user_wallet_address, value_amount, multicall_args, self._gas_limits, return_hash=True
        )

        print(f"Order creation transaction hash: {tx_hash.hex()}")
        receipt = self._connection.eth.wait_for_transaction_receipt(tx_hash)
        # for log in receipt.logs:
        #     # Try to decode logs if you have relevant ABIs
        #     print(f"Log topics: {log['topics']}")
        #     print(f"Log data: {log['data'].hex()}")

        # Get the order key from datastore using the ORDER_LIST constant we created
        datastore = get_datastore_contract(self.config)
        order_count = datastore.functions.getBytes32Count(ORDER_LIST).call()
        if order_count == 0:
            raise Exception("No orders found")

        # Get the most recent order key
        order_key = datastore.functions.getBytes32ValuesAt(ORDER_LIST, order_count - 1, order_count).call()[0]
        print(f"Order created with key: {order_key.hex()}")

        # Give blockchain a moment to process
        time.sleep(2)

        return order_key

    def execute_order(self, order_key, overrides=None):
        """Execute an order with oracle prices"""

        if overrides is None:
            overrides = {}
        # Get the datastore contract
        # datastore = get_datastore_contract(self.config)

        # Process override parameters
        gas_usage_label = overrides.get("gas_usage_label")
        oracle_block_number_offset = overrides.get("oracle_block_number_offset")

        # Set token addresses if not provided
        tokens = overrides.get(
            "tokens",
            [
                to_checksum_address("0xf97f4df75117a78c1a5a0dbb814af92458539fb4"),  # LINK on Arbitrum
                to_checksum_address("0x2bcC6D6CdBbDC0a4071e48bb3B969b06B3330c07"),  # SOL on Arbitrum
            ],
        )

        # Set default parameters if not provided
        data_stream_tokens = overrides.get("data_stream_tokens", [])
        data_stream_data = overrides.get("data_stream_data", [])
        price_feed_tokens = overrides.get("price_feed_tokens", [])
        precisions = overrides.get("precisions", [8, 18])

        # Default prices (equivalent to expandDecimals(5000, 4) and expandDecimals(1, 6) in JS)
        min_prices = overrides.get("min_prices", [5000 * 10**4, 1 * 10**6])
        max_prices = overrides.get("max_prices", [5000 * 10**4, 1 * 10**6])

        # Get oracle block number if not provided
        oracle_block_number = overrides.get("oracle_block_number")
        if not oracle_block_number:
            oracle_block_number = self._connection.eth.block_number

        # Apply oracle block number offset if provided
        if oracle_block_number_offset:
            if oracle_block_number_offset > 0:
                # Since we can't "mine" blocks in Python directly, this would be handled differently
                # in a real application. Here we just adjust the number.
                pass

            oracle_block_number += oracle_block_number_offset

        # Extract additional oracle parameters
        oracle_blocks = overrides.get("oracle_blocks")
        min_oracle_block_numbers = overrides.get("min_oracle_block_numbers")
        max_oracle_block_numbers = overrides.get("max_oracle_block_numbers")
        oracle_timestamps = overrides.get("oracle_timestamps")
        block_hashes = overrides.get("block_hashes")

        # Build the parameters for execute_with_oracle_params
        params = {
            "key": order_key,
            "oracleBlockNumber": oracle_block_number,
            "tokens": tokens,
            "precisions": precisions,
            "minPrices": min_prices,
            "maxPrices": max_prices,
            "simulate": overrides.get("simulate", False),
            "gasUsageLabel": gas_usage_label,
            "oracleBlocks": oracle_blocks,
            "minOracleBlockNumbers": min_oracle_block_numbers,
            "maxOracleBlockNumbers": max_oracle_block_numbers,
            "oracleTimestamps": oracle_timestamps,
            "blockHashes": block_hashes,
            "dataStreamTokens": data_stream_tokens,
            "dataStreamData": data_stream_data,
            "priceFeedTokens": price_feed_tokens,
        }

        # Create a fixture-like object with necessary properties
        fixture = {
            "config": self.config,
            "web3Provider": self._connection,
            "chain": self.config.chain,
            "accounts": {"signers": [self.config.get_signer()]},
            "props": {
                "oracleSalt": hash_data(["uint256", "string"], [self.config.chain_id, "xget-oracle-v1"]),
                "signerIndexes": [0, 1, 2, 3, 4, 5, 6],  # Default signer indexes
            },
        }

        print("************************")
        print(f"params: {params}")
        print("************************")
        print(f"fixture: {fixture}")
        print("************************")
        # Call execute_with_oracle_params with the built parameters
        return execute_with_oracle_params(fixture, params, self.config)

    def _submit_transaction(
        self,
        user_wallet_address: str,
        value_amount: float,
        multicall_args: list,
        gas_limits: dict,
        return_hash: bool = False,
    ):
        """
        Submit Transaction

        Parameters
        ----------
        user_wallet_address : str
            Address of the user's wallet (used for nonce calculation)
        value_amount : float
            Amount of native token to send with the transaction
        multicall_args : list
            List of encoded function calls for multicall
        gas_limits : dict
            Gas limits for the transaction
        return_hash : bool
            Whether to return the transaction hash

        Returns
        -------
        str or None
            Transaction hash if transaction is sent and return_hash is True,
            None in debug mode or if return_hash is False
        """
        self.log.info("Building transaction...")

        # Get the signer from config
        signer = self.config.get_signer()

        try:
            wallet_address = Web3.to_checksum_address(user_wallet_address)
        except AttributeError:
            wallet_address = Web3.toChecksumAddress(user_wallet_address)

        # Ensure the signer address matches the wallet address
        if signer.get_address().lower() != wallet_address.lower():
            self.log.warning(f"Signer address {signer.get_address()} doesn't match wallet address {wallet_address}")

        nonce = self._connection.eth.get_transaction_count(signer.get_address())

        raw_txn = self._exchange_router_contract_obj.functions.multicall(multicall_args).build_transaction(
            {
                "from": signer.get_address(),
                "value": value_amount,
                "chainId": self.config.chain_id,
                "gas": (self._gas_limits_order_type.call() + self._gas_limits_order_type.call()),
                "maxFeePerGas": int(self.max_fee_per_gas),
                "maxPriorityFeePerGas": 0,
                "nonce": nonce,
            }
        )

        if not self.debug_mode:
            # Use signer to send the transaction
            tx_hash = signer.send_transaction(raw_txn)

            self.log.info("Txn submitted!")
            self.log.info(f"Check status: https://arbiscan.io/tx/{tx_hash.hex()}")

            if return_hash:
                return tx_hash

        return None


def main(rpc="http://localhost:8545"):
    w3 = Web3(Web3.HTTPProvider(JSON_RPC_BASE))
    print(f"Connected to Arbitrum with chain ID: {w3.eth.chain_id}")

    # Addresses
    whale_address = "0xD7a827FBaf38c98E8336C5658E4BcbCD20a4fd2d"
    recipient_address = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
    link_token_address = "0xf97f4df75117a78c1A5a0DBb814Af92458539FB4"  # LINK token contract
    target_address = to_checksum_address("0x2bcC6D6CdBbDC0a4071e48bb3B969b06B3330c07")  # SOL

    erc20_abi = [
        {
            "constant": True,
            "inputs": [{"name": "_owner", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"name": "balance", "type": "uint256"}],
            "type": "function",
        },
        {
            "constant": False,
            "inputs": [
                {"name": "_to", "type": "address"},
                {"name": "_value", "type": "uint256"},
            ],
            "name": "transfer",
            "outputs": [{"name": "", "type": "bool"}],
            "type": "function",
        },
        {
            "constant": True,
            "inputs": [],
            "name": "decimals",
            "outputs": [{"name": "", "type": "uint8"}],
            "type": "function",
        },
    ]

    link_contract = w3.eth.contract(address=link_token_address, abi=erc20_abi)
    target_contract = w3.eth.contract(address=target_address, abi=erc20_abi)

    decimals = link_contract.functions.decimals().call()

    # Check initial balances
    balance = link_contract.functions.balanceOf(recipient_address).call()
    print(f"Recipient LINK balance: {balance / (10**decimals)}")

    sol_balance_before = target_contract.functions.balanceOf(recipient_address).call()
    print(f"Recipient SOL balance before: {sol_balance_before / 10**decimals}")

    # GMX config
    config = ConfigManager(chain="arbitrum")
    config.set_config()
    config.set_rpc(JSON_RPC_BASE)

    # Important: Set the user wallet address
    config.user_wallet_address = recipient_address

    parameters = {
        "chain": "arbitrum",
        "out_token_symbol": "SOL",
        "start_token_symbol": "LINK",
        "is_long": False,
        "size_delta_usd": 0,
        "initial_collateral_delta": 1000.000001,
        "slippage_percent": 0.02,
    }

    order_parameters = OrderArgumentParser(config, is_swap=True).process_parameters_dictionary(parameters)

    # Create our enhanced swap order
    order = EnhancedSwapOrder(
        config=config,
        market_key=order_parameters["swap_path"][-1],
        start_token=order_parameters["start_token_address"],
        out_token=order_parameters["out_token_address"],
        collateral_address=order_parameters["start_token_address"],
        index_token_address=order_parameters["out_token_address"],
        is_long=False,
        size_delta=0,
        initial_collateral_delta_amount=(order_parameters["initial_collateral_delta"]),
        slippage_percent=order_parameters["slippage_percent"],
        swap_path=order_parameters["swap_path"],
        debug_mode=False,
        execution_buffer=2.2,
        max_fee_per_gas=15,
    )

    # Create the order and get the key
    try:
        # order_key = order.create_order_and_get_key()

        data_store = get_datastore_contract(config)

        # print(f"Order LIST: {ORDER_LIST.hex()}")

        assert ORDER_LIST.hex() == "0x86f7cfd5d8f8404e5145c91bebb8484657420159dabd0753d6a59f3de3f7b8c1"[2:], (
            "Order list mismatch"
        )
        keys = data_store.functions.getBytes32ValuesAt(ORDER_LIST, 0, 20).call()
        # print(f"Key: {keys}")
        order_key = keys[-1]

        for key in keys:
            print(f"Key: {key.hex()}")

        # print(f"Order key: {order_key.hex()}")

        # Execute the order with oracle prices
        order.execute_order(order_key)

        # Check the balances after execution
        balance = link_contract.functions.balanceOf(recipient_address).call()
        print(f"Recipient LINK balance after swap: {balance / (10**decimals)}")

        balance = target_contract.functions.balanceOf(recipient_address).call()
        print(f"Recipient SOL balance after swap: {balance / 10**decimals}")

        print(f"Change in SOL balance: {(balance - sol_balance_before) / 10**decimals}")
    except Exception as e:
        print(f"Error during swap process: {e!s}")
        raise e

    return order


if __name__ == "__main__":
    main(JSON_RPC_BASE)
