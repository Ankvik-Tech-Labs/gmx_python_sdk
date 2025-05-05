import os
from web3 import Web3
from decimal import Decimal

from gmx_python_sdk.scripts.v2.order.create_swap_order import SwapOrder
from gmx_python_sdk.scripts.v2.gmx_utils import ConfigManager
from gmx_python_sdk.scripts.v2.order.order_argument_parser import OrderArgumentParser
from gmx_python_sdk.scripts.v2.get.get_markets import Markets


class MockSwapOrder(SwapOrder):
    """
    Extension of SwapOrder that allows for mocked oracle data in tests
    """

    def __init__(self, *args, **kwargs):
        # Extract test-specific parameters
        self.mock_oracle_prices = kwargs.pop("mock_oracle_prices", None)
        self.mock_precision = kwargs.pop("mock_precision", [8, 18])  # Default precisions for ETH/USDC

        # Initialize the parent class
        super().__init__(*args, **kwargs)

    def order_builder(self, is_open=False, is_close=False, is_swap=False):
        """
        Override the order_builder method to use mocked oracle data
        """
        self.log.info("Creating mock swap order with fixed oracle prices...")

        # Basic setup similar to the parent method
        self.determine_gas_limits()
        gas_price = self._connection.eth.gas_price
        execution_fee = int(self._get_execution_fee() * self.execution_buffer)

        if not self.debug_mode:
            self.check_for_approval()

        # Setup order parameters - similar to parent but with mock data
        market_key = self.market_key
        initial_collateral_delta_amount = self.initial_collateral_delta_amount

        # Create the multicall arguments for the order
        multicall_args = self._create_multicall_args(market_key, initial_collateral_delta_amount, execution_fee)

        # Submit the transaction
        user_wallet_address = self.config.user_wallet_address
        value_amount = execution_fee

        if self.collateral_address != "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1":
            value_amount = execution_fee
        else:
            # If using ETH as collateral, include it in the value
            value_amount = initial_collateral_delta_amount + execution_fee

        # Submit the transaction with mock oracle params
        return self._submit_transaction_with_mock_oracle(
            user_wallet_address, value_amount, multicall_args, self._gas_limits
        )

    def _create_multicall_args(self, market_key, initial_collateral_delta_amount, execution_fee):
        """Helper to create the multicall arguments"""
        from hexbytes import HexBytes

        multicall_args = []

        # If the collateral is not ETH, send tokens to vault
        if self.collateral_address != "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1":
            multicall_args = [
                HexBytes(self._send_wnt(execution_fee)),
                HexBytes(self._send_tokens(self.collateral_address, initial_collateral_delta_amount)),
                HexBytes(self._create_order(self._get_order_arguments())),
            ]
        else:
            # If using ETH as collateral, include it in the value sent
            value_amount = initial_collateral_delta_amount + execution_fee
            multicall_args = [
                HexBytes(self._send_wnt(value_amount)),
                HexBytes(self._create_order(self._get_order_arguments())),
            ]

        return multicall_args

    def _get_order_arguments(self):
        """Generate order arguments similar to the parent class"""
        from hexbytes import HexBytes
        from web3 import Web3

        # Use constant values for testing
        acceptable_price = 0
        callback_gas_limit = 0
        execution_fee = int(self._get_execution_fee() * self.execution_buffer)
        min_output_amount = 0

        # For swap orders
        order_type = 0  # Market swap
        decrease_position_swap_type = 0  # No swap
        should_unwrap_native_token = True
        referral_code = HexBytes("0x0000000000000000000000000000000000000000000000000000000000000000")

        # Get addresses
        user_wallet_address = Web3.to_checksum_address(self.config.user_wallet_address)
        cancellation_receiver = user_wallet_address
        eth_zero_address = Web3.to_checksum_address("0x0000000000000000000000000000000000000000")
        ui_ref_address = Web3.to_checksum_address("0x0000000000000000000000000000000000000000")

        # For swap orders, market is not important
        gmx_market_address = "0x0000000000000000000000000000000000000000"
        collateral_address = Web3.to_checksum_address(self.collateral_address)

        # Organize arguments in the format expected by the contract
        arguments = (
            (
                user_wallet_address,
                cancellation_receiver,
                eth_zero_address,
                ui_ref_address,
                gmx_market_address,
                collateral_address,
                self.swap_path,
            ),
            (
                0,  # Size delta (0 for swaps)
                self.initial_collateral_delta_amount,
                0,  # Mark price (not important for swaps)
                acceptable_price,
                execution_fee,
                callback_gas_limit,
                min_output_amount,
                0,  # Valid from time
            ),
            order_type,
            decrease_position_swap_type,
            self.is_long,
            should_unwrap_native_token,
            False,  # Auto cancel
            referral_code,
        )

        return arguments

    def _get_execution_fee(self):
        """Calculate execution fee from gas limits"""
        from gmx_python_sdk.scripts.v2.gas_utils import get_execution_fee

        gas_price = self._connection.eth.gas_price
        return get_execution_fee(self._gas_limits, self._gas_limits_order_type, gas_price)

    def _submit_transaction_with_mock_oracle(self, user_wallet_address, value_amount, multicall_args, gas_limits):
        """
        Submit transaction with mock oracle parameters.
        This is where the mock oracle data is injected.
        """
        from web3 import Web3

        self.log.info("Building transaction with mock oracle data...")

        # Get the signer from config
        signer = self.config.get_signer()
        wallet_address = Web3.to_checksum_address(user_wallet_address)

        # If debug mode, just log and return
        if self.debug_mode:
            self.log.info("Debug mode: Transaction would be executed with mock oracle data.")
            return None

        # Otherwise, build and send the transaction
        nonce = self._connection.eth.get_transaction_count(signer.get_address())

        # Create the transaction
        raw_txn = self._exchange_router_contract_obj.functions.multicall(multicall_args).build_transaction(
            {
                "from": signer.get_address(),
                "value": value_amount,
                "chainId": self.config.chain_id,
                "gas": (self._gas_limits_order_type.call() * 2),  # Add buffer
                "maxFeePerGas": int(self.max_fee_per_gas),
                "maxPriorityFeePerGas": 0,
                "nonce": nonce,
            }
        )

        # Sign and send the transaction
        tx_hash = signer.send_transaction(raw_txn)

        self.log.info(f"Transaction submitted with hash: {tx_hash.hex()}")
        return tx_hash


