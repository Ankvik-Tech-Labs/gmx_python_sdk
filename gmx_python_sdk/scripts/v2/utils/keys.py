# keys.py - Protocol key management
from typing import Union
from hexbytes import HexBytes
from gmx_python_sdk.scripts.v2.utils.hash_utils import hash_string, hash_data

# Basic protocol constants
WNT = hash_string("WNT")
NONCE = hash_string("NONCE")

FEE_RECEIVER = hash_string("FEE_RECEIVER")
HOLDING_ADDRESS = hash_string("HOLDING_ADDRESS")
SEQUENCER_GRACE_DURATION = hash_string("SEQUENCER_GRACE_DURATION")
IN_STRICT_PRICE_FEED_MODE = hash_string("IN_STRICT_PRICE_FEED_MODE")

MIN_HANDLE_EXECUTION_ERROR_GAS = hash_string("MIN_HANDLE_EXECUTION_ERROR_GAS")
MIN_ADDITIONAL_GAS_FOR_EXECUTION = hash_string("MIN_ADDITIONAL_GAS_FOR_EXECUTION")
MIN_HANDLE_EXECUTION_ERROR_GAS_TO_FORWARD = hash_string("MIN_HANDLE_EXECUTION_ERROR_GAS_TO_FORWARD")
REFUND_EXECUTION_FEE_GAS_LIMIT = hash_string("REFUND_EXECUTION_FEE_GAS_LIMIT")

MAX_LEVERAGE = hash_string("MAX_LEVERAGE")

MARKET_LIST = hash_string("MARKET_LIST")

DEPOSIT_LIST = hash_string("DEPOSIT_LIST")
ACCOUNT_DEPOSIT_LIST = hash_string("ACCOUNT_DEPOSIT_LIST")

GLV_LIST = hash_string("GLV_LIST")

GLV_DEPOSIT_LIST = hash_string("GLV_DEPOSIT_LIST")
ACCOUNT_GLV_DEPOSIT_LIST = hash_string("ACCOUNT_GLV_DEPOSIT_LIST")

WITHDRAWAL_LIST = hash_string("WITHDRAWAL_LIST")
ACCOUNT_WITHDRAWAL_LIST = hash_string("ACCOUNT_WITHDRAWAL_LIST")

GLV_WITHDRAWAL_LIST = hash_string("GLV_WITHDRAWAL_LIST")
ACCOUNT_GLV_WITHDRAWAL_LIST = hash_string("ACCOUNT_GLV_WITHDRAWAL_LIST")

SHIFT_LIST = hash_string("SHIFT_LIST")
ACCOUNT_SHIFT_LIST = hash_string("ACCOUNT_SHIFT_LIST")

GLV_SHIFT_LIST = hash_string("GLV_SHIFT_LIST")

POSITION_LIST = hash_string("POSITION_LIST")
ACCOUNT_POSITION_LIST = hash_string("ACCOUNT_POSITION_LIST")

ORDER_LIST = hash_string("ORDER_LIST")
ACCOUNT_ORDER_LIST = hash_string("ACCOUNT_ORDER_LIST")

SUBACCOUNT_LIST = hash_string("SUBACCOUNT_LIST")

AUTO_CANCEL_ORDER_LIST = hash_string("AUTO_CANCEL_ORDER_LIST")

CREATE_DEPOSIT_FEATURE_DISABLED = hash_string("CREATE_DEPOSIT_FEATURE_DISABLED")
CANCEL_DEPOSIT_FEATURE_DISABLED = hash_string("CANCEL_DEPOSIT_FEATURE_DISABLED")
EXECUTE_DEPOSIT_FEATURE_DISABLED = hash_string("EXECUTE_DEPOSIT_FEATURE_DISABLED")
GASLESS_FEATURE_DISABLED = hash_string("GASLESS_FEATURE_DISABLED")

CREATE_ORDER_FEATURE_DISABLED = hash_string("CREATE_ORDER_FEATURE_DISABLED")
EXECUTE_ORDER_FEATURE_DISABLED = hash_string("EXECUTE_ORDER_FEATURE_DISABLED")
EXECUTE_ADL_FEATURE_DISABLED = hash_string("EXECUTE_ADL_FEATURE_DISABLED")
UPDATE_ORDER_FEATURE_DISABLED = hash_string("UPDATE_ORDER_FEATURE_DISABLED")
CANCEL_ORDER_FEATURE_DISABLED = hash_string("CANCEL_ORDER_FEATURE_DISABLED")

CREATE_WITHDRAWAL_FEATURE_DISABLED = hash_string("CREATE_WITHDRAWAL_FEATURE_DISABLED")
CANCEL_WITHDRAWAL_FEATURE_DISABLED = hash_string("CANCEL_WITHDRAWAL_FEATURE_DISABLED")
EXECUTE_WITHDRAWAL_FEATURE_DISABLED = hash_string("EXECUTE_WITHDRAWAL_FEATURE_DISABLED")
EXECUTE_ATOMIC_WITHDRAWAL_FEATURE_DISABLED = hash_string("EXECUTE_ATOMIC_WITHDRAWAL_FEATURE_DISABLED")

CREATE_SHIFT_FEATURE_DISABLED = hash_string("CREATE_SHIFT_FEATURE_DISABLED")
EXECUTE_SHIFT_FEATURE_DISABLED = hash_string("EXECUTE_SHIFT_FEATURE_DISABLED")
CANCEL_SHIFT_FEATURE_DISABLED = hash_string("CANCEL_SHIFT_FEATURE_DISABLED")

CREATE_GLV_DEPOSIT_FEATURE_DISABLED = hash_string("CREATE_GLV_DEPOSIT_FEATURE_DISABLED")

