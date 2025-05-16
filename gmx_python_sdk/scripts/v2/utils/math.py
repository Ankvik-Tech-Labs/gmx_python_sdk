# numeric_utils.py - Utilities for numeric operations in blockchain applications

import re
from decimal import Decimal
from typing import Union, Optional, Any
from web3 import Web3

# Constants
MAX_UINT8 = "255"  # 2^8 - 1
MAX_UINT32 = "4294967295"  # 2^32 - 1
MAX_UINT64 = "18446744073709551615"  # 2^64 - 1

# Precision for float calculations (10^30)
FLOAT_PRECISION = 10**30


def percentage_to_float(value: str) -> int:
    """
    Convert percentage string to float value with precision

    Args:
        value: Percentage string (e.g. "5%")

    Returns:
        Integer representing the float value with precision
    """
    if not value.endswith("%"):
        raise ValueError("Invalid percentage input")

    trimmed_value = value[:-1]
    # Parse to decimal and convert to wei (with 28 decimals of precision)
    return Web3.to_wei(Decimal(trimmed_value), "ether") // 100


def exponent_to_float(value: str) -> int:
    """
    Convert scientific notation to float value with precision

    Args:
        value: String in scientific notation (e.g. "1.5e-5")

    Returns:
        Integer representing the float value with precision
    """
    if "e" not in value:
        raise ValueError("Invalid exponent input")

    components = value.split("e")
    if len(components) != 2:
        raise ValueError("Invalid exponent input")

    try:
        exponent = int(components[1])
    except ValueError:
        raise ValueError("Invalid exponent")

    # Convert to float with appropriate precision (30 + exponent)
    return Web3.to_wei(Decimal(components[0]), "ether") * 10**exponent


def expand_decimals(n: Union[int, str], decimals: int) -> int:
    """
    Multiply n by 10^decimals

    Args:
        n: Number to scale
        decimals: Number of decimal places to add

    Returns:
        Scaled integer
    """
    return int(n) * 10**decimals


def decimal_to_float(value: Union[int, str], decimals: int = 0) -> int:
    """
    Convert decimal to float with precision

    Args:
        value: Value to convert
        decimals: Current decimal places in the value

    Returns:
        Integer representing the float value with precision
    """
    return expand_decimals(value, 30 - decimals)


def apply_factor(n: Union[int, str], factor: Union[int, str]) -> int:
    """
    Apply factor to a number with proper precision

    Args:
        n: Number to scale
        factor: Factor to apply

    Returns:
        Scaled number
    """
    return (int(n) * int(factor)) // FLOAT_PRECISION


def limit_decimals(amount: Union[float, str], max_decimals: Optional[int] = None) -> str:
    """
    Limit the number of decimal places in a string representation

    Args:
        amount: Amount to format
        max_decimals: Maximum number of decimal places

    Returns:
        Formatted string
    """
    amount_str = str(amount)

    if max_decimals is None:
        return amount_str

    if max_decimals == 0:
        return amount_str.split(".")[0]

    dot_index = amount_str.find(".")
    if dot_index != -1:
        decimals = len(amount_str) - dot_index - 1
        if decimals > max_decimals:
            amount_str = amount_str[: dot_index + max_decimals + 1]

    return amount_str


def pad_decimals(amount: Union[float, str], min_decimals: int) -> str:
    """
    Ensure string has minimum decimal places

    Args:
        amount: Amount to format
        min_decimals: Minimum number of decimal places

    Returns:
        Formatted string
    """
    amount_str = str(amount)
    dot_index = amount_str.find(".")

    if dot_index != -1:
        decimals = len(amount_str) - dot_index - 1
        if decimals < min_decimals:
            amount_str = amount_str + "0" * (min_decimals - decimals)
    else:
        amount_str = amount_str + "." + "0" * min_decimals

    return amount_str


def number_with_commas(x: Union[float, str]) -> str:
    """
    Format number with commas as thousands separators

    Args:
        x: Number to format

    Returns:
        Formatted string
    """
    if not x:
        return "..."

    parts = str(x).split(".")
    parts[0] = re.sub(r"\B(?=(\d{3})+(?!\d))", ",", parts[0])
    return ".".join(parts)


def format_amount(
    amount: Union[int, str],
    token_decimals: int,
    display_decimals: Optional[int] = None,
    use_commas: bool = False,
    default_value: Any = "...",
) -> str:
    """
    Format token amount for display

    Args:
        amount: Amount in wei
        token_decimals: Decimals used by the token
        display_decimals: Decimals to display
        use_commas: Whether to use commas as thousands separators
        default_value: Default value if amount is invalid

    Returns:
        Formatted amount string
    """
    if amount is None or str(amount) == "":
        return default_value

    if display_decimals is None:
        display_decimals = 4

    # Convert from wei to eth-like units
    amount_str = Web3.from_wei(
        int(amount),
        ("ether" if token_decimals == 18 else "lovelace" if token_decimals == 6 else "gwei"),
    )

    # If we need further precision adjustment
    if token_decimals not in (18, 6, 9):
        amount_str = Decimal(amount) / Decimal(10**token_decimals)

    amount_str = limit_decimals(amount_str, display_decimals)

    if display_decimals != 0:
        amount_str = pad_decimals(amount_str, display_decimals)

    if use_commas:
        return number_with_commas(amount_str)

    return str(amount_str)
