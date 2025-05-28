import logging
from typing import Any

from eth_utils import to_checksum_address

from gmx_python_sdk.scripts.v2.get.get_oracle_prices import OraclePrices
from gmx_python_sdk.scripts.v2.gmx_utils import get_contract_object
from gmx_python_sdk.scripts.v2.utils.oracle import (
    get_oracle_params_for_custom_oracle,
    get_oracle_params_for_simulation,
    TOKEN_ORACLE_TYPES,
)


def get_execute_params(fixture, params: dict[str, Any]) -> dict[str, list]:
    """
    Get execution parameters for oracle-based transactions

    Args:
        fixture: Object containing contract references
        params: dictionary with tokens and prices

    Returns:
        dictionary with execution parameters
    """
    # Extract tokens and prices from the parameters
    tokens = params.get("tokens", [])
    prices = params.get("prices", [])

    # Get contract references from fixture
    contracts = fixture.get("contracts")
    wnt = contracts.get("wnt")
    wbtc = contracts.get("wbtc")
    usdc = contracts.get("usdc")
    usdt = contracts.get("usdt")

    # Default price info for common tokens
    ref_prices = fixture.get("prices")
    default_price_info_items = {
        wnt.address: ref_prices.get("wnt"),
        wbtc.address: ref_prices.get("wbtc"),
        usdc.address: ref_prices.get("usdc"),
        usdt.address: ref_prices.get("usdt"),
    }

    # Prepare return parameters
    result_params = {
        "tokens": [],
        "precisions": [],
        "minPrices": [],
        "maxPrices": [],
    }

    # Process tokens if provided
    if tokens:
        for token in tokens:
            price_info_item = default_price_info_items.get(token.address)
            if not price_info_item:
                msg = f"Missing price info for token {token.address}"
                raise ValueError(msg)

            result_params["tokens"].append(token.address)
            result_params["precisions"].append(price_info_item["precision"])
            result_params["minPrices"].append(price_info_item["min"])
            result_params["maxPrices"].append(price_info_item["max"])

    # Process prices if provided
    if prices:
        for price_info_item in prices:
            token = contracts.get(price_info_item["contractName"])

            result_params["tokens"].append(token.address)
            result_params["precisions"].append(price_info_item["precision"])
            result_params["minPrices"].append(price_info_item["min"])
            result_params["maxPrices"].append(price_info_item["max"])

    return result_params


# Handle block hash conversion to bytes properly for all formats
def get_block_hashes(block, tokens):
    if block.hash is None:
        # Handle the case when block hash is None
        return [b"\x00" * 32] * len(tokens)  # Use null bytes as placeholder

    # If block hash is already bytes, use it directly
    if isinstance(block.hash, bytes):
        block_hash_bytes = block.hash
    # If it's HexBytes, convert to regular bytes
    elif hasattr(block.hash, "hex") and callable(block.hash.hex):
        block_hash_bytes = block.hash
    # Handle hex string with '0x' prefix
    elif isinstance(block.hash, str):
        # Remove '0x' prefix if present
        clean_hash = block.hash[2:] if block.hash.startswith("0x") else block.hash
        try:
            # Convert hex string to bytes
            block_hash_bytes = bytes.fromhex(clean_hash)
        except ValueError as e:
            # Log the problematic hash for debugging
            print(f"Error converting block hash: {block.hash}, type: {type(block.hash)}")
            # Fallback to a safe default or raise custom error with more details
            msg = f"Invalid block hash format: {block.hash}"
            raise ValueError(msg) from e
    else:
        # Unknown format - raise a clear error
        msg = f"Unsupported block hash type: {type(block.hash)}"
        raise TypeError(msg)

    # Create a list of the same block hash for each token
    return [block_hash_bytes] * len(tokens)