CLAIMABLE_FEE_AMOUNT = hash_string("CLAIMABLE_FEE_AMOUNT")
CLAIMABLE_FUNDING_AMOUNT = hash_string("CLAIMABLE_FUNDING_AMOUNT")
CLAIMABLE_COLLATERAL_AMOUNT = hash_string("CLAIMABLE_COLLATERAL_AMOUNT")
CLAIMABLE_COLLATERAL_FACTOR = hash_string("CLAIMABLE_COLLATERAL_FACTOR")
CLAIMABLE_COLLATERAL_TIME_DIVISOR = hash_string("CLAIMABLE_COLLATERAL_TIME_DIVISOR")

CLAIMABLE_UI_FEE_AMOUNT = hash_string("CLAIMABLE_UI_FEE_AMOUNT")
AFFILIATE_REWARD = hash_string("AFFILIATE_REWARD")
MAX_UI_FEE_FACTOR = hash_string("MAX_UI_FEE_FACTOR")
MIN_AFFILIATE_REWARD_FACTOR = hash_string("MIN_AFFILIATE_REWARD_FACTOR")

MAX_AUTO_CANCEL_ORDERS = hash_string("MAX_AUTO_CANCEL_ORDERS")
MAX_TOTAL_CALLBACK_GAS_LIMIT_FOR_AUTO_CANCEL_ORDERS = hash_string("MAX_TOTAL_CALLBACK_GAS_LIMIT_FOR_AUTO_CANCEL_ORDERS")

IS_MARKET_DISABLED = hash_string("IS_MARKET_DISABLED")
MAX_SWAP_PATH_LENGTH = hash_string("MAX_SWAP_PATH_LENGTH")
MIN_MARKET_TOKENS_FOR_FIRST_DEPOSIT = hash_string("MIN_MARKET_TOKENS_FOR_FIRST_DEPOSIT")

MIN_ORACLE_BLOCK_CONFIRMATIONS = hash_string("MIN_ORACLE_BLOCK_CONFIRMATIONS")
MAX_ORACLE_PRICE_AGE = hash_string("MAX_ORACLE_PRICE_AGE")
MAX_ORACLE_REF_PRICE_DEVIATION_FACTOR = hash_string("MAX_ORACLE_REF_PRICE_DEVIATION_FACTOR")
MIN_ORACLE_SIGNERS = hash_string("MIN_ORACLE_SIGNERS")
MAX_ORACLE_TIMESTAMP_RANGE = hash_string("MAX_ORACLE_TIMESTAMP_RANGE")
IS_ORACLE_PROVIDER_ENABLED = hash_string("IS_ORACLE_PROVIDER_ENABLED")
IS_ATOMIC_ORACLE_PROVIDER = hash_string("IS_ATOMIC_ORACLE_PROVIDER")
CHAINLINK_PAYMENT_TOKEN = hash_string("CHAINLINK_PAYMENT_TOKEN")

MIN_COLLATERAL_FACTOR = hash_string("MIN_COLLATERAL_FACTOR")
MIN_COLLATERAL_FACTOR_FOR_OPEN_INTEREST_MULTIPLIER = hash_string("MIN_COLLATERAL_FACTOR_FOR_OPEN_INTEREST_MULTIPLIER")
MIN_COLLATERAL_USD = hash_string("MIN_COLLATERAL_USD")
MIN_POSITION_SIZE_USD = hash_string("MIN_POSITION_SIZE_USD")

SWAP_FEE_RECEIVER_FACTOR = hash_string("SWAP_FEE_RECEIVER_FACTOR")
ATOMIC_SWAP_FEE_TYPE = hash_string("ATOMIC_SWAP_FEE_TYPE")
TOKEN_TRANSFER_GAS_LIMIT = hash_string("TOKEN_TRANSFER_GAS_LIMIT")
NATIVE_TOKEN_TRANSFER_GAS_LIMIT = hash_string("NATIVE_TOKEN_TRANSFER_GAS_LIMIT")

MAX_CALLBACK_GAS_LIMIT = hash_string("MAX_CALLBACK_GAS_LIMIT")

REQUEST_EXPIRATION_TIME = hash_string("REQUEST_EXPIRATION_TIME")

PRICE_FEED = hash_string("PRICE_FEED")
PRICE_FEED_MULTIPLIER = hash_string("PRICE_FEED_MULTIPLIER")
PRICE_FEED_HEARTBEAT_DURATION = hash_string("PRICE_FEED_HEARTBEAT_DURATION")
DATA_STREAM_ID = hash_string("DATA_STREAM_ID")
DATA_STREAM_MULTIPLIER = hash_string("DATA_STREAM_MULTIPLIER")
DATA_STREAM_SPREAD_REDUCTION_FACTOR = hash_string("DATA_STREAM_SPREAD_REDUCTION_FACTOR")
STABLE_PRICE = hash_string("STABLE_PRICE")

ORACLE_TYPE = hash_string("ORACLE_TYPE")
ORACLE_PROVIDER_FOR_TOKEN = hash_string("ORACLE_PROVIDER_FOR_TOKEN")
ORACLE_TIMESTAMP_ADJUSTMENT = hash_string("ORACLE_TIMESTAMP_ADJUSTMENT")

OPEN_INTEREST = hash_string("OPEN_INTEREST")
OPEN_INTEREST_IN_TOKENS = hash_string("OPEN_INTEREST_IN_TOKENS")

COLLATERAL_SUM = hash_string("COLLATERAL_SUM")
POOL_AMOUNT = hash_string("POOL_AMOUNT")
MAX_POOL_AMOUNT = hash_string("MAX_POOL_AMOUNT")
MAX_POOL_USD_FOR_DEPOSIT = hash_string("MAX_POOL_USD_FOR_DEPOSIT")
MAX_OPEN_INTEREST = hash_string("MAX_OPEN_INTEREST")

