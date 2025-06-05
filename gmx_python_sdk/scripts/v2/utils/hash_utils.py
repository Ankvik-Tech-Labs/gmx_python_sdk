# hash.py - Ethereum hashing utilities

from web3 import Web3
from eth_utils import to_hex, keccak
from hexbytes import HexBytes
from typing import Any, Union
from eth_abi import encode

# Initialize Web3 instance
w3 = Web3()


def encode_data(data_types: list[str], data_values: list[Any]) -> str:
    """
    Encode data according to Ethereum ABI

    Args:
        data_types: List of Solidity data types
        data_values: List of values to encode

    Returns:
        Hexadecimal string representation of encoded data
    """
    encoded = w3.codec.encode_abi(data_types, data_values)
    return to_hex(encoded)


def decode_data(data_types: list[str], data: Union[str, bytes]) -> list[Any]:
    """
    Decode ABI encoded data according to provided types

    Args:
        data_types: List of Solidity data types
        data: Encoded data as hex string or bytes

    Returns:
        List of decoded values
    """
    if isinstance(data, str) and data.startswith("0x"):
        data = HexBytes(data)
    elif isinstance(data, str):
        data = HexBytes("0x" + data)

    return w3.codec.decode_abi(data_types, data)


def hash_data(data_types: list[str], data_values: list[Any]) -> HexBytes:
    """
    Encode data according to ABI and compute keccak256 hash

    Args:
        data_types: List of Solidity data types
        data_values: List of values to encode

    Returns:
        keccak256 hash of encoded data
    """
    encoded = encode(data_types, data_values)
    return HexBytes(keccak(encoded))


def hash_string(string: str) -> HexBytes:
    """
    Hash a string using keccak256

    Args:
        string: String to hash

    Returns:
        keccak256 hash of the string
    """
    return hash_data(["string"], [string])


def keccak_string(string: str) -> HexBytes:
    """
    Direct keccak256 hash of UTF-8 encoded string

    Args:
        string: String to hash

    Returns:
        keccak256 hash of UTF-8 encoded string
    """
    return w3.keccak(text=string)