def execute_with_oracle_params(fixture, overrides: dict, config, deployed_oracle_address, is_swap: bool = True) -> Any:
    """
    Execute a transaction with oracle parameters

    Args:
        fixture: Object containing account and contract references
        overrides: Parameters for execution including oracle info
        deployed_oracle_address: Address of the deployed oracle contract
        is_swap: Boolean indicating if this is a swap transaction. Defaults to True.

    Returns:
        Transaction receipt or simulation result
    """
    # Extract parameters from overrides
    key = overrides.get("key")
    oracle_blocks = overrides.get("oracleBlocks")
    oracle_block_number = overrides.get("oracleBlockNumber")
    tokens = overrides.get("tokens", [])
    precisions = overrides.get("precisions", [])
    min_prices = overrides.get("minPrices", [])
    max_prices = overrides.get("maxPrices", [])

    # execute = overrides.get("execute")
    simulate = overrides.get("simulate", False)
    gas_usage_label = overrides.get("gasUsageLabel")
    data_stream_tokens = overrides.get("dataStreamTokens", [])
    data_stream_data = overrides.get("dataStreamData", [])
    price_feed_tokens = overrides.get("priceFeedTokens", [])

    # Get Web3 provider and account references - safely handle nested dictionaries
    web3_provider = fixture.get("web3_provider") or fixture.get("web3Provider")
    chain = fixture.get("chain")

    # Safely handle nested dictionaries
    accounts = fixture.get("accounts", {})
    props = fixture.get("props", {})

    # Get signer - handle both single signer and list of signers
    signer = accounts.get("signers")
    signers = [signer] if signer and not isinstance(signer, list) else signer or []

    oracle_salt = props.get("oracleSalt")
    signer_indexes = props.get("signerIndexes", [])

    # Validate inputs
    if len(tokens) > len(precisions) or len(tokens) > len(min_prices) or len(tokens) > len(max_prices):
        msg = "`tokens` should not be bigger than `precisions`, `minPrices` or `maxPrices`"
        raise ValueError(msg)

    if not oracle_block_number:
        msg = "`oracleBlockNumber` is required"
        raise ValueError(msg)

    if not web3_provider:
        msg = "web3_provider is required in the fixture"
        raise ValueError(msg)

    # Get blockchain block information
    block = web3_provider.eth.get_block(int(oracle_block_number))
    # print(f"Block number: {block.number}")

    # Default to standard oracle types if not provided
    token_oracle_types = overrides.get("tokenOracleTypes", [TOKEN_ORACLE_TYPES["DEFAULT"]] * len(tokens))

    # Initialize oracle block information
    # FIX: Create empty lists first, then populate them
    min_oracle_block_numbers = []
    max_oracle_block_numbers = []
    oracle_timestamps = []
    block_hashes = []

    # Process oracle blocks if provided, otherwise use default values
    if oracle_blocks:
        for oracle_block in oracle_blocks:
            min_oracle_block_numbers.append(oracle_block["number"])
            max_oracle_block_numbers.append(oracle_block["number"])
            oracle_timestamps.append(oracle_block["timestamp"])
            block_hashes.append(oracle_block["hash"])
    else:
        # FIX: Directly set the values instead of using get() with defaults
        # This ensures the lists are properly populated
        min_oracle_block_numbers = overrides.get("minOracleBlockNumbers")
        if not min_oracle_block_numbers:
            min_oracle_block_numbers = [block.number] * len(tokens)

        max_oracle_block_numbers = overrides.get("maxOracleBlockNumbers")
        if not max_oracle_block_numbers:
            max_oracle_block_numbers = [block.number] * len(tokens)

        oracle_timestamps_from_overrides = overrides.get("oracleTimestamps")
        if not oracle_timestamps_from_overrides:
            oracle_timestamps = [block.timestamp] * len(tokens)
        else:
            oracle_timestamps = oracle_timestamps_from_overrides

        # Handle block hash depending on its format
        # block_hash = block.hash.hex() if isinstance(block.hash, bytes) else block.hash
        block_hashes = get_block_hashes(block, tokens)

    # Prepare arguments for oracle parameters - no conditional checks needed now
    args = {
        # skip the 0x prefix
        "oracle_salt": oracle_salt,
        "min_oracle_block_numbers": min_oracle_block_numbers,
        "max_oracle_block_numbers": max_oracle_block_numbers,
        "oracle_timestamps": oracle_timestamps,
        "block_hashes": block_hashes,
        "signer_indexes": signer_indexes,
        "tokens": tokens,
        "token_oracle_types": token_oracle_types,
        "precisions": precisions,
        "min_prices": min_prices,
        "max_prices": max_prices,
        "signers": signers,
        "data_stream_tokens": data_stream_tokens,
        "data_stream_data": data_stream_data,
        "price_feed_tokens": price_feed_tokens,
    }

    config = fixture.get("config")
    if not config:
        msg = "config is required in the fixture"
        raise ValueError(msg)

    order_handler = get_contract_object(web3_provider, "orderhandler", chain)

    # Get oracle parameters for simulation or execution
    if simulate:
        oracle_params = get_oracle_params_for_simulation(
            tokens=tokens,
            min_prices=min_prices,
            max_prices=max_prices,
            precisions=precisions,
            oracle_timestamps=oracle_timestamps,
            web3_provider=web3_provider,
        )
        try:
            return order_handler.functions.simulateExecuteOrder(key, oracle_params).call()
        except Exception as ex:
            if "EndOfOracleSimulation" not in str(ex):
                raise ex
            logging.info("Oracle simulation completed")
    else:
        keeper_address = "0xE47b36382DC50b90bCF6176Ddb159C4b9333A7AB"
        controller_address = "0xb6d37DFCdA9c237ca98215f9154Dc414EFe0aC1b"
        # Get full oracle parameters for execution
        # print(f"Args for oracle params: {args}")
        oracle_params = get_oracle_params_for_custom_oracle(
            config=config,
            keeper_address=keeper_address,
            controller_address=controller_address,
            deployed_oracle_address=deployed_oracle_address,
            **args,
        )

        logging.info(f"Key: {key}")
        logging.info(f"Oracle Params: {oracle_params}")

        # Get the first signer if available
        if not signers:
            msg = "At least one signer is required for transaction execution"
            raise ValueError(msg)

        active_signer = signers[0]
        nonce = web3_provider.eth.get_transaction_count(keeper_address)

        controller = "0xf5F30B10141E1F63FC11eD772931A8294a591996"
        oracle_contract = get_contract_object(config.get_web3_connection(), "oracle", config.chain)
        # * clear the price first
        oracle_contract.functions.clearAllPrices().transact({"from": controller})
        # ETH PRICE. WETH address: 0x82aF49447D8a07e3bd95BD0d56f35241523fBab1
        # oracle_contract.functions.setPrimaryPrice(
        #     "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1", (2505849875000000, 2505989682807298)
        # ).transact({"from": controller})

        # LINK price
        # # NOTE: address, (min_price, max_price)
        # oracle_contract.functions.setPrimaryPrice(
        #     "0xf97f4df75117a78c1A5a0DBb814Af92458539FB4", (16364090000000, 16373342000000)
        # ).transact({"from": controller})

        # USDC Price
        # oracle_contract.functions.setPrimaryPrice(
        #     "0xaf88d065e77c8cC2239327C5EDb3A432268e5831", (999923135340409600000000, 1000053137654175000000000)
        # ).transact({"from": controller})

        # ? for increase & decrease orders, we need to set the prices.
        # Keep it hardcoded for now. Only supports postions in ARB/USDC market with USDC as collateral.
        if not is_swap:
            oracle_prices = OraclePrices(chain="arbitrum").get_recent_prices()

            max_price = int(
                oracle_prices[to_checksum_address("0xf97f4df75117a78c1a5a0dbb814af92458539fb4")]["maxPriceFull"]
            )
            min_price = int(
                oracle_prices[to_checksum_address("0xf97f4df75117a78c1a5a0dbb814af92458539fb4")]["minPriceFull"]
            )
            oracle_contract = get_contract_object(config.get_web3_connection(), "oracle", config.chain)
            # LINK price
            oracle_contract.functions.setPrimaryPrice(
                to_checksum_address("0xf97f4df75117a78c1a5a0dbb814af92458539fb4"), (min_price, max_price)
            ).transact({"from": controller})

            # USDC price
            max_price = int(
                oracle_prices[to_checksum_address("0xaf88d065e77c8cC2239327C5EDb3A432268e5831")]["maxPriceFull"]
            )
            min_price = int(
                oracle_prices[to_checksum_address("0xaf88d065e77c8cC2239327C5EDb3A432268e5831")]["minPriceFull"]
            )

            # USDC price
            oracle_contract.functions.setPrimaryPrice(
                to_checksum_address("0xaf88d065e77c8cC2239327C5EDb3A432268e5831"), (min_price, max_price)
            ).transact({"from": controller})

        # Build the transaction
        transaction = order_handler.functions.executeOrder(key, oracle_params).build_transaction(
            {
                "from": keeper_address,  # to_checksum_address(active_signer.get_address()),
                "nonce": nonce,
                "gas": 90000000,
                "gasPrice": web3_provider.eth.gas_price,
            }
        )
        # owner of order_handler 0xE7BfFf2aB721264887230037940490351700a068
        # Sign and send the transaction
        # signed_tx = active_signer.sign_transaction(transaction)
        # tx_hash = web3_provider.eth.send_raw_transaction(signed_tx.raw_transaction)
        tx_hash = web3_provider.eth.send_transaction(transaction)

        # A Python equivalent of logGasUsage function
        if gas_usage_label:
            receipt = web3_provider.eth.wait_for_transaction_receipt(tx_hash)
            gas_used = receipt.gasUsed
            logging.info(f"Gas used ({gas_usage_label}): {gas_used}")

        return tx_hash