POSITION_IMPACT_POOL_AMOUNT = hash_string("POSITION_IMPACT_POOL_AMOUNT")
MIN_POSITION_IMPACT_POOL_AMOUNT = hash_string("MIN_POSITION_IMPACT_POOL_AMOUNT")
POSITION_IMPACT_POOL_DISTRIBUTION_RATE = hash_string("POSITION_IMPACT_POOL_DISTRIBUTION_RATE")
POSITION_IMPACT_POOL_DISTRIBUTED_AT = hash_string("POSITION_IMPACT_POOL_DISTRIBUTED_AT")

SWAP_IMPACT_POOL_AMOUNT = hash_string("SWAP_IMPACT_POOL_AMOUNT")

POSITION_FEE_RECEIVER_FACTOR = hash_string("POSITION_FEE_RECEIVER_FACTOR")
LIQUIDATION_FEE_RECEIVER_FACTOR = hash_string("LIQUIDATION_FEE_RECEIVER_FACTOR")
BORROWING_FEE_RECEIVER_FACTOR = hash_string("BORROWING_FEE_RECEIVER_FACTOR")

SWAP_FEE_FACTOR = hash_string("SWAP_FEE_FACTOR")
DEPOSIT_FEE_FACTOR = hash_string("DEPOSIT_FEE_FACTOR")
WITHDRAWAL_FEE_FACTOR = hash_string("WITHDRAWAL_FEE_FACTOR")
ATOMIC_SWAP_FEE_FACTOR = hash_string("ATOMIC_SWAP_FEE_FACTOR")
ATOMIC_WITHDRAWAL_FEE_FACTOR = hash_string("ATOMIC_WITHDRAWAL_FEE_FACTOR")
SWAP_IMPACT_FACTOR = hash_string("SWAP_IMPACT_FACTOR")
SWAP_IMPACT_EXPONENT_FACTOR = hash_string("SWAP_IMPACT_EXPONENT_FACTOR")

POSITION_IMPACT_FACTOR = hash_string("POSITION_IMPACT_FACTOR")
POSITION_IMPACT_EXPONENT_FACTOR = hash_string("POSITION_IMPACT_EXPONENT_FACTOR")
MAX_POSITION_IMPACT_FACTOR = hash_string("MAX_POSITION_IMPACT_FACTOR")
MAX_POSITION_IMPACT_FACTOR_FOR_LIQUIDATIONS = hash_string("MAX_POSITION_IMPACT_FACTOR_FOR_LIQUIDATIONS")
POSITION_FEE_FACTOR = hash_string("POSITION_FEE_FACTOR")
LIQUIDATION_FEE_FACTOR = hash_string("LIQUIDATION_FEE_FACTOR")
PRO_TRADER_TIER = hash_string("PRO_TRADER_TIER")
PRO_DISCOUNT_FACTOR = hash_string("PRO_DISCOUNT_FACTOR")

RESERVE_FACTOR = hash_string("RESERVE_FACTOR")
OPEN_INTEREST_RESERVE_FACTOR = hash_string("OPEN_INTEREST_RESERVE_FACTOR")

MAX_PNL_FACTOR = hash_string("MAX_PNL_FACTOR")
MAX_PNL_FACTOR_FOR_TRADERS = hash_string("MAX_PNL_FACTOR_FOR_TRADERS")
MAX_PNL_FACTOR_FOR_ADL = hash_string("MAX_PNL_FACTOR_FOR_ADL")
MIN_PNL_FACTOR_AFTER_ADL = hash_string("MIN_PNL_FACTOR_AFTER_ADL")
MAX_PNL_FACTOR_FOR_DEPOSITS = hash_string("MAX_PNL_FACTOR_FOR_DEPOSITS")
MAX_PNL_FACTOR_FOR_WITHDRAWALS = hash_string("MAX_PNL_FACTOR_FOR_WITHDRAWALS")

LATEST_ADL_BLOCK = hash_string("LATEST_ADL_BLOCK")
IS_ADL_ENABLED = hash_string("IS_ADL_ENABLED")

FUNDING_FACTOR = hash_string("FUNDING_FACTOR")
FUNDING_EXPONENT_FACTOR = hash_string("FUNDING_EXPONENT_FACTOR")

SAVED_FUNDING_FACTOR_PER_SECOND = hash_string("SAVED_FUNDING_FACTOR_PER_SECOND")
FUNDING_INCREASE_FACTOR_PER_SECOND = hash_string("FUNDING_INCREASE_FACTOR_PER_SECOND")
FUNDING_DECREASE_FACTOR_PER_SECOND = hash_string("FUNDING_DECREASE_FACTOR_PER_SECOND")
MIN_FUNDING_FACTOR_PER_SECOND = hash_string("MIN_FUNDING_FACTOR_PER_SECOND")
MAX_FUNDING_FACTOR_PER_SECOND = hash_string("MAX_FUNDING_FACTOR_PER_SECOND")
THRESHOLD_FOR_STABLE_FUNDING = hash_string("THRESHOLD_FOR_STABLE_FUNDING")
THRESHOLD_FOR_DECREASE_FUNDING = hash_string("THRESHOLD_FOR_DECREASE_FUNDING")

FUNDING_FEE_AMOUNT_PER_SIZE = hash_string("FUNDING_FEE_AMOUNT_PER_SIZE")
CLAIMABLE_FUNDING_AMOUNT_PER_SIZE = hash_string("CLAIMABLE_FUNDING_AMOUNT_PER_SIZE")
FUNDING_UPDATED_AT = hash_string("FUNDING_UPDATED_AT")

