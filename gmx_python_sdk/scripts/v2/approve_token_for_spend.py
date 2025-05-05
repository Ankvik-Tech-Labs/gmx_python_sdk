import json
import os

from .gmx_utils import base_dir, convert_to_checksum_address, create_connection


def check_if_approved(
    config,
    spender: str,
    token_to_approve: str,
    amount_of_tokens_to_spend: int,
    max_fee_per_gas,
    approve: bool,
):
    """
    For a given chain, check if a given amount of tokens is approved for spend by a contract, and
    approve is passed as true

    Parameters
    ----------
    config : ConfigManager
        Config manager with connection and signer details
    spender : str
        contract address of the requested spender.
    token_to_approve : str
        contract address of token to spend.
    amount_of_tokens_to_spend : int
        amount of tokens to spend in expanded decimals.
    max_fee_per_gas : int
        maximum gas fee per gas unit
    approve : bool
        Pass as True if we want to approve spend incase it is not already.

    Raises
    ------
    Exception
        Insufficient balance or token not approved for spend.
    """
    connection = create_connection(config)

    if token_to_approve == "0x47904963fc8b2340414262125aF798B9655E58Cd":
        token_to_approve = "0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f"

    spender_checksum_address = convert_to_checksum_address(config, spender)

    # Get the signer and its address
    signer = config.get_signer()
    user_checksum_address = signer.get_address()

    token_checksum_address = convert_to_checksum_address(config, token_to_approve)

    token_contract_abi = json.load(open(os.path.join(base_dir, "gmx_python_sdk", "contracts", "token_approval.json")))

    token_contract_obj = connection.eth.contract(address=token_to_approve, abi=token_contract_abi)

    # TODO - for AVAX support this will need to incl WAVAX address
    if token_checksum_address == "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1":
        try:
            balance_of = connection.eth.get_balance(user_checksum_address)
        except AttributeError:
            balance_of = connection.eth.getBalance(user_checksum_address)

    else:
        balance_of = token_contract_obj.functions.balanceOf(user_checksum_address).call()

    if balance_of < amount_of_tokens_to_spend:
        msg = "Insufficient balance!"
        raise Exception(msg)

    amount_approved = token_contract_obj.functions.allowance(user_checksum_address, spender_checksum_address).call()

    if amount_approved < amount_of_tokens_to_spend and approve:
        nonce = connection.eth.get_transaction_count(user_checksum_address)

        arguments = spender_checksum_address, amount_of_tokens_to_spend
        raw_txn = token_contract_obj.functions.approve(*arguments).build_transaction(
            {
                "from": user_checksum_address,
                "value": 0,
                "chainId": config.chain_id,
                "gas": 4000000,
                "maxFeePerGas": int(max_fee_per_gas),
                "maxPriorityFeePerGas": 0,
                "nonce": nonce,
            }
        )
        # Use signer to send the transaction
        signer.send_transaction(raw_txn)

    if amount_approved < amount_of_tokens_to_spend and not approve:
        msg = "Token not approved for spend, please allow first!"
        raise Exception(msg)


if __name__ == "__main__":
    pass
