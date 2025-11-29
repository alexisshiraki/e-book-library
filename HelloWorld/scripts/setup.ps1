# One-line setup wrapper for the HelloWorld project
# Run this from the repository root in PowerShell to create and activate the venv,
# upgrade pip, and install dependencies.

python -m venv .venv; .\.venv\Scripts\Activate.ps1; python -m pip install --upgrade pip; pip install -r requirements.txt
