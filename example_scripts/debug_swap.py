import os
import time
from web3 import Web3
from eth_defi.provider.anvil import fork_network_anvil
from eth_defi.provider.multi_provider import create_multi_provider_web3
from eth_defi.trace import trace_evm_transaction
from rich.console import Console
from web3.exceptions import TransactionNotFound

console = Console()

JSON_RPC_BASE = os.getenv("ARBITRUM_CHAIN_JSON_RPC")


def main():
    """
    Main debugging function for GMX swaps
    """
    # Fork the network with keepers unlocked
    keeper_address = "0x83bb6232D281905A6c6D2108e1cB3596328e1E84"
    anvil = fork_network_anvil(
        JSON_RPC_BASE,
        unlocked_addresses=[
            "0xD7a827FBaf38c98E8336C5658E4BcbCD20a4fd2d",  # Whale address
            keeper_address,  # GMX keeper for mock execution
        ],
        test_request_timeout=50,
    )

    rpc = anvil.json_rpc_url
    web3 = create_multi_provider_web3(rpc + " " + JSON_RPC_BASE)

    # Import SwapOrder and other dependencies here to avoid circular imports
    from create_swap_order import main as create_swap
    from gmx_python_sdk.scripts.v2.gmx_utils import ConfigManager

    # Print initial balances
    print_token_balances(web3, "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266")

    # 1. Create the swap order
    print("\n--- Step 1: Creating Swap Order ---")
    order = create_swap(rpc)
    tx_hash = order.tx_info
    anvil.mine()

    # Get the transaction receipt
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

    # 2. Trace the order creation transaction
    print("\n--- Step 2: Analyzing Order Creation Transaction ---")
    order_trace = trace_evm_transaction(web3, tx_hash)
    print("Order Creation Transaction Trace (summary):")
    print_trace_summary(order_trace)  # Helper to print a compact version

    # 3. Check balances after order creation
    print("\n--- Step 3: Checking Balances After Order Creation ---")
    print_token_balances(web3, "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266")

    # 4. Check order status
    print("\n--- Step 4: Checking Order Status ---")
    config = ConfigManager(chain="arbitrum", rpc=rpc)
    order_status = check_order_status(web3, receipt, config)

    # 5. Execute the order with a mock keeper
    print("\n--- Step 5: Executing Order With Mock Keeper ---")
    execution_tx = simulate_gmx_keeper(web3, receipt, config, keeper_address)

    if execution_tx:
        # Get execution receipt
        execution_receipt = web3.eth.wait_for_transaction_receipt(execution_tx)

        # 6. Trace the execution transaction
        print("\n--- Step 6: Analyzing Order Execution Transaction ---")
        execution_trace = trace_evm_transaction(web3, execution_tx)
        print("Order Execution Transaction Trace (summary):")
        print_trace_summary(execution_trace)

        # 7. Check final balances
        print("\n--- Step 7: Checking Final Balances After Execution ---")
        print_token_balances(web3, "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266")
    else:
        print("Order execution failed or was skipped.")

    print("\n--- Debugging Complete ---")
    print("Now you should be able to see if and why the target token balance changes")


def print_token_balances(web3, address):
    """Print balances of relevant tokens for debugging"""
    erc20_abi = [
        {
            "constant": True,
            "inputs": [{"name": "_owner", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"name": "balance", "type": "uint256"}],
            "type": "function",
        },
        {
            "constant": True,
            "inputs": [],
            "name": "decimals",
            "outputs": [{"name": "", "type": "uint8"}],
            "type": "function",
        },
        {
            "constant": True,
            "inputs": [],
            "name": "symbol",
            "outputs": [{"name": "", "type": "string"}],
            "type": "function",
        },
    ]

    # Token addresses to check
    tokens = {
        "LINK": "0xf97f4df75117a78c1A5a0DBb814Af92458539FB4",
        "USDC": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
        "ETH": "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",
    }

    print(f"Balances for address: {address}")

    for symbol, token_address in tokens.items():
        try:
            token = web3.eth.contract(address=token_address, abi=erc20_abi)
            decimals = token.functions.decimals().call()
            balance = token.functions.balanceOf(address).call()
            print(f"  {symbol}: {balance / (10**decimals)}")
        except Exception as e:
            print(f"  Error getting {symbol} balance: {e}")

    # Also check OrderVault balance
    order_vault = "0x31eF83a530Fde1B38EE9A18093A333D8Bbbc40D5"
    print(f"\nOrderVault ({order_vault}) balances:")
    for symbol, token_address in tokens.items():
        try:
            token = web3.eth.contract(address=token_address, abi=erc20_abi)
            decimals = token.functions.decimals().call()
            balance = token.functions.balanceOf(order_vault).call()
            print(f"  {symbol}: {balance / (10**decimals)}")
        except Exception as e:
            print(f"  Error getting OrderVault {symbol} balance: {e}")


