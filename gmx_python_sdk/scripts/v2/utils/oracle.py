# oracle_utils.py - Oracle utilities for blockchain price feed management
from typing import Any, Union, Optional
from web3 import Web3

from gmx_python_sdk.scripts.v2.gmx_utils import (
    create_connection,
    get_contract_object,
    get_datastore_contract,
)
from gmx_python_sdk.scripts.v2.utils import keys
from gmx_python_sdk.scripts.v2.utils.hash_utils import hash_string, hash_data
from gmx_python_sdk.scripts.v2.utils.math import (
    expand_decimals,
    MAX_UINT8,
    MAX_UINT32,
    MAX_UINT64,
)

# Constants
TOKEN_ORACLE_TYPES = {
    "ONE_PERCENT_PER_MINUTE": hash_string("one-percent-per-minute"),
}
TOKEN_ORACLE_TYPES["DEFAULT"] = TOKEN_ORACLE_TYPES["ONE_PERCENT_PER_MINUTE"]

# Initialize Web3
w3 = Web3()


def sign_price(
    signer,
    salt: str,
    min_oracle_block_number: Union[int, str],
    max_oracle_block_number: Union[int, str],
    oracle_timestamp: Union[int, str],
    block_hash: str,
    token: str,
    token_oracle_type: str,
    precision: Union[int, str],
    min_price: Union[int, str],
    max_price: Union[int, str],
) -> bytes:
    """
    Sign price data for oracle validation

    Args:
        signer: Ethereum signer object
        salt: Unique salt value
        min_oracle_block_number: Minimum block number for oracle data
        max_oracle_block_number: Maximum block number for oracle data
        oracle_timestamp: Timestamp for oracle data
        block_hash: Block hash
        token: Token address
        token_oracle_type: Oracle type identifier
        precision: Price precision
        min_price: Minimum price
        max_price: Maximum price

    Returns:
        Signature string
    """
    if min_oracle_block_number > int(MAX_UINT64):
        raise ValueError(f"minOracleBlockNumber exceeds max value: {min_oracle_block_number}")

    if max_oracle_block_number > int(MAX_UINT64):
        raise ValueError(f"maxOracleBlockNumber exceeds max value: {max_oracle_block_number}")

    if oracle_timestamp > int(MAX_UINT64):
        raise ValueError(f"oracleTimestamp exceeds max value: {oracle_timestamp}")

    if precision > int(MAX_UINT8):
        raise ValueError(f"precision exceeds max value: {precision}")

    # if min_price > int(MAX_UINT32):
    #     raise ValueError(f"minPrice exceeds max value: {min_price}")

    # if max_price > int(MAX_UINT32):
    #     raise ValueError(f"maxPrice exceeds max value: {max_price}")

    expanded_precision = expand_decimals(1, int(precision))
    hash_result = hash_data(
        [
            "bytes32",
            "uint256",
            "uint256",
            "uint256",
            "bytes32",
            "address",
            "bytes32",
            "uint256",
            "uint256",
            "uint256",
        ],
        [
            salt,
            min_oracle_block_number,
            max_oracle_block_number,
            oracle_timestamp,
            block_hash,
            token,
            token_oracle_type,
            expanded_precision,
            min_price,
            max_price,
        ],
    )

    # Convert the hash to a format that can be signed
    message_hash = w3.to_bytes(hexstr=hash_result.hex())

    # Sign the message
    return bytes.fromhex(signer.sign_message(message_hash).signature.hex())


def sign_prices(
    signers: list[Any],
    salt: str,
    min_oracle_block_number: Union[int, str],
    max_oracle_block_number: Union[int, str],
    oracle_timestamp: Union[int, str],
    block_hash: str,
    token: str,
    token_oracle_type: str,
    precision: Union[int, str],
    min_prices: list[Union[int, str]],
    max_prices: list[Union[int, str]],
) -> list[str]:
    """
    Sign price data with multiple signers

    Args:
        signers: list of Ethereum signer objects
        salt: Unique salt value
        min_oracle_block_number: Minimum block number for oracle data
        max_oracle_block_number: Maximum block number for oracle data
        oracle_timestamp: Timestamp for oracle data
        block_hash: Block hash
        token: Token address
        token_oracle_type: Oracle type identifier
        precision: Price precision
        min_prices: list of minimum prices
        max_prices: list of maximum prices

    Returns:
        list of signatures
    """
    signatures = []

    for i in range(len(signers)):
        signature = sign_price(
            signer=signers[i],
            salt=salt,
            min_oracle_block_number=min_oracle_block_number,
            max_oracle_block_number=max_oracle_block_number,
            oracle_timestamp=oracle_timestamp,
            block_hash=block_hash,
            token=token,
            token_oracle_type=token_oracle_type,
            precision=precision,
            min_price=min_prices[i],
            max_price=max_prices[i],
        )
        signatures.append(signature)

    return signatures


