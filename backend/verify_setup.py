"""
Quick setup verification script.
Run this to verify all dependencies are installed correctly.
"""

import sys


def check_imports():
    """Check if all required packages can be imported."""
    packages = {
        "flask": "Flask",
        "flask_cors": "Flask-CORS",
        "dotenv": "python-dotenv",
        "pandas": "Pandas",
        "numpy": "NumPy",
        "prophet": "Prophet",
        "sklearn": "Scikit-learn",
        "xgboost": "XGBoost",
        "groq": "Groq",
        "holidays": "holidays",
        "openpyxl": "openpyxl",
        "matplotlib": "Matplotlib",
        "seaborn": "Seaborn",
        "pickle": "Pickle (built-in)",
    }

    print("=" * 60)
    print("CHECKING DEPENDENCIES")
    print("=" * 60)

    all_good = True
    for module, name in packages.items():
        try:
            __import__(module)
            print(f"[OK] {name:20} - OK")
        except ImportError:
            print(f"[MISSING] {name:20} - MISSING")
            all_good = False

    print("\n" + "=" * 60)
    if all_good:
        print("[OK] ALL DEPENDENCIES INSTALLED SUCCESSFULLY!")
        print("=" * 60)
        print("\nNEXT STEPS:")
        print("1. Add Train.csv to the data/ folder")
        print("2. Run: cd backend && python model.py")
        print("3. Run: cd backend && python app.py")
        print("4. In another terminal: cd frontend && npm run dev")
        print("5. Open http://localhost:5173 in your browser")
        return True

    print("[ERROR] SOME DEPENDENCIES ARE MISSING")
    print("=" * 60)
    print("\nRun: pip install -r requirements.txt")
    return False


if __name__ == "__main__":
    success = check_imports()
    sys.exit(0 if success else 1)