OPTIMAL_USAGE_FACTOR = hash_string("OPTIMAL_USAGE_FACTOR")
BASE_BORROWING_FACTOR = hash_string("BASE_BORROWING_FACTOR")
ABOVE_OPTIMAL_USAGE_BORROWING_FACTOR = hash_string("ABOVE_OPTIMAL_USAGE_BORROWING_FACTOR")
IGNORE_OPEN_INTEREST_FOR_USAGE_FACTOR = hash_string("IGNORE_OPEN_INTEREST_FOR_USAGE_FACTOR")

BORROWING_FACTOR = hash_string("BORROWING_FACTOR")
BORROWING_EXPONENT_FACTOR = hash_string("BORROWING_EXPONENT_FACTOR")

SKIP_BORROWING_FEE_FOR_SMALLER_SIDE = hash_string("SKIP_BORROWING_FEE_FOR_SMALLER_SIDE")

ESTIMATED_GAS_FEE_BASE_AMOUNT_V2_1 = hash_string("ESTIMATED_GAS_FEE_BASE_AMOUNT_V2_1")
ESTIMATED_GAS_FEE_PER_ORACLE_PRICE = hash_string("ESTIMATED_GAS_FEE_PER_ORACLE_PRICE")
ESTIMATED_GAS_FEE_MULTIPLIER_FACTOR = hash_string("ESTIMATED_GAS_FEE_MULTIPLIER_FACTOR")
MAX_EXECUTION_FEE_MULTIPLIER_FACTOR = hash_string("MAX_EXECUTION_FEE_MULTIPLIER_FACTOR")

EXECUTION_GAS_FEE_BASE_AMOUNT_V2_1 = hash_string("EXECUTION_GAS_FEE_BASE_AMOUNT_V2_1")
EXECUTION_GAS_FEE_PER_ORACLE_PRICE = hash_string("EXECUTION_GAS_FEE_PER_ORACLE_PRICE")
EXECUTION_GAS_FEE_MULTIPLIER_FACTOR = hash_string("EXECUTION_GAS_FEE_MULTIPLIER_FACTOR")

DEPOSIT_GAS_LIMIT = hash_string("DEPOSIT_GAS_LIMIT")
WITHDRAWAL_GAS_LIMIT = hash_string("WITHDRAWAL_GAS_LIMIT")
SHIFT_GAS_LIMIT = hash_string("SHIFT_GAS_LIMIT")
SINGLE_SWAP_GAS_LIMIT = hash_string("SINGLE_SWAP_GAS_LIMIT")
INCREASE_ORDER_GAS_LIMIT = hash_string("INCREASE_ORDER_GAS_LIMIT")
DECREASE_ORDER_GAS_LIMIT = hash_string("DECREASE_ORDER_GAS_LIMIT")
SWAP_ORDER_GAS_LIMIT = hash_string("SWAP_ORDER_GAS_LIMIT")
GLV_DEPOSIT_GAS_LIMIT = hash_string("GLV_DEPOSIT_GAS_LIMIT")
GLV_WITHDRAWAL_GAS_LIMIT = hash_string("GLV_WITHDRAWAL_GAS_LIMIT")
GLV_SHIFT_GAS_LIMIT = hash_string("GLV_SHIFT_GAS_LIMIT")
GLV_PER_MARKET_GAS_LIMIT = hash_string("GLV_PER_MARKET_GAS_LIMIT")

CUMULATIVE_BORROWING_FACTOR = hash_string("CUMULATIVE_BORROWING_FACTOR")
CUMULATIVE_BORROWING_FACTOR_UPDATED_AT = hash_string("CUMULATIVE_BORROWING_FACTOR_UPDATED_AT")

VIRTUAL_TOKEN_ID = hash_string("VIRTUAL_TOKEN_ID")
VIRTUAL_MARKET_ID = hash_string("VIRTUAL_MARKET_ID")

VIRTUAL_INVENTORY_FOR_SWAPS = hash_string("VIRTUAL_INVENTORY_FOR_SWAPS")
VIRTUAL_INVENTORY_FOR_POSITIONS = hash_string("VIRTUAL_INVENTORY_FOR_POSITIONS")

MAX_ALLOWED_SUBACCOUNT_ACTION_COUNT = hash_string("MAX_ALLOWED_SUBACCOUNT_ACTION_COUNT")
SUBACCOUNT_ACTION_COUNT = hash_string("SUBACCOUNT_ACTION_COUNT")
SUBACCOUNT_AUTO_TOP_UP_AMOUNT = hash_string("SUBACCOUNT_AUTO_TOP_UP_AMOUNT")
SUBACCOUNT_ORDER_ACTION = hash_string("SUBACCOUNT_ORDER_ACTION")
SUBACCOUNT_EXPIRES_AT = hash_string("SUBACCOUNT_EXPIRES_AT")
GLV_SUPPORTED_MARKET_LIST = hash_string("GLV_SUPPORTED_MARKET_LIST")
MIN_GLV_TOKENS_FOR_FIRST_DEPOSIT = hash_string("MIN_GLV_TOKENS_FOR_FIRST_DEPOSIT")

GLV_SHIFT_MAX_PRICE_IMPACT_FACTOR = hash_string("GLV_SHIFT_MAX_PRICE_IMPACT_FACTOR")
GLV_MAX_MARKET_COUNT = hash_string("GLV_MAX_MARKET_COUNT")
GLV_MAX_MARKET_TOKEN_BALANCE_USD = hash_string("GLV_MAX_MARKET_TOKEN_BALANCE_USD")
GLV_MAX_MARKET_TOKEN_BALANCE_AMOUNT = hash_string("GLV_MAX_MARKET_TOKEN_BALANCE_AMOUNT")
GLV_SHIFT_MIN_INTERVAL = hash_string("GLV_SHIFT_MIN_INTERVAL")
IS_GLV_MARKET_DISABLED = hash_string("IS_GLV_MARKET_DISABLED")

