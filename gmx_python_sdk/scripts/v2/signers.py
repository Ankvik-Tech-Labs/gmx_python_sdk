from abc import ABC, abstractmethod
from eth_account.messages import encode_defunct


class Signer(ABC):
    """Abstract interface for transaction signing."""

    @abstractmethod
    def get_address(self) -> str:
        """Return the wallet address associated with this signer."""
        pass

    @abstractmethod
    def sign_transaction(self, unsigned_tx):
        """Sign a transaction and return the signed transaction object."""
        pass

    @abstractmethod
    def send_transaction(self, unsigned_tx):
        """Sign and send a transaction, returning the transaction hash."""
        pass

    @abstractmethod
    def sign_message(self, message):
        """Sign a message and return the signature."""
        pass


class PrivateKeySigner(Signer):
    """Signer implementation using a private key."""

    def __init__(self, web3_obj, private_key):
        self.web3 = web3_obj
        self._account = self.web3.eth.account.from_key(private_key)

    def get_address(self) -> str:
        return self._account.address

    def sign_transaction(self, unsigned_tx):
        return self.web3.eth.account.sign_transaction(unsigned_tx, self._account.key)

    def send_transaction(self, unsigned_tx):
        signed_tx = self.sign_transaction(unsigned_tx)
        try:
            txn = signed_tx.raw_transaction
        except AttributeError:
            txn = signed_tx.rawTransaction
        return self.web3.eth.send_raw_transaction(txn)

    def sign_message(self, message):
        """
        Sign a message using the private key

        Args:
            message: The message to sign (bytes or hex string)

        Returns:
            Signature as a hex string
        """
        # Ensure the message is in the right format
        # Convert message to SignableMessage format
        if isinstance(message, str):
            if message.startswith("0x"):
                message_bytes = encode_defunct(hexstr=message)
            else:
                message_bytes = encode_defunct(text=message)
        elif isinstance(message, bytes):
            message_bytes = encode_defunct(primitive=message)
        else:
            msg = f"Unsupported message type: {type(message)}"
            raise TypeError(msg)

        # Sign the message
        signature = self.web3.eth.account.sign_message(message_bytes, private_key=self._account.key)

        # Return the signature
        return signature


class Web3ProviderSigner(Signer):
    """Signer that delegates to a connected wallet provider."""

    def __init__(self, web3_obj):
        self.web3 = web3_obj
        # Ensure we have a connected account
        if not self.web3.eth.accounts:
            msg = "No accounts available in the connected Web3 provider"
            raise ValueError(msg)

    def get_address(self) -> str:
        return self.web3.eth.accounts[0]

    def sign_transaction(self, unsigned_tx):
        # Not typically used directly with wallet connections
        msg = "Direct signing not supported with wallet connection"
        raise NotImplementedError(msg)

    def send_transaction(self, unsigned_tx):
        # Web3 provider handles signing internally
        del unsigned_tx["from"]  # Provider will add this
        return self.web3.eth.send_transaction(unsigned_tx)


class LocalAccountSigner(Signer):
    """Signer implementation using a LocalAccount."""

    def __init__(self, web3_obj, account):
        self.web3 = web3_obj
        self.account = account

    def get_address(self) -> str:
        return self.account.address

    def sign_transaction(self, unsigned_tx):
        return self.account.sign_transaction(unsigned_tx)

    def send_transaction(self, unsigned_tx):
        signed_tx = self.sign_transaction(unsigned_tx)
        try:
            txn = signed_tx.raw_transaction
        except AttributeError:
            txn = signed_tx.rawTransaction
        return self.web3.eth.send_raw_transaction(txn)


def create_signer(web3_obj, private_key=None, account=None):
    """
    Factory function to create the appropriate signer based on provided credentials.

    Parameters
    ----------
    web3_obj : web3.Web3
        Web3 instance for the blockchain connection.
    private_key : str, optional
        Private key for creating a PrivateKeySigner.
    account : LocalAccount, optional
        LocalAccount instance for creating a LocalAccountSigner.

    Returns
    -------
    Signer
        Appropriate Signer implementation.
    """
    if account is not None:
        return LocalAccountSigner(web3_obj, account)
    elif private_key:
        return PrivateKeySigner(web3_obj, private_key)
    else:
        return Web3ProviderSigner(web3_obj)
