import requests
import time
import logging
import random


class OraclePrices:
    def __init__(self, chain: str):
        self.chain = chain
        self.oracle_url = {
            "arbitrum": ("https://arbitrum-api.gmxinfra2.io/signed_prices/latest"),
            "avalanche": ("https://avalanche-api.gmxinfra.io/signed_prices/latest"),
        }

    def get_recent_prices(self):
        """
        Get raw output of the GMX rest v2 api for signed prices

        Returns
        -------
        dict
            dictionary containing raw output for each token as its keys.

        """
        raw_output = self._make_query().json()
        return self._process_output(raw_output)

    def _make_query(self, max_retries=5, initial_backoff=1, max_backoff=60):
        """
        Make request using oracle URL with retry mechanism.

        Parameters
        ----------
        max_retries : int
            Maximum number of retry attempts
        initial_backoff : float
            Initial backoff time in seconds
        max_backoff : float
            Maximum backoff time in seconds

        Returns
        -------
        requests.models.Response
            Raw request response.

        Raises
        ------
        requests.exceptions.RequestException
            If all retry attempts fail
        """
        url = self.oracle_url[self.chain]
        attempts = 0
        backoff = initial_backoff

        while attempts < max_retries:
            try:
                logging.info(f"Querying oracle at {url}")
                response = requests.get(url, timeout=30)  # Added timeout for safety
                response.raise_for_status()  # Raise exception for 4XX/5XX status codes
                return response

            except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
                attempts += 1

                if attempts >= max_retries:
                    logging.error(f"Failed to query oracle after {max_retries} attempts: {str(e)}")
                    raise

                # Add jitter to avoid thundering herd problem
                jitter = random.uniform(0, 0.1 * backoff)
                wait_time = backoff + jitter

                logging.debug(
                    f"Request failed: {str(e)}. Retrying in {wait_time:.2f} seconds (attempt {attempts}/{max_retries})"
                )
                time.sleep(wait_time)

                # Exponential backoff with capping
                backoff = min(backoff * 2, max_backoff)

    def _process_output(self, output: dict):
        """
        Take the API response and create a new dictionary where the index token
        addresses are the keys

        Parameters
        ----------
        output : dict
            Dictionary of rest API repsonse.

        Returns
        -------
        processed : TYPE
            DESCRIPTION.

        """
        processed = {}
        for i in output["signedPrices"]:
            processed[i["tokenAddress"]] = i

        return processed


if __name__ == "__main__":
    pass
