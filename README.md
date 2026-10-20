Assignment 1 – Retail Data Pipeline
What does this project do?
This Python program reads retail transactions from a CSV file, checks for mistakes, and prints a summary of sales across different store branches.

It can show total sales, estimated taxes, profit before overhead, the best-performing branch, customer tiers, and how many rows passed validation. Invalid rows are rejected instead of being included in the calculations.
How to run it
1. Open the Assignment-1 folder in VS Code.
2. Open the terminal (Terminal → New Terminal).
3. Run:
   python main.py
The results will appear in the terminal. This command uses the included data/transactions.csv file.

You only need Python installed. No extra packages are required.
How to use your own CSV file
Option A: Replace the sample data
1. Open the data folder in VS Code.
2. Replace transactions.csv with your own CSV file using the same filename.
3. Run python main.py again.
Option B: Keep the sample data and use a different file
1. Put your CSV file inside the data folder (for example, my_sales.csv).
2. Run:
   python main.py data/my_sales.csv
You can also use a CSV from another folder by giving its path. Put quotation marks around paths containing spaces.
Required CSV columns
Your CSV must have these column names in its first row, in any order:
transaction_id,branch_id,transaction_date,customer_tier,item_count,revenue,cost,region,active
T001,ON-101,2026-10-01,Gold,3,149.99,90.00,ON,True
T002,AB-201,2026-10-02,Silver,1,59.50,30.00,AB,True
Rules for the data:
- Dates must be YYYY-MM-DD (example: 2026-10-01).
- Customer tiers must be Bronze, Silver, Gold, or Platinum.
- Regions must be ON, AB, or BC (the regions currently supported by the code).
- item_count must be a positive whole number.
- revenue and cost must be nonnegative numbers without $ signs.
- active can be True/False, Yes/No, or 1/0.
- Every row needs a transaction ID and branch ID.
The program ignores capitalization differences in customer tiers and regions. If a row has invalid data, the report counts it as rejected. Valid but inactive transactions count toward data quality, but not sales totals.

How to run the tests
In the VS Code terminal, enter:
python -m unittest discover -s tests -v
Project contribution
Created by: David Lambert