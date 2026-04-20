"""
Application constants and magic numbers in one place.
Improves maintainability and makes tuning easier.
"""

# Request and Timeout Constants
DEFAULT_REQUEST_TIMEOUT = 30  # seconds
DEFAULT_AI_TIMEOUT = 45  # seconds
MAX_UPLOAD_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

# Session Management Constants
DEFAULT_UPLOAD_TTL_MINUTES = 90
DEFAULT_MAX_UPLOAD_SESSIONS = 25
MIN_UPLOAD_TTL_MINUTES = 5
MAX_UPLOAD_TTL_MINUTES = 1440  # 24 hours
SESSION_CLEANUP_INTERVAL = 300  # seconds

# Forecasting Constants
DEFAULT_FORECAST_PERIODS = {
    'daily': 30,
    'weekly': 12,
    'monthly': 12,
    'yearly': 3,
}

# Prophet Configuration Constants
PROPHET_SEASONALITY_PRIORS = {
    'yearly_seasonality_prior_scale': 10.0,
    'seasonality_prior_scale': 10.0,
    'seasonality_mode': 'additive',
}

PROPHET_INTERVAL_WIDTH = 0.85  # 85% confidence interval

# XGBoost Configuration Constants
XGBOOST_PARAMS = {
    'max_depth': 5,
    'learning_rate': 0.1,
    'n_estimators': 100,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
}

XGBOOST_MIN_ROWS = 50  # Minimum data points to train XGBoost

# Ensemble Weighting Logic
ENSEMBLE_WEIGHTS = {
    'low_data': (0.8, 0.2),    # < 100 rows: 80% Prophet, 20% XGBoost
    'medium_data': (0.5, 0.5),  # 100-300 rows: 50/50 split
    'high_data': (0.2, 0.8),    # > 300 rows: 20% Prophet, 80% XGBoost
}

ENSEMBLE_CONFIDENCE_THRESHOLD = 0.7  # Threshold for "High" confidence

# Data Processing Constants
PRODUCT_SEARCH_LIMIT = 25  # Max products to return in search
DEFAULT_PRODUCT_SEARCH_LIMIT = 10
PRODUCT_SEARCH_MIN_RESULTS = 1
PRODUCT_SEARCH_MAX_RESULTS = 100

# Trend Analysis Constants
HISTORY_LIMIT_DAYS = 180  # Default historical window
TREND_COMPARISON_WINDOW_DAILY = 7
TREND_COMPARISON_WINDOW_WEEKLY = 4
TREND_COMPARISON_WINDOW_MONTHLY = 3
TREND_COMPARISON_WINDOW_YEARLY = 1

# Festival Impact Constants
DEFAULT_NO_FESTIVAL_DISTANCE = 61  # days
FESTIVAL_LOOKAHEAD_DAYS = 60  # days to look ahead for festivals

# API Response Constants
API_VERSION = "3.0"
API_TIMEOUT_STATUS_CODE = 408
API_CONFLICT_STATUS_CODE = 409

# Logging Constants
LOG_LEVEL_DEVELOPMENT = "DEBUG"
LOG_LEVEL_PRODUCTION = "INFO"
MAX_LOG_FILE_SIZE = 10 * 1024 * 1024  # 10 MB per log file

# Cache Constants
DEFAULT_CACHE_TTL = 300  # 5 minutes
CALENDAR_CACHE_TTL = 3600  # 1 hour (calendars don't change often)
MAX_CACHE_SIZE = 128

# AI Configuration Constants
DEFAULT_AI_MODEL = "llama-3.3-70b-versatile"
DEFAULT_AI_TEMPERATURE = 0.25  # Lower = more deterministic
DEFAULT_AI_MAX_TOKENS = 420
SUPPORTED_AI_LANGUAGES = [
    "English",
    "Hindi",
    "Marathi",
    "Bengali",
    "Telugu",
    "Tamil",
    "Malayalam",
]

# Market/Country Constants
SUPPORTED_MARKETS = {
    'IN': 'India',
    'US': 'United States',
    'GB': 'United Kingdom',
    'AE': 'UAE',
    'AU': 'Australia',
    'CA': 'Canada',
}

# Validation Constants
MIN_FORECAST_PERIODS = 1
MAX_FORECAST_PERIODS = 1000
MIN_PRODUCT_NAME_LENGTH = 1
MAX_PRODUCT_NAME_LENGTH = 500
