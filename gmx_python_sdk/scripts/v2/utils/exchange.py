import logging
from typing import Any

import web3

from gmx_python_sdk.scripts.v2.gmx_utils import get_contract_object
from gmx_python_sdk.scripts.v2.utils.oracle import (
    get_oracle_params,
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
    contracts = fixture.contracts
    wnt = contracts.get("wnt")
    wbtc = contracts.get("wbtc")
    usdc = contracts.get("usdc")
    usdt = contracts.get("usdt")

    # Default price info for common tokens
    ref_prices = fixture.prices
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
                raise ValueError(f"Missing price info for token {token.address}")

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


def execute_with_oracle_params(fixture, overrides: dict[str, Any]):
    """
    Execute a transaction with oracle parameters

    Args:
        fixture: Object containing account and contract references
        overrides: Parameters for execution including oracle info

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
    execute = overrides.get("execute")
    simulate_execute = overrides.get("simulateExecute")
    simulate = overrides.get("simulate", False)
    gas_usage_label = overrides.get("gasUsageLabel")
    data_stream_tokens = overrides.get("dataStreamTokens", [])
    data_stream_data = overrides.get("dataStreamData", [])
    price_feed_tokens = overrides.get("priceFeedTokens", [])

    # Get Web3 provider and account references
    web3_provider = fixture.web3_provider
    chain = fixture.chain
    signer = fixture.accounts.get("signer", [])
    oracle_salt = fixture.props.get("oracleSalt")
    signer_indexes = fixture.props.get("signerIndexes", [])

    # Validate inputs
    if len(tokens) > len(precisions) or len(tokens) > len(min_prices) or len(tokens) > len(max_prices):
        msg = "`tokens` should not be bigger than `precisions`, `minPrices` or `maxPrices`"
        raise ValueError(msg)

    if simulate and not simulate_execute:
        raise ValueError("`simulateExecute` is required if `simulate` is true")

    if not oracle_block_number:
        raise ValueError("`oracleBlockNumber` is required")

    # Get blockchain block information
    block = web3_provider.eth.get_block(int(oracle_block_number))

    # Default to standard oracle types if not provided
    token_oracle_types = overrides.get("tokenOracleTypes", [TOKEN_ORACLE_TYPES["DEFAULT"]] * len(tokens))

    # Initialize oracle block information
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
        # Use provided values or defaults based on the current block
        min_oracle_block_numbers = overrides.get("minOracleBlockNumbers", [block.number] * len(tokens))
        max_oracle_block_numbers = overrides.get("maxOracleBlockNumbers", [block.number] * len(tokens))
        oracle_timestamps = overrides.get("oracleTimestamps", [block.timestamp] * len(tokens))
        block_hashes = [block.hash.hex() if isinstance(block.hash, bytes) else block.hash] * len(tokens)

    # Prepare arguments for oracle parameters
    args = {
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
        "signer": signer,
        "data_stream_tokens": data_stream_tokens,
        "data_stream_data": data_stream_data,
        "price_feed_tokens": price_feed_tokens,
    }
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
        # Get full oracle parameters for execution
        oracle_params = get_oracle_params(config=fixture.config, **args)

        logging.info(f"Key: {key}")
        logging.info(f"Oracle Params: {oracle_params}")

        nonce = web3.eth.get_transaction_count(signer.get_address())
        # Build the transaction
        transaction = order_handler.functions.executeOrder(key, oracle_params).build_transaction(
            {
                "from": signer.get_address(),
                "nonce": nonce,
                "gas": 3000000,  # Set appropriate gas limit
                "maxFeePerGas": web3.eth.gas_price * 2,  # Adjust as needed
                "maxPriorityFeePerGas": web3.eth.gas_price // 10,  # Adjust as needed
            }
        )

        # Sign and send the transaction
        signed_tx = signer.sign_transaction(transaction)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

        # A Python equivalent of logGasUsage function
        if gas_usage_label:
            receipt = web3_provider.eth.wait_for_transaction_receipt(tx_hash)
            gas_used = receipt.gasUsed
            logging.info(f"Gas used ({gas_usage_label}): {gas_used}")

        return tx_hash
