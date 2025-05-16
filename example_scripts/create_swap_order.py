import sys
import os
from eth_typing import HexStr
from eth_utils import to_checksum_address
from web3 import Web3

from gmx_python_sdk.scripts.v2.gmx_utils import ConfigManager, get_datastore_contract
from gmx_python_sdk.scripts.v2.order.create_swap_order import SwapOrder
from gmx_python_sdk.scripts.v2.order.order_argument_parser import OrderArgumentParser
from gmx_python_sdk.scripts.v2.utils.keys import ORDER_LIST


def _set_paths():
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to the target directory relative to the current script
    target_dir = os.path.join(current_dir, "../")
    # Add the target directory to sys.path
    sys.path.append(target_dir)


_set_paths()


JSON_RPC_BASE = "https://virtual.arbitrum.rpc.tenderly.co/be06beda-af74-4457-8752-d10012ab2bb6"  # "https://virtual.arbitrum.rpc.tenderly.co/338aa0f8-ef60-4ae1-baf9-958c3754686d" # os.getenv("ARBITRUM_CHAIN_JSON_RPC")


def main(rpc="http://localhost:8545"):
    w3 = Web3(Web3.HTTPProvider(JSON_RPC_BASE))
    # 420000042000000028161458831360
    print(w3.eth.chain_id)

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
    # amount = 4000 * (10**decimals)  # Transfer 3000 LINK tokens

    # tx = link_contract.functions.transfer(recipient_address, amount).build_transaction(
    #     {
    #         "from": whale_address,
    #         "nonce": w3.eth.get_transaction_count(whale_address),
    #         "gas": 100000,
    #         "gasPrice": w3.to_wei("1", "gwei"),
    #     }
    # )

    # tx_hash = w3.eth.send_transaction(tx)

    # # Wait for transaction receipt
    # receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    # print(f"Transaction successful with hash: {tx_hash.hex()}")

    balance = link_contract.functions.balanceOf(recipient_address).call()
    print(f"Recipient LINK balance: {balance / (10**decimals)}")

    sol_balance_before = target_contract.functions.balanceOf(recipient_address).call()
    print(f"Recipient SOL balance before: {sol_balance_before / 10**decimals}")

    config = ConfigManager(chain="arbitrum")
    config.set_config()
    config.set_rpc(JSON_RPC_BASE)

    parameters = {
        "chain": "arbitrum",
        # token to use as collateral. Start token swaps into collateral token if
        # different
        "out_token_symbol": "SOL",
        # the token to start with - WETH not supported yet
        "start_token_symbol": "LINK",
        # True for long, False for short
        "is_long": False,
        # Position size in in USD
        "size_delta_usd": 0,
        # if leverage is passed, will calculate number of tokens in
        # start_token_symbol amount
        "initial_collateral_delta": 100.000001,
        # as a percentage
        "slippage_percent": 0.02,
    }

    order_parameters = OrderArgumentParser(config, is_swap=True).process_parameters_dictionary(parameters)

    order = SwapOrder(
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
        max_fee_per_gas=10976000 * 15,
    )

    # swap_estimate = order.estimated_swap_output(
    #     market,
    #     "0x7f1fa204bb700853D36994DA19F830b6Ad18455C",
    #     parameters["initial_collateral_delta"],
    # )
    # print(f"Estimated swap output: {swap_estimate}")

    data_store = get_datastore_contract(config)

    print(f"Order LIST: {ORDER_LIST.hex()}")

    assert ORDER_LIST.hex() == "0x86f7cfd5d8f8404e5145c91bebb8484657420159dabd0753d6a59f3de3f7b8c1"[2:], (
        "Order list mismatch"
    )
    keys = data_store.functions.getBytes32ValuesAt(ORDER_LIST, 0, 20).call()
    # print(f"Key: {keys}")

    for key in keys:
        print(f"Key: {key.hex()}")

    balance = link_contract.functions.balanceOf(recipient_address).call()
    print(f"Recipient LINK balance after swap: {balance / (10**decimals)}")

    balance = target_contract.functions.balanceOf(recipient_address).call()
    print(f"Recipient SOL balance: {balance / 10**decimals}")

    print(f"Change is SOL balance: {(balance - sol_balance_before) / 10**decimals}")

    return order


if __name__ == "__main__":
    main(JSON_RPC_BASE)