def print_trace_summary(trace):
    """Print a compact summary of the trace"""
    # This is a simplified version - you could make it more detailed
    calls = []

    def extract_calls(item, depth=0):
        call_type = list(item.keys())[0] if isinstance(item, dict) else None
        if call_type in ["CALL", "DELEGATECALL", "STATICCALL"]:
            target = item[call_type]["to"]
            value = item[call_type].get("value", "0x0")
            gas = item[call_type]["gas"]
            calls.append((depth, call_type, target, value, gas))

            if "calls" in item[call_type]:
                for subcall in item[call_type]["calls"]:
                    extract_calls(subcall, depth + 1)

    extract_calls({"CALL": trace})

    for depth, call_type, target, value, gas in calls:
        indent = "  " * depth
        print(f"{indent}{call_type}: {target} [gas: {int(gas, 16)}]")


def check_order_status(web3, tx_receipt, config):
    """
    Check the status of a GMX order after it's been created
    """
    from gmx_python_sdk.scripts.v2.gmx_utils import get_reader_contract, contract_map
    import json
    import os

    # Get the reader contract
    reader = get_reader_contract(config)

    # Get DataStore address
    datastore_address = contract_map[config.chain]["datastore"]["contract_address"]

    # First, extract the order key from events
    # We need the EventEmitter ABI to decode events
    event_emitter_address = contract_map[config.chain]["eventemitter"]["contract_address"]
    event_emitter_abi_path = contract_map[config.chain]["eventemitter"]["abi_path"]

    # Load EventEmitter ABI
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    with open(os.path.join(base_dir, "gmx_python_sdk", event_emitter_abi_path)) as f:
        event_emitter_abi = json.load(f)

    # Create contract object
    event_emitter = web3.eth.contract(address=event_emitter_address, abi=event_emitter_abi)

    # Look for OrderCreated event
    order_key = None
    for log in tx_receipt.logs:
        if log["address"].lower() == event_emitter_address.lower():
            for event in event_emitter.events:
                if event.__class__.__name__ == "OrderCreated":
                    try:
                        # Try to decode as OrderCreated event
                        decoded_log = event_emitter.events.OrderCreated().process_log(log)
                        order_key = decoded_log["args"]["key"]
                        print(f"Found order key: {order_key.hex()}")
                        break
                    except:
                        # Not an OrderCreated event, continue
                        continue

    if not order_key:
        print("Could not find OrderCreated event in transaction logs")
        return None

    # Now check the order status using the Reader contract
    try:
        order_info = reader.functions.getOrder(datastore_address, order_key).call()

        # order_info structure: [addresses, numbers, flags, data]
        print("\nOrder information:")
        print(f"Order addresses: {order_info[0]}")  # 0-account, 1-receiver, 2-callbackContract, etc.
        print(f"Order numbers: {order_info[1]}")  # Various numerical parameters
        print(f"Order flags: {order_info[2]}")  # Boolean flags

        # Interpret order state
        is_executed = False
        is_cancelled = False

        # Check if there's a flag indicating execution or cancellation
        # The exact structure depends on GMX implementation
        if len(order_info[2]) >= 3:  # Assuming flags include execution status
            is_executed = order_info[2][1]  # This index might need adjustment
            is_cancelled = order_info[2][2]  # This index might need adjustment

        print(f"Order executed: {is_executed}")
        print(f"Order cancelled: {is_cancelled}")

        if not is_executed and not is_cancelled:
            print("\nThe order is still pending execution by a keeper.")
            print("The funds are held in the OrderVault until execution.")
            print("You won't see the target token balance change until the order is executed.")

        return order_info, order_key

    except Exception as e:
        print(f"Error checking order status: {e}")
        return None, order_key