SYNC_CONFIG_FEATURE_DISABLED = hash_string("SYNC_CONFIG_FEATURE_DISABLED")
SYNC_CONFIG_MARKET_DISABLED = hash_string("SYNC_CONFIG_MARKET_DISABLED")
SYNC_CONFIG_PARAMETER_DISABLED = hash_string("SYNC_CONFIG_PARAMETER_DISABLED")
SYNC_CONFIG_MARKET_PARAMETER_DISABLED = hash_string("SYNC_CONFIG_MARKET_PARAMETER_DISABLED")
SYNC_CONFIG_UPDATE_COMPLETED = hash_string("SYNC_CONFIG_UPDATE_COMPLETED")
SYNC_CONFIG_LATEST_UPDATE_ID = hash_string("SYNC_CONFIG_LATEST_UPDATE_ID")

BUYBACK_BATCH_AMOUNT = hash_string("BUYBACK_BATCH_AMOUNT")
BUYBACK_AVAILABLE_FEE_AMOUNT = hash_string("BUYBACK_AVAILABLE_FEE_AMOUNT")
BUYBACK_GMX_FACTOR = hash_string("BUYBACK_GMX_FACTOR")
BUYBACK_MAX_PRICE_IMPACT_FACTOR = hash_string("BUYBACK_MAX_PRICE_IMPACT_FACTOR")
BUYBACK_MAX_PRICE_AGE = hash_string("BUYBACK_MAX_PRICE_AGE")
WITHDRAWABLE_BUYBACK_TOKEN_AMOUNT = hash_string("WITHDRAWABLE_BUYBACK_TOKEN_AMOUNT")

VALID_FROM_TIME = hash_string("VALID_FROM_TIME")


def account_deposit_list_key(account: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [ACCOUNT_DEPOSIT_LIST, account])


def account_withdrawal_list_key(account: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [ACCOUNT_WITHDRAWAL_LIST, account])


def account_shift_list_key(account: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [ACCOUNT_SHIFT_LIST, account])


def account_position_list_key(account: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [ACCOUNT_POSITION_LIST, account])


def account_order_list_key(account: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [ACCOUNT_ORDER_LIST, account])


def subaccount_list_key(account: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [SUBACCOUNT_LIST, account])


def auto_cancel_order_list_key(position_key: Union[str, HexBytes]) -> HexBytes:
    return hash_data(["bytes32", "bytes32"], [AUTO_CANCEL_ORDER_LIST, position_key])


def is_market_disabled_key(market: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [IS_MARKET_DISABLED, market])


def min_market_tokens_for_first_deposit(market: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [MIN_MARKET_TOKENS_FOR_FIRST_DEPOSIT, market])


def create_deposit_feature_disabled_key(contract: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [CREATE_DEPOSIT_FEATURE_DISABLED, contract])


def cancel_deposit_feature_disabled_key(contract: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [CANCEL_DEPOSIT_FEATURE_DISABLED, contract])


def gasless_feature_disabled_key(module: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [GASLESS_FEATURE_DISABLED, module])


def execute_deposit_feature_disabled_key(contract: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [EXECUTE_DEPOSIT_FEATURE_DISABLED, contract])


def create_order_feature_disabled_key(contract: str, order_type: int) -> HexBytes:
    return hash_data(
        ["bytes32", "address", "uint256"],
        [CREATE_ORDER_FEATURE_DISABLED, contract, order_type],
    )


def execute_order_feature_disabled_key(contract: str, order_type: int) -> HexBytes:
    return hash_data(
        ["bytes32", "address", "uint256"],
        [EXECUTE_ORDER_FEATURE_DISABLED, contract, order_type],
    )


def execute_adl_feature_disabled_key(contract: str, order_type: int) -> HexBytes:
    return hash_data(
        ["bytes32", "address", "uint256"],
        [EXECUTE_ADL_FEATURE_DISABLED, contract, order_type],
    )


def update_order_feature_disabled_key(contract: str, order_type: int) -> HexBytes:
    return hash_data(
        ["bytes32", "address", "uint256"],
        [UPDATE_ORDER_FEATURE_DISABLED, contract, order_type],
    )


def cancel_order_feature_disabled_key(contract: str, order_type: int) -> HexBytes:
    return hash_data(
        ["bytes32", "address", "uint256"],
        [CANCEL_ORDER_FEATURE_DISABLED, contract, order_type],
    )


def claimable_fee_amount_key(market: str, token: str) -> HexBytes:
    return hash_data(["bytes32", "address", "address"], [CLAIMABLE_FEE_AMOUNT, market, token])


def claimable_funding_amount_key(market: str, token: str, account: str) -> HexBytes:
    return hash_data(
        ["bytes32", "address", "address", "address"],
        [CLAIMABLE_FUNDING_AMOUNT, market, token, account],
    )


def claimable_collateral_amount_key(market: str, token: str, time_key: int, account: str) -> HexBytes:
    return hash_data(
        ["bytes32", "address", "address", "uint256", "address"],
        [CLAIMABLE_COLLATERAL_AMOUNT, market, token, time_key, account],
    )


def claimable_collateral_factor_key(market: str, token: str, time_key: int) -> HexBytes:
    return hash_data(
        ["bytes32", "address", "address", "uint256"],
        [CLAIMABLE_COLLATERAL_FACTOR, market, token, time_key],
    )


def claimable_collateral_factor_for_account_key(market: str, token: str, time_key: int, account: str) -> HexBytes:
    return hash_data(
        ["bytes32", "address", "address", "uint256", "address"],
        [CLAIMABLE_COLLATERAL_FACTOR, market, token, time_key, account],
    )


