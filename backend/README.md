# Backend Module Documentation

## Core Modules

### app.py
Main Flask application entrypoint.

**Key Components:**
- Flask API initialization
- Route handlers for all endpoints
- Upload session management
- Error handling and logging

**Key Functions:**
- `health_check()` - Server health status
- `upload_csv()` - File upload and normalization
- `product_search()` - Product search within uploads
- `forecast()` - Prophet + XGBoost ensemble forecasting
- `analyze_patterns()` - Historical analysis and patterns
- `festival_impact()` - Upcoming festival forecasting
- `ai_insights()` - AI-generated business insights

### analytics_engine.py
Data normalization, analysis, and forecasting engine.

**Key Functions:**
- `prepare_uploaded_dataframe()` - Normalize and standardize uploaded data
- `generate_forecast()` - Prophet time-series forecasting
- `analyze_dataset()` - Historical trend analysis
- `search_products()` - Product search and ranking
- `filter_dataset_by_product()` - Product-specific filtering

**Key Classes:**
- `UploadStore` - In-memory session storage with TTL
- `ProductIdentityResolver` - Product name/ID normalization

### ensemble_engine.py
XGBoost model training and ensemble forecasting.

**Key Functions:**
- `train_user_model()` - Train per-upload XGBoost models
- `predict_ensemble()` - Combine Prophet + XGBoost predictions
- `_build_scope_series()` - Prepare data for training

**Key Constants:**
- `AGGREGATE_SCOPE` - Store-level forecasting
- `PRODUCT_SCOPE` - Product-level forecasting

### market_holidays.py
Multi-country holiday calendar and festival awareness.

**Key Classes:**
- `MarketFestivalsCalendar` - Holiday detection and impact scoring

**Key Functions:**
- `get_calendar()` - Get or create calendar for country code

### ai_engine.py
Groq-powered AI insights generation.

**Key Functions:**
- `get_ai_insight()` - Generate multilingual business briefs
- `build_prompt()` - Construct AI prompt from analysis data

## Utility Modules

### config.py
Centralized configuration management from environment variables.

**Key Classes:**
- `AppConfig` - Root configuration object
- `FlaskConfig` - Flask-specific settings
- `UploadConfig` - Upload session settings
- `AIConfig` - AI service settings

**Key Functions:**
- `get_config()` - Get singleton configuration instance

### logger.py
Structured logging utilities.

**Key Functions:**
- `get_logger()` - Get logger instance for a module

### cache.py
TTL-based caching decorator for expensive operations.

**Key Functions:**
- `@cached()` - Decorator for caching function results

### errors.py
Error handling and standardized error responses.

**Key Functions:**
- `create_error_response()` - Create standardized error responses
- `handle_api_error()` - Handle and log API errors
- `log_warning()` - Log warnings with context

### validation.py
Input validation utilities.

**Key Functions:**
- `validate_required_fields()` - Check required fields present
- `validate_positive()` - Validate positive numeric values
- `validate_in_choices()` - Validate enum-like values

## Archived Modules

See `ARCHIVED_SCRIPTS.md` for information about offline training scripts.

## Environment Variables

See `.env.example` for configuration options.

## Performance Considerations

1. **Caching** - Calendar objects are cached after first load
2. **Upload Sessions** - Expired after configurable TTL (default: 90 minutes)
3. **API Timeouts** - Configurable per service (default: 30 seconds)
4. **Model Storage** - Per-upload XGBoost models stored as JSON files

## Common Tasks

### Adding a New API Endpoint

1. Create handler function in `app.py`
2. Add `@app.route()` decorator
3. Use `config` and `logger` for settings and logging
4. Return JSON response using `jsonify()`
5. Handle errors with `handle_api_error()` helper

### Adding a New Market

1. Update market code support in `frontend/src/App.jsx`
2. Verify country code is supported by `holidays` library
3. Calendar is automatically created in `market_holidays.py`

### Debugging API Issues

1. Check log output from `logger` calls
2. Use `FLASK_DEBUG=true` for verbose errors
3. Check `.env` configuration
4. Verify upload sessions haven't expired (90 min default)