def simulate_gmx_keeper(web3, tx_receipt, config, keeper_address):
    """
    Simulate a GMX keeper that executes pending orders
    This is for testing/debugging purposes on local forks

    Args:
            web3: Web3 instance
            tx_receipt: Transaction receipt from order creation
            config: GMX ConfigManager instance
            keeper_address: Address of the keeper to use

    Returns:
            execution_tx_hash: The hash of the execution transaction
    """
    from gmx_python_sdk.scripts.v2.gmx_utils import contract_map
    from web3.exceptions import ContractLogicError
    import json
    import os

    print("Simulating GMX keeper to execute the order...")

    # Get order status and key
    order_info, order_key = check_order_status(web3, tx_receipt, config)

    if not order_key:
        print("Cannot execute: no order key found")
        return None

    if not order_info:
        print("Cannot execute: failed to get order info")
        return None

    # Check if order is already executed or cancelled
    if len(order_info[2]) >= 3 and (order_info[2][1] or order_info[2][2]):
        print("Order is already executed or cancelled, skipping execution")
        return None

    # Load SyntheticsRouter ABI
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    router_abi_path = contract_map[config.chain]["syntheticsrouter"]["abi_path"]
    router_address = contract_map[config.chain]["syntheticsrouter"]["contract_address"]

    try:
        with open(os.path.join(base_dir, "gmx_python_sdk", router_abi_path)) as f:
            router_abi = json.load(f)
    except FileNotFoundError:
        # Fallback path for when running directly
        with open(f"gmx_python_sdk/{router_abi_path}") as f:
            router_abi = json.load(f)

    # Create router contract
    router = web3.eth.contract(address=router_address, abi=router_abi)

    print(f"Using keeper address: {keeper_address}")
    print(f"Attempting to execute order with key: {order_key.hex()}")

    # Prepare execution parameters
    # Note: Real keepers have sophisticated systems to determine these values
    block_number = web3.eth.block_number
    min_oracle_block_numbers = [block_number]
    max_oracle_block_numbers = [block_number + 100]
    execution_deadline = web3.eth.get_block("latest")["timestamp"] + 300  # 5 minutes

    try:
        # Get gas estimate first to detect potential issues
        gas_estimate = router.functions.executeOrder(
            contract_map[config.chain]["datastore"]["contract_address"],
            order_key,
            min_oracle_block_numbers,
            max_oracle_block_numbers,
            execution_deadline,
        ).estimate_gas(
            {
                "from": keeper_address,
                "gas": 5000000,  # High initial estimate
            }
        )

        print(f"Gas estimate for execution: {gas_estimate}")

        # Build the transaction
        tx = router.functions.executeOrder(
            contract_map[config.chain]["datastore"]["contract_address"],
            order_key,
            min_oracle_block_numbers,
            max_oracle_block_numbers,
            execution_deadline,
        ).build_transaction(
            {
                "from": keeper_address,
                "gas": int(gas_estimate * 1.2),  # Add 20% buffer
                "gasPrice": web3.eth.gas_price,
                "nonce": web3.eth.get_transaction_count(keeper_address),
            }
        )

        # Send the transaction
        tx_hash = web3.eth.send_transaction(tx)
        print(f"Order execution transaction sent: {tx_hash.hex()}")

        # Wait for the transaction to be mined
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status == 1:
            print(f"Order successfully executed!")
            return tx_hash
        else:
            print(f"Order execution failed! Transaction status: {receipt.status}")
            return None

    except ContractLogicError as e:
        print(f"Contract error during execution: {e}")
        # Try to decode the error for more information
        try:
            error_string = str(e)
            revert_reason = error_string[error_string.find("revert: ") + 8 :]
            print(f"Revert reason: {revert_reason}")
        except:
            pass
        return None
    except Exception as e:
        print(f"Error executing order: {e}")
        return None


def analyze_gmx_execution_flow():
    """
    Educational function to explain how GMX execution flows work
    """
    print("\n--- GMX V2 Order Execution Flow ---")
    print("GMX V2 uses a two-transaction model for executing trades:")
    print("\n1. Order Creation (Your Transaction):")
    print("   - Call to ExchangeRouter.createOrder(...)")
    print("   - Funds are transferred to OrderVault contract")
    print("   - Order information is stored in DataStore contract")
    print("   - OrderCreated event is emitted")
    print("   - This transaction completes WITHOUT executing the swap")

    print("\n2. Order Execution (Keeper Transaction):")
    print("   - After your transaction, the order is in 'pending' state")
    print("   - Keepers (specialized bots) monitor for pending orders")
    print("   - A keeper calls SyntheticsRouter.executeOrder(...)")
    print("   - Order is validated and executed")
    print("   - Target tokens are sent to the receiver address")
    print("   - OrderExecuted event is emitted")

    print("\nThis is why you don't see target tokens after the first transaction.")
    print("The target tokens only appear after the second transaction by the keeper.")

    print("\nOn local forks, you need to simulate both transactions to see the complete flow.")
    print("In production, keepers will automatically execute valid orders, usually within seconds.")


if __name__ == "__main__":
    main()

    # Additional educational information
    analyze_gmx_execution_flow()