def claimable_ui_fee_amount_key(market: str, token: str, ui_fee_receiver: str) -> HexBytes:
    return hash_data(
        ["bytes32", "address", "address", "address"],
        [CLAIMABLE_UI_FEE_AMOUNT, market, token, ui_fee_receiver],
    )


def affiliate_reward_key(market: str, token: str, account: str) -> HexBytes:
    return hash_data(
        ["bytes32", "address", "address", "address"],
        [AFFILIATE_REWARD, market, token, account],
    )


def min_affiliate_reward_factor_key(referral_tier_level: int) -> HexBytes:
    return hash_data(["bytes32", "uint256"], [MIN_AFFILIATE_REWARD_FACTOR, referral_tier_level])


def token_transfer_gas_limit(token: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [TOKEN_TRANSFER_GAS_LIMIT, token])


def price_feed_key(token: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [PRICE_FEED, token])


def price_feed_multiplier_key(token: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [PRICE_FEED_MULTIPLIER, token])


def price_feed_heartbeat_duration_key(token: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [PRICE_FEED_HEARTBEAT_DURATION, token])


def data_stream_id_key(token: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [DATA_STREAM_ID, token])


def data_stream_multiplier_key(token: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [DATA_STREAM_MULTIPLIER, token])


def data_stream_spread_reduction_factor_key(token: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [DATA_STREAM_SPREAD_REDUCTION_FACTOR, token])


def stable_price_key(token: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [STABLE_PRICE, token])


def oracle_type_key(token: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [ORACLE_TYPE, token])


def oracle_timestamp_adjustment_key(provider: str, token: str) -> HexBytes:
    return hash_data(
        ["bytes32", "address", "address"],
        [ORACLE_TIMESTAMP_ADJUSTMENT, provider, token],
    )


def oracle_provider_for_token_key(token: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [ORACLE_PROVIDER_FOR_TOKEN, token])


def open_interest_key(market: str, collateral_token: str, is_long: bool) -> HexBytes:
    return hash_data(
        ["bytes32", "address", "address", "bool"],
        [OPEN_INTEREST, market, collateral_token, is_long],
    )


def open_interest_in_tokens_key(market: str, collateral_token: str, is_long: bool) -> HexBytes:
    return hash_data(
        ["bytes32", "address", "address", "bool"],
        [OPEN_INTEREST_IN_TOKENS, market, collateral_token, is_long],
    )


def is_oracle_provider_enabled_key(provider: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [IS_ORACLE_PROVIDER_ENABLED, provider])


def is_atomic_oracle_provider_key(provider: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [IS_ATOMIC_ORACLE_PROVIDER, provider])


def min_collateral_factor_key(market: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [MIN_COLLATERAL_FACTOR, market])


def min_collateral_factor_for_open_interest_multiplier_key(market: str, is_long: bool) -> HexBytes:
    return hash_data(
        ["bytes32", "address", "bool"],
        [MIN_COLLATERAL_FACTOR_FOR_OPEN_INTEREST_MULTIPLIER, market, is_long],
    )


def reserve_factor_key(market: str, is_long: bool) -> HexBytes:
    return hash_data(["bytes32", "address", "bool"], [RESERVE_FACTOR, market, is_long])


def open_interest_reserve_factor_key(market: str, is_long: bool) -> HexBytes:
    return hash_data(["bytes32", "address", "bool"], [OPEN_INTEREST_RESERVE_FACTOR, market, is_long])


def max_pnl_factor_key(pnl_factor_type: str, market: str, is_long: bool) -> HexBytes:
    return hash_data(
        ["bytes32", "bytes32", "address", "bool"],
        [MAX_PNL_FACTOR, pnl_factor_type, market, is_long],
    )


def min_pnl_factor_after_adl(market: str, is_long: bool) -> HexBytes:
    return hash_data(["bytes32", "address", "bool"], [MIN_PNL_FACTOR_AFTER_ADL, market, is_long])


def collateral_sum_key(market: str, collateral_token: str, is_long: bool) -> HexBytes:
    return hash_data(
        ["bytes32", "address", "address", "bool"],
        [COLLATERAL_SUM, market, collateral_token, is_long],
    )


def pool_amount_key(market: str, token: str) -> HexBytes:
    return hash_data(["bytes32", "address", "address"], [POOL_AMOUNT, market, token])


def max_pool_amount_key(market: str, token: str) -> HexBytes:
    return hash_data(["bytes32", "address", "address"], [MAX_POOL_AMOUNT, market, token])


def max_pool_usd_for_deposit_key(market: str, token: str) -> HexBytes:
    return hash_data(["bytes32", "address", "address"], [MAX_POOL_USD_FOR_DEPOSIT, market, token])


def max_open_interest_key(market: str, is_long: bool) -> HexBytes:
    return hash_data(["bytes32", "address", "bool"], [MAX_OPEN_INTEREST, market, is_long])


def position_impact_pool_amount_key(market: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [POSITION_IMPACT_POOL_AMOUNT, market])


def min_position_impact_pool_amount_key(market: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [MIN_POSITION_IMPACT_POOL_AMOUNT, market])


def position_impact_pool_distribution_rate_key(market: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [POSITION_IMPACT_POOL_DISTRIBUTION_RATE, market])


def position_impact_pool_distributed_at_key(market: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [POSITION_IMPACT_POOL_DISTRIBUTED_AT, market])


def swap_impact_pool_amount_key(market: str, token: str) -> HexBytes:
    return hash_data(["bytes32", "address", "address"], [SWAP_IMPACT_POOL_AMOUNT, market, token])


def swap_fee_factor_key(market: str, for_positive_impact: bool) -> HexBytes:
    return hash_data(["bytes32", "address", "bool"], [SWAP_FEE_FACTOR, market, for_positive_impact])


