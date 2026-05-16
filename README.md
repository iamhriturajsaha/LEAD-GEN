# Simple Lead Generation Automation

This project is a Python automation script that collects lead data from a public API, performs data cleaning, and stores the organized data in an Excel file.

## Features
- **Data Collection**: Fetches 30 users' data from the DummyJSON public API.
- **Data Extraction**: Extracts Name, Email, LinkedIn (generated), Company, and Location.
- **Data Cleaning**: Uses `pandas` to remove duplicates and handle missing values.
- **Bonus Features**:
  - *API Integration*: Uses `requests` to fetch data from a REST API.
  - *Email Format Generation*: Intentionally missing emails are auto-generated based on the person's name and company.
  - *Automation Trigger*: Uses the `schedule` library to demonstrate how to run the script automatically on a schedule.

## Setup Instructions
1. Ensure you have Python installed.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the script:
   ```bash
   python lead_gen.py
   ```
4. Check the generated `leads_output.xlsx` file in the same directory.

## Evaluation Approach
- **Logic**: Use an API to gather reliable dummy data. Inject artificial dirty data (duplicates and missing emails) to demonstrate robust cleaning logic.
- **Tools Used**: `requests` for data collection, `pandas` for data manipulation, `openpyxl` for Excel generation, and `schedule` for the automation trigger.