def get_signer_info(signer_indexes: list[int]) -> int:
    """
    Generate signer info from signer indexes

    Args:
        signer_indexes: list of signer indexes

    Returns:
        Signer info as a string
    """
    signer_index_length = 16
    signer_info = len(signer_indexes)

    for i in range(len(signer_indexes)):
        signer_index = signer_indexes[i]
        if signer_index > int(MAX_UINT8):
            raise ValueError(f"Max signer index exceeded: {signer_index}")

        # Perform bitwise OR with shifted signer index
        signer_info |= signer_index << ((i + 1) * signer_index_length)

    return signer_info


def get_compacted_values(
    values: list[Union[int, str]],
    compacted_value_bit_length: int,
    max_value: Union[int, str],
) -> list[str]:
    """
    Compact values into fewer slots using bitwise operations

    Args:
        values: list of values to compact
        compacted_value_bit_length: Bit length for each compacted value
        max_value: Maximum allowed value

    Returns:
        list of compacted values as strings
    """
    compacted_values_per_slot = 256 // compacted_value_bit_length
    compacted_values = []
    should_exit = False
    max_value_int = int(max_value)

    for i in range((len(values) - 1) // compacted_values_per_slot + 1):
        value_bits = 0
        for j in range(compacted_values_per_slot):
            index = i * compacted_values_per_slot + j

            if index >= len(values):
                should_exit = True
                break

            value = int(values[index])

            if value > max_value_int:
                raise ValueError(f"Max value exceeded: {value}")

            # Perform bitwise OR with shifted value
            value_bits |= value << (j * compacted_value_bit_length)

        compacted_values.append(str(value_bits))

        if should_exit:
            break

    return compacted_values


def get_compacted_prices(prices: list[Union[int, str]]) -> list[str]:
    """
    Compact price values

    Args:
        prices: list of price values

    Returns:
        list of compacted price values
    """
    return get_compacted_values(prices, 32, MAX_UINT32)


def get_compacted_price_indexes(price_indexes: list[Union[int, str]]) -> list[str]:
    """
    Compact price index values

    Args:
        price_indexes: list of price index values

    Returns:
        list of compacted price index values
    """
    return get_compacted_values(price_indexes, 8, MAX_UINT8)


def get_compacted_decimals(decimals: list[Union[int, str]]) -> list[str]:
    """
    Compact decimal values

    Args:
        decimals: list of decimal values

    Returns:
        list of compacted decimal values
    """
    return get_compacted_values(decimals, 8, MAX_UINT8)


def get_compacted_oracle_block_numbers(block_numbers: list[Union[int, str]]) -> list[str]:
    """
    Compact oracle block number values

    Args:
        block_numbers: list of block number values

    Returns:
        list of compacted block number values
    """
    return get_compacted_values(block_numbers, 64, MAX_UINT64)


def get_compacted_oracle_timestamps(timestamps: list[Union[int, str]]) -> list[str]:
    """
    Compact oracle timestamp values

    Args:
        timestamps: list of timestamp values

    Returns:
        list of compacted timestamp values
    """
    return get_compacted_values(timestamps, 64, MAX_UINT64)


def get_oracle_params_for_simulation(
    tokens: list[str],
    min_prices: list[int],
    max_prices: list[int],
    precisions: list[int],
    oracle_timestamps: list[int],
    web3_provider,
) -> dict:
    """
    Get oracle parameters for simulation

    Args:
        tokens: list of token addresses
        min_prices: list of minimum prices
        max_prices: list of maximum prices
        precisions: list of precision values
        oracle_timestamps: list of oracle timestamps
        web3_provider: Web3 provider

    Returns:
        dictionary with oracle parameters
    """
    if len(tokens) != len(min_prices):
        raise ValueError(f"Invalid input, tokens.length != minPrices.length {tokens}, {min_prices}")

    if len(tokens) != len(max_prices):
        raise ValueError(f"Invalid input, tokens.length != maxPrices.length {tokens}, {max_prices}")

    # Get latest block timestamp
    latest_block = web3_provider.eth.get_block("latest")
    current_timestamp = latest_block.timestamp + 2

    min_timestamp = current_timestamp
    max_timestamp = current_timestamp

    for timestamp in oracle_timestamps:
        min_timestamp = min(min_timestamp, timestamp)
        max_timestamp = max(max_timestamp, timestamp)

    primary_tokens = []
    primary_prices = []

    for i in range(len(tokens)):
        token = tokens[i]
        precision_multiplier = expand_decimals(1, precisions[i])
        min_price = min_prices[i] * precision_multiplier
        max_price = max_prices[i] * precision_multiplier

        primary_tokens.append(token)
        primary_prices.append({"min": min_price, "max": max_price})

    return {
        "primaryTokens": primary_tokens,
        "primaryPrices": primary_prices,
        "minTimestamp": min_timestamp,
        "maxTimestamp": max_timestamp,
    }


def get_oracle_params(
    oracle_salt: str,
    min_oracle_block_numbers: list[int],
    max_oracle_block_numbers: list[int],
    oracle_timestamps: list[int],
    block_hashes: list[str],
    signer_indexes: list[int],
    tokens: list[str],
    token_oracle_types: list[str],
    precisions: list[int],
    min_prices: list[int],
    max_prices: list[int],
    signers: list[Any],
    data_stream_tokens: list[str],
    data_stream_data: list[str],
    price_feed_tokens: list[str],
    config,
    keeper_address: Optional[str] = None,
    controller_address: Optional[str] = None,
    deployed_oracle_address: Optional[str] = None,
) -> dict:
    """
    Get complete oracle parameters

    Args:
        oracle_salt: Oracle salt
        min_oracle_block_numbers: List of minimum oracle block numbers
        max_oracle_block_numbers: List of maximum oracle block numbers
        oracle_timestamps: List of oracle timestamps
        block_hashes: List of block hashes
        signer_indexes: List of signer indexes
        tokens: List of token addresses
        token_oracle_types: List of token oracle types
        precisions: List of precision values
        min_prices: List of minimum prices
        max_prices: List of maximum prices
        signers: List of signers
        data_stream_tokens: List of data stream token addresses
        data_stream_data: List of data stream data
        price_feed_tokens: List of price feed token addresses
        config: ConfigManager instance with connection and contract details

    Returns:
        Dictionary with oracle parameters
    """
    # Get signer info
    signer_info = 1  # get_signer_info(signer_indexes) # 31154177296857295712124637770940423
    print(f"Signer info: {signer_info}")
    data_store = get_datastore_contract(config)

    # Get oracle provider contracts
    web3_obj = create_connection(config)
    gm_oracle_provider = get_contract_object(web3_obj, "gmoracleprovider", config.chain)
    chainlink_price_feed_provider = get_contract_object(web3_obj, "chainlinkpricefeedprovider", config.chain)
    chainlink_data_stream_provider = get_contract_object(web3_obj, "chainlinkdatastreamprovider", config.chain)

    params = {"tokens": [], "providers": [], "data": []}

    for i in range(len(tokens)):
        min_oracle_block_number = min_oracle_block_numbers[i]
        max_oracle_block_number = max_oracle_block_numbers[i]
        oracle_timestamp = oracle_timestamps[i]
        block_hash = block_hashes[i]
        token = tokens[i]
        token_oracle_type = token_oracle_types[i]
        precision = precisions[i]
        min_price = min_prices[i]
        max_price = max_prices[i]

        signatures = []
        signed_min_prices = []
        signed_max_prices = []

        for j in range(len(signers)):
            signature = sign_price(
                signer=signers[j],
                salt=oracle_salt,
                min_oracle_block_number=min_oracle_block_number,
                max_oracle_block_number=max_oracle_block_number,
                oracle_timestamp=oracle_timestamp,
                block_hash=block_hash,
                token=token,
                token_oracle_type=token_oracle_type,
                precision=precision,
                min_price=min_price,
                max_price=max_price,
            )

            signed_min_prices.append(min_price)
            signed_max_prices.append(max_price)
            signatures.append(signature)

        # Encode the data using the web3 connection from the SDK
        data_tuple = [
            token,
            signer_info,
            precision,
            min_oracle_block_number,
            max_oracle_block_number,
            oracle_timestamp,
            block_hash,
            signed_min_prices,
            signed_max_prices,
            signatures,
        ]
        print(f"Data tuple: {data_tuple}")
        # TODO: Look at this encoding might be wrong that's why the values are 0 for target token
        # TODO: Update the custom oracle provider contract to see what'sup with it
        # Use the appropriate encoding method for the web3.py version
        try:
            # For newer web3.py versions
            data = web3_obj.eth.codec.encode_abi(
                ["(address,uint256,uint256,uint256,uint256,uint256,bytes32,uint256[],uint256[],bytes[])"],
                [data_tuple],
            ).hex()
        except AttributeError:
            # For older web3.py versions
            from eth_abi import encode

            data = (
                "0x"
                + encode(
                    ["(address,uint256,uint256,uint256,uint256,uint256,bytes32,uint256[],uint256[],bytes[])"],
                    [data_tuple],
                ).hex()
            )

        params["tokens"].append(token)
        # params["providers"].append(gm_oracle_provider.address)
        # custom deployed oracle
        params["providers"].append(deployed_oracle_address)
        params["data"].append(data)

    for i in range(len(price_feed_tokens)):
        token = price_feed_tokens[i]
        # Set the oracle provider for token using the SDK's pattern
        data_store.functions.setAddress(
            keys.oracle_provider_for_token_key(token),
            chainlink_price_feed_provider.address,
        ).transact({"from": controller_address})

        params["tokens"].append(token)
        params["providers"].append(chainlink_price_feed_provider.address)
        params["data"].append("0x")

    for i in range(len(data_stream_tokens)):
        token = data_stream_tokens[i]
        # Set the oracle provider for token using the SDK's pattern
        data_store.functions.setAddress(
            keys.oracle_provider_for_token_key(token),
            chainlink_data_stream_provider.address,
        ).transact({"from": controller_address})

        params["tokens"].append(token)
        params["providers"].append(chainlink_data_stream_provider.address)
        params["data"].append(data_stream_data[i])

    return params


def get_oracle_params_for_custom_oracle(
    oracle_salt: str,
    min_oracle_block_numbers: list[int],
    max_oracle_block_numbers: list[int],
    oracle_timestamps: list[int],
    block_hashes: list[str],
    signer_indexes: list[int],
    tokens: list[str],
    token_oracle_types: list[str],
    precisions: list[int],
    min_prices: list[int],
    max_prices: list[int],
    signers: list[Any],
    data_stream_tokens: list[str],
    data_stream_data: list[str],
    price_feed_tokens: list[str],
    config,
    keeper_address: Optional[str] = None,
    controller_address: Optional[str] = None,
    deployed_oracle_address: Optional[str] = None,
) -> dict:
    """
    Get complete oracle parameters, formatting `data` for getOraclePrice(token, data)

    For custom providers, `data` is abi.encode([uint256, uint256, uint256], [min_price, max_price, timestamp]).
    Chainlink feeds use empty data (`0x`).
    Data streams pass through provided `data_stream_data`.

    Returns:
        Dictionary with keys: tokens, providers, data
    """
    # Prepare web3 and contracts
    web3_obj = create_connection(config)
    data_store = get_datastore_contract(config)
    chainlink_price_feed_provider = get_contract_object(web3_obj, "chainlinkpricefeedprovider", config.chain)
    chainlink_data_stream_provider = get_contract_object(web3_obj, "chainlinkdatastreamprovider", config.chain)

    params = {"tokens": [], "providers": [], "data": []}

    # Custom oracle encoding: [min_price, max_price, timestamp]
    for i, token in enumerate(tokens):
        min_price = min_prices[i]
        max_price = max_prices[i]
        timestamp = oracle_timestamps[i]

        # Encode only the three uint256 values for getOraclePrice
        try:
            encoded = web3_obj.eth.codec.encode_abi(
                ["uint256", "uint256", "uint256"], [min_price, max_price, timestamp]
            ).hex()
            data = "0x" + encoded if not encoded.startswith("0x") else encoded
        except AttributeError:
            from eth_abi import encode

            data = "0x" + encode(["uint256", "uint256", "uint256"], [min_price, max_price, timestamp]).hex()

        params["tokens"].append(token)
        params["providers"].append(deployed_oracle_address)
        params["data"].append(data)

    # Chainlink price feeds: empty data
    for token in price_feed_tokens:
        data_store.functions.setAddress(
            keys.oracle_provider_for_token_key(token),
            chainlink_price_feed_provider.address,
        ).transact({"from": controller_address})

        params["tokens"].append(token)
        params["providers"].append(chainlink_price_feed_provider.address)
        params["data"].append("0x")

    # Chainlink data streams: passed-through data
    for i, token in enumerate(data_stream_tokens):
        data_store.functions.setAddress(
            keys.oracle_provider_for_token_key(token),
            chainlink_data_stream_provider.address,
        ).transact({"from": controller_address})

        params["tokens"].append(token)
        params["providers"].append(chainlink_data_stream_provider.address)
        params["data"].append(data_stream_data[i])

    return params


DEFAULT_ORACLE_PROVIDER = "chainlinkDataStream"


def get_oracle_provider_address(oracle_provider_key: Optional[str] = None) -> str:
    """
    Get address for specific oracle provider

    Args:
        oracle_provider_key: Oracle provider identifier

    Returns:
        Oracle provider address
    """
    if not oracle_provider_key:
        oracle_provider_key = DEFAULT_ORACLE_PROVIDER

    oracle_provider_map = get_oracle_provider_map()
    if oracle_provider_key not in oracle_provider_map:
        raise ValueError(f"Unknown oracle provider {oracle_provider_key}")

    return oracle_provider_map[oracle_provider_key]


def get_oracle_provider_key(oracle_provider_address: str) -> Optional[str]:
    """
    Get key for oracle provider address

    Args:
        oracle_provider_address: Oracle provider address

    Returns:
        Oracle provider key if found
    """
    oracle_provider_map = get_oracle_provider_map()

    for key, address in oracle_provider_map.items():
        if address == oracle_provider_address:
            return key

    return None


_oracle_provider_map = None


def get_oracle_provider_map(config):
    """
    Get map of oracle provider keys to addresses

    Args:
        config: ConfigManager instance with connection details

    Returns:
        Oracle provider map mapping provider names to addresses
    """
    global _oracle_provider_map

    if not _oracle_provider_map:
        # Get web3 connection from config
        web3_obj = create_connection(config)

        # Load contract objects using the SDK's pattern
        chainlink_price_feed_provider = get_contract_object(web3_obj, "chainlinkpricefeedprovider", config.chain)

        chainlink_data_stream_provider = get_contract_object(web3_obj, "chainlinkdatastreamprovider", config.chain)

        gm_oracle_provider = get_contract_object(web3_obj, "gmoracleprovider", config.chain)

        # Create the provider map with contract addresses
        _oracle_provider_map = {
            "chainlinkPriceFeed": chainlink_price_feed_provider.address,
            "chainlinkDataStream": chainlink_data_stream_provider.address,
            "gmOracle": gm_oracle_provider.address,
        }

    return _oracle_provider_map


def encode_data_stream_data(data: dict) -> str:
    """
    Encode data stream data for oracle use

    Args:
        data: dictionary with data stream fields

    Returns:
        Encoded data as hex string
    """
    feed_id = data.get("feedId")
    valid_from_timestamp = data.get("validFromTimestamp")
    observations_timestamp = data.get("observationsTimestamp")
    native_fee = data.get("nativeFee")
    link_fee = data.get("linkFee")
    expires_at = data.get("expiresAt")
    price = data.get("price")
    bid = data.get("bid")
    ask = data.get("ask")

    encoded = w3.eth.abi.encode_abi(
        [
            "bytes32",
            "uint32",
            "uint32",
            "uint192",
            "uint192",
            "uint32",
            "int192",
            "int192",
            "int192",
        ],
        [
            feed_id,
            valid_from_timestamp,
            observations_timestamp,
            native_fee,
            link_fee,
            expires_at,
            price,
            bid,
            ask,
        ],
    )

    return encoded.hex()