def deposit_fee_factor_key(market: str, for_positive_impact: bool) -> HexBytes:
    return hash_data(
        ["bytes32", "address", "bool"],
        [DEPOSIT_FEE_FACTOR, market, for_positive_impact],
    )


def withdrawal_fee_factor_key(market: str, for_positive_impact: bool) -> HexBytes:
    return hash_data(
        ["bytes32", "address", "bool"],
        [WITHDRAWAL_FEE_FACTOR, market, for_positive_impact],
    )


def atomic_swap_fee_factor_key(market: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [ATOMIC_SWAP_FEE_FACTOR, market])


def swap_impact_factor_key(market: str, is_positive: bool) -> HexBytes:
    return hash_data(["bytes32", "address", "bool"], [SWAP_IMPACT_FACTOR, market, is_positive])


def swap_impact_exponent_factor_key(market: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [SWAP_IMPACT_EXPONENT_FACTOR, market])


def position_impact_factor_key(market: str, is_positive: bool) -> HexBytes:
    return hash_data(["bytes32", "address", "bool"], [POSITION_IMPACT_FACTOR, market, is_positive])


def position_impact_exponent_factor_key(market: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [POSITION_IMPACT_EXPONENT_FACTOR, market])


def max_position_impact_factor_key(market: str, is_positive: bool) -> HexBytes:
    return hash_data(
        ["bytes32", "address", "bool"],
        [MAX_POSITION_IMPACT_FACTOR, market, is_positive],
    )


def max_position_impact_factor_for_liquidations_key(market: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [MAX_POSITION_IMPACT_FACTOR_FOR_LIQUIDATIONS, market])


def position_fee_factor_key(market: str, for_positive_impact: bool) -> HexBytes:
    return hash_data(
        ["bytes32", "address", "bool"],
        [POSITION_FEE_FACTOR, market, for_positive_impact],
    )


def pro_trader_tier_key(account: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [PRO_TRADER_TIER, account])


def pro_discount_factor_key(pro_tier: int) -> HexBytes:
    return hash_data(["bytes32", "uint256"], [PRO_DISCOUNT_FACTOR, pro_tier])


def liquidation_fee_factor_key(market: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [LIQUIDATION_FEE_FACTOR, market])


def latest_adl_block_key(market: str, is_long: bool) -> HexBytes:
    return hash_data(["bytes32", "address", "bool"], [LATEST_ADL_BLOCK, market, is_long])


def is_adl_enabled_key(market: str, is_long: bool) -> HexBytes:
    return hash_data(["bytes32", "address", "bool"], [IS_ADL_ENABLED, market, is_long])


def funding_factor_key(market: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [FUNDING_FACTOR, market])


def funding_exponent_factor_key(market: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [FUNDING_EXPONENT_FACTOR, market])


def saved_funding_factor_per_second_key(market: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [SAVED_FUNDING_FACTOR_PER_SECOND, market])


def funding_increase_factor_per_second_key(market: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [FUNDING_INCREASE_FACTOR_PER_SECOND, market])


def funding_decrease_factor_per_second_key(market: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [FUNDING_DECREASE_FACTOR_PER_SECOND, market])


def min_funding_factor_per_second_key(market: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [MIN_FUNDING_FACTOR_PER_SECOND, market])


def max_funding_factor_per_second_key(market: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [MAX_FUNDING_FACTOR_PER_SECOND, market])


def threshold_for_stable_funding_key(market: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [THRESHOLD_FOR_STABLE_FUNDING, market])


def threshold_for_decrease_funding_key(market: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [THRESHOLD_FOR_DECREASE_FUNDING, market])


def funding_fee_amount_per_size_key(market: str, collateral_token: str, is_long: bool) -> HexBytes:
    return hash_data(
        ["bytes32", "address", "address", "bool"],
        [FUNDING_FEE_AMOUNT_PER_SIZE, market, collateral_token, is_long],
    )


def claimable_funding_amount_per_size_key(market: str, collateral_token: str, is_long: bool) -> HexBytes:
    return hash_data(
        ["bytes32", "address", "address", "bool"],
        [CLAIMABLE_FUNDING_AMOUNT_PER_SIZE, market, collateral_token, is_long],
    )


def funding_updated_at_key(market: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [FUNDING_UPDATED_AT, market])


def borrowing_factor_key(market: str, is_long: bool) -> HexBytes:
    return hash_data(["bytes32", "address", "bool"], [BORROWING_FACTOR, market, is_long])


def borrowing_exponent_factor_key(market: str, is_long: bool) -> HexBytes:
    return hash_data(["bytes32", "address", "bool"], [BORROWING_EXPONENT_FACTOR, market, is_long])


def deposit_gas_limit_key() -> HexBytes:
    return DEPOSIT_GAS_LIMIT


def withdrawal_gas_limit_key() -> HexBytes:
    return WITHDRAWAL_GAS_LIMIT


def shift_gas_limit_key() -> HexBytes:
    return SHIFT_GAS_LIMIT


def single_swap_gas_limit_key() -> HexBytes:
    return SINGLE_SWAP_GAS_LIMIT


def increase_order_gas_limit_key() -> HexBytes:
    return INCREASE_ORDER_GAS_LIMIT


def decrease_order_gas_limit_key() -> HexBytes:
    return DECREASE_ORDER_GAS_LIMIT


def swap_order_gas_limit_key() -> HexBytes:
    return SWAP_ORDER_GAS_LIMIT


def glv_deposit_gas_limit_key() -> HexBytes:
    return GLV_DEPOSIT_GAS_LIMIT


def glv_withdrawal_gas_limit_key() -> HexBytes:
    return GLV_WITHDRAWAL_GAS_LIMIT


def glv_shift_gas_limit_key() -> HexBytes:
    return GLV_SHIFT_GAS_LIMIT


