# Backend Data Notes

This folder contains archived training data, reference datasets, and offline-processing inputs. The live upload-based API does not require these files for normal forecasting requests.

## Main datasets

### 1. BigMart reference data
- `Train.csv`
- `Test.csv`

These files belong to the older BigMart-style training workflow and are mainly relevant to `backend/model.py`.

### 2. Unified offline training data
- `unified_training_data.csv`

This engineered dataset is produced by `backend/unified_data_processor.py` and is used by the archived integrated model workflow.

### 3. Diwali sales reference data
- `diwali_sales/Diwali Sales Data.csv`

This dataset contributes festival-oriented signals for offline experimentation and analysis.

### 4. Indian retail reference data
- `indian_retail/INDIA_RETAIL_DATA.xlsx`

This dataset provides dated retail rows that are useful for offline exploration and training experiments.

### 5. Raw archive files
- `archive.zip`
- `Diwali Sales.zip`
- `Holidays dataset.zip`
- `indian retail.zip`

These remain in the repository for provenance and manual reuse.

## Runtime distinction

- Live API uploads come from user-provided CSV or XLSX files.
- Upload parsing and normalization happen in `backend/analytics_engine.py`.
- Holiday enrichment for the running app comes from `backend/market_holidays.py` and the `holidays` library.
- Archived datasets in this folder are not loaded automatically for the standard `/api/upload-csv` to `/api/forecast` flow.

## Related files

- `backend/explore_datasets.py`
- `backend/unified_data_processor.py`
- `backend/train_integrated_model.py`
- `backend/ARCHIVED_SCRIPTS.md`
