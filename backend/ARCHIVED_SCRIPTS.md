# Archived Training Scripts

These scripts are part of the legacy offline training pipeline and are **NOT used** by the live Flask API.

## Files

- **model.py** - Legacy BigMart training pipeline (archived)  
- **train_integrated_model.py** - Integrated model training on unified dataset (archived)
- **unified_data_processor.py** - Data preparation for offline training (archived)  
- **explore_datasets.py** - Dataset inspection utility (archived)

## Why They're Here

These scripts remain in the repository for:
- Reference and documentation of the training process
- Offline experimentation and research
- Historical artifact preservation
- Potential future retraining scenarios

## Live Application

The live Flask API (`app.py`) uses **upload-driven runtime forecasting** instead:
- Per-upload Prophet + XGBoost ensemble
- No dependency on pre-trained model bundles
- Models are trained dynamically on each uploaded dataset
- Upload sessions are stored in memory only
- Session-specific XGBoost JSON files are written to `backend/models/`

## Archived Artifacts

- `models/sales_model.pkl` belongs to the older BigMart-style phase.
- `models/integrated_sales_model.pkl` belongs to the integrated offline training workflow.
- `unified_data_processor.py` can assign synthetic dates when combining source datasets, so its output should be described as engineered training data rather than pure operational history.

## Running Archived Scripts

If you need to rebuild offline models:

```bash
cd backend
python unified_data_processor.py   # Process datasets
python train_integrated_model.py   # Train integrated model
python model.py                    # Train BigMart model  
python explore_datasets.py         # Inspect datasets
```

**Note:** These require the full training data to be present and are for offline analysis only.
