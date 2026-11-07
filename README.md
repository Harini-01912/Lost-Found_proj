# Smart Lost Item Recovery and Matching System

A small Flask application for reporting lost and found items. Reports are stored
in SQLite, and a built-in text similarity algorithm ranks possible matches.

## Requirements

- Python 3.9 or newer
- pip

## Run in VS Code (Windows PowerShell)

1. Open this folder in VS Code.
2. Open **Terminal → New Terminal**.
3. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use `.\.venv\Scripts\python.exe` in place
   of `python` in the following commands.

4. Install Flask:

   ```powershell
   python -m pip install -r requirements.txt
   ```

5. Start the application:

   ```powershell
   python app.py
   ```

6. Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in a browser.

The SQLite database is created automatically at `instance/lost_found.db` the
first time the application starts. Stop the local server with **Ctrl+C**.

## Features

- Home page with recent lost and found reports.
- Validated forms for lost and found items.
- Ranked possible matches after either type of report is submitted.
- Dashboard with all reports and cross-matched item pairs.
- Item detail pages linked from recent reports, match results, and dashboard.
- Similarity compares item name, category, description, and location. Results
  below 30% are not shown as suitable matches.

## Run the tests

```powershell
python -m unittest discover -s tests
```
