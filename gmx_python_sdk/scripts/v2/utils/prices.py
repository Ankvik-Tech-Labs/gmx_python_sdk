# return the latest prices


import requests
from decimal import Decimal


def get_tickers_url(network: str) -> str:
    """
    Get the appropriate tickers URL based on the network

    Args:
        network: Network name (arbitrum or avalanche)

    Returns:
        URL string for the tickers API
    """
    if network == "arbitrum":
        return "https://arbitrum-api.gmxinfra.io/prices/tickers"
    elif network == "avalanche":
        return "https://avalanche-api.gmxinfra.io/prices/tickers"
    else:
        msg = f"Unsupported network: {network}"
        raise ValueError(msg)


def fetch_ticker_prices(network: str) -> dict:
    """
    Fetch the latest ticker prices from GMX API

    Args:
        network: Network name (arbitrum or avalanche)

    Returns:
        Dictionary with token addresses as keys and price info as values
    """
    tickers_url = get_tickers_url(network)

    # Fetch data from the API
    response = requests.get(tickers_url)
    response.raise_for_status()  # Raise exception for HTTP errors
    token_prices = response.json()

    # Process the response into a dictionary
    prices_by_token_address = {}
    for token_price in token_prices:
        prices_by_token_address[token_price["tokenAddress"].lower()] = {
            "min": Decimal(token_price["minPrice"]),
            "max": Decimal(token_price["maxPrice"]),
            "symbol": token_price["tokenSymbol"],
            "timestamp": token_price["timestamp"],
        }

    return prices_by_token_address


# Define default price information
# prices = {}
# prices["wnt"] = {
#     "contractName": "wnt",
#     "precision": 8,
#     "min": Decimal("50000000"),  # 5000 * 10^4
#     "max": Decimal("50000000"),  # 5000 * 10^4
# }


# Function to get prices for specific tokens
def get_default_prices(network: str, token_addresses: dict) -> dict:
    """
    Get prices for the default token list

    Args:
        network: Network name (arbitrum or avalanche)
        token_addresses: Dictionary mapping token names to addresses

    Returns:
        Dictionary with token addresses as keys and price info as values
    """
    all_prices = fetch_ticker_prices(network)

    default_prices = {}
    for _, address in token_addresses.items():
        if address.lower() in all_prices:
            default_prices[address] = all_prices[address.lower()]

    return default_prices


if __name__ == "__main__":
    # Example usage
    network = "arbitrum"
    token_addresses = {
        "wnt": "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",
        "wbtc": "0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f",
        "usdc": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
        "usdt": "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9",
    }

    prices = get_default_prices(network, token_addresses)