def glv_per_market_gas_limit_key() -> HexBytes:
    return GLV_PER_MARKET_GAS_LIMIT


def cumulative_borrowing_factor_key(market: str, is_long: bool) -> HexBytes:
    return hash_data(["bytes32", "address", "bool"], [CUMULATIVE_BORROWING_FACTOR, market, is_long])


def cumulative_borrowing_factor_updated_at_key(market: str, is_long: bool) -> HexBytes:
    return hash_data(
        ["bytes32", "address", "bool"],
        [CUMULATIVE_BORROWING_FACTOR_UPDATED_AT, market, is_long],
    )


def virtual_token_id_key(token: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [VIRTUAL_TOKEN_ID, token])


def virtual_market_id_key(market: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [VIRTUAL_MARKET_ID, market])


def virtual_inventory_for_swaps_key(virtual_market_id: str, is_long_token: bool) -> HexBytes:
    return hash_data(
        ["bytes32", "bytes32", "bool"],
        [VIRTUAL_INVENTORY_FOR_SWAPS, virtual_market_id, is_long_token],
    )


def virtual_inventory_for_positions_key(virtual_token_id: str) -> HexBytes:
    return hash_data(["bytes32", "bytes32"], [VIRTUAL_INVENTORY_FOR_POSITIONS, virtual_token_id])


def max_allowed_subaccount_action_count_key(account: str, subaccount: str, action_type: str) -> HexBytes:
    return hash_data(
        ["bytes32", "address", "address", "bytes32"],
        [MAX_ALLOWED_SUBACCOUNT_ACTION_COUNT, account, subaccount, action_type],
    )


def subaccount_expires_at_key(account: str, subaccount: str, action_type: str) -> HexBytes:
    return hash_data(
        ["bytes32", "address", "address", "bytes32"],
        [SUBACCOUNT_EXPIRES_AT, account, subaccount, action_type],
    )


def subaccount_action_count_key(account: str, subaccount: str, action_type: str) -> HexBytes:
    return hash_data(
        ["bytes32", "address", "address", "bytes32"],
        [SUBACCOUNT_ACTION_COUNT, account, subaccount, action_type],
    )


def subaccount_auto_top_up_amount_key(account: str, subaccount: str) -> HexBytes:
    return hash_data(
        ["bytes32", "address", "address"],
        [SUBACCOUNT_AUTO_TOP_UP_AMOUNT, account, subaccount],
    )


def glv_supported_market_list_key(glv: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [GLV_SUPPORTED_MARKET_LIST, glv])


def min_glv_tokens_for_first_glv_deposit_key(glv: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [MIN_GLV_TOKENS_FOR_FIRST_DEPOSIT, glv])


def account_glv_deposit_list_key(account: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [ACCOUNT_GLV_DEPOSIT_LIST, account])


def account_glv_withdrawal_list_key(account: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [ACCOUNT_GLV_WITHDRAWAL_LIST, account])


def glv_max_market_token_balance_usd_key(glv: str, market: str) -> HexBytes:
    return hash_data(
        ["bytes32", "address", "address"],
        [GLV_MAX_MARKET_TOKEN_BALANCE_USD, glv, market],
    )


def glv_max_market_token_balance_amount_key(glv: str, market: str) -> HexBytes:
    return hash_data(
        ["bytes32", "address", "address"],
        [GLV_MAX_MARKET_TOKEN_BALANCE_AMOUNT, glv, market],
    )


def glv_shift_min_interval_key(glv: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [GLV_SHIFT_MIN_INTERVAL, glv])


def glv_shift_max_price_impact_factor_key(glv: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [GLV_SHIFT_MAX_PRICE_IMPACT_FACTOR, glv])


def is_glv_market_disabled_key(glv: str, market: str) -> HexBytes:
    return hash_data(["bytes32", "address", "address"], [IS_GLV_MARKET_DISABLED, glv, market])


def sync_config_feature_disabled_key(contract: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [SYNC_CONFIG_FEATURE_DISABLED, contract])


def sync_config_market_disabled_key(market: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [SYNC_CONFIG_MARKET_DISABLED, market])


def sync_config_parameter_disabled_key(parameter: str) -> HexBytes:
    return hash_data(["bytes32", "string"], [SYNC_CONFIG_PARAMETER_DISABLED, parameter])


def sync_config_market_parameter_disabled_key(market: str, parameter: str) -> HexBytes:
    return hash_data(
        ["bytes32", "address", "string"],
        [SYNC_CONFIG_MARKET_PARAMETER_DISABLED, market, parameter],
    )


def sync_config_update_completed_key(update_id: int) -> HexBytes:
    return hash_data(["bytes32", "uint256"], [SYNC_CONFIG_UPDATE_COMPLETED, update_id])


def sync_config_latest_update_id_key() -> HexBytes:
    return SYNC_CONFIG_LATEST_UPDATE_ID


def buyback_batch_amount_key(token: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [BUYBACK_BATCH_AMOUNT, token])


def buyback_available_fee_amount_key(fee_token: str, swap_token: str) -> HexBytes:
    return hash_data(
        ["bytes32", "address", "address"],
        [BUYBACK_AVAILABLE_FEE_AMOUNT, fee_token, swap_token],
    )


def buyback_gmx_factor_key(version: int) -> HexBytes:
    return hash_data(["bytes32", "uint256"], [BUYBACK_GMX_FACTOR, version])


def buyback_max_price_impact_factor_key(token: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [BUYBACK_MAX_PRICE_IMPACT_FACTOR, token])


def withdrawable_buyback_token_amount_key(buyback_token: str) -> HexBytes:
    return hash_data(["bytes32", "address"], [WITHDRAWABLE_BUYBACK_TOKEN_AMOUNT, buyback_token])