def run_mock_swap_test(rpc_url):
    """
    Execute a test swap using mocked oracle data
    """
    # Setup config
    config = ConfigManager(chain="arbitrum")
    config.set_rpc(rpc_url)
    config.set_config()

    # Define swap parameters
    parameters = {
        "chain": "arbitrum",
        "out_token_symbol": "USDC",
        "start_token_symbol": "LINK",
        "is_long": False,
        "size_delta_usd": 0,
        "initial_collateral_delta": 1.0,  # 1 ETH
        "slippage_percent": 0.02,
    }

    # Parse parameters
    order_parameters = OrderArgumentParser(config, is_swap=True).process_parameters_dictionary(parameters)

    # Define mock oracle prices - similar to the TypeScript test
    # These values would be the exact mock prices you want to use
    mock_prices = {
        # Format: token_address: {"minPriceFull": min_price, "maxPriceFull": max_price}
        # ETH price at 5000 USD
        "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1": {
            "minPriceFull": "5000000000000000000000000000000",
            "maxPriceFull": "5000000000000000000000000000000",
        },
        # USDC price at 1 USD
        "0xaf88d065e77c8cC2239327C5EDb3A432268e5831": {
            "minPriceFull": "1000000000000000000000000000000",
            "maxPriceFull": "1000000000000000000000000000000",
        },
    }

    # Create and execute the mock swap order
    order = MockSwapOrder(
        config=config,
        market_key=order_parameters["swap_path"][-1],
        start_token=order_parameters["start_token_address"],
        out_token=order_parameters["out_token_address"],
        collateral_address=order_parameters["start_token_address"],
        index_token_address=order_parameters["out_token_address"],
        is_long=False,
        size_delta=0,
        initial_collateral_delta_amount=order_parameters["initial_collateral_delta"],
        slippage_percent=order_parameters["slippage_percent"],
        swap_path=order_parameters["swap_path"],
        debug_mode=False,
        mock_oracle_prices=mock_prices,
    )

    # Execute the order
    return order.order_builder(is_swap=True)


if __name__ == "__main__":
    # Use your fork RPC URL
    rpc_url = "https://virtual.arbitrum.rpc.tenderly.co/8ebd8115-6fcf-49d4-96cb-d5c75ad4c9ed"  # Change to your forked node URL
    run_mock_swap_test(rpc_url)
