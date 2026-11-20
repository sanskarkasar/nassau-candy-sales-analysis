# Nassau Candy Sales Analytics Dashboard

Interactive dashboard for the Nassau Candy Distributor dataset.

## Features
- Sales, gross profit, margin, orders, and customer KPIs
- Sales by region and division
- Monthly sales trend
- Profitability views
- Top products and customers
- Shipping-date data-quality investigation
- Region, division, and ship-mode filters
- Filtered CSV export

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```
Upload the CSV file in the dashboard when prompted.

## Deployment
Deploy with Streamlit Community Cloud; choose `app.py` as the main file.

## Data limitation
Shipping duration is investigated for data quality only; verify the original dates before interpreting delivery performance.

## Project scope
Sales analytics and shipping-date quality investigation. Factory relocation optimization is not implemented.
