# CBP & ICE Contract Spending Dashboard

An interactive dashboard for tracking U.S. Customs and Border Protection (CBP) and U.S. Immigration and Customs Enforcement (ICE) contract spending data from USAspending.gov.

**Live Dashboard:** https://wrags81.github.io/cbp-ice-dashboard/

## Features

- **Multi-Fiscal Year Support**: View contract data from FY2021 through FY2026
- **Trump Administration Filter**: Quick filter for transactions since January 20, 2025
- **Interactive Charts**:
  - Monthly spending trends
  - Agency comparison (CBP vs ICE)
  - Top 10 recipients by agency
  - Top 10 Product/Service Categories (PSC)
  - Top 10 Industries (NAICS)
- **Sortable Data Table**: Click column headers to sort by Agency, Recipient, Amount, Date, PSC, or NAICS
- **Search Functionality**: Filter transactions by recipient name or description
- **Direct Links**: Click any transaction to view full details on USAspending.gov
- **CSV Export**: Download filtered data for further analysis

## Data Source

All data is fetched from the [USAspending.gov API](https://api.usaspending.gov/), specifically the `/api/v2/search/spending_by_transaction/` endpoint. The dashboard tracks federal contract obligations (award type codes A, B, C, D) for:

- **CBP**: U.S. Customs and Border Protection
- **ICE**: U.S. Immigration and Customs Enforcement

## Project Structure

```
cbp-ice-dashboard/
├── index.html              # Main dashboard (HTML, CSS, JavaScript)
├── fetch_and_build.py      # Python script to fetch data from USAspending API
├── data/                   # CSV data files
│   ├── CBP_ICE_FY2021_Contract_Obligations.csv
│   ├── CBP_ICE_FY2022_Contract_Obligations.csv
│   ├── CBP_ICE_FY2023_Contract_Obligations.csv
│   ├── CBP_ICE_FY2024_Contract_Obligations.csv
│   ├── CBP_ICE_FY2025_Contract_Obligations.csv
│   └── CBP_ICE_FY2026_Contract_Obligations.csv
└── README.md
```

## How It Works

### Data Fetching (Python)

The `fetch_and_build.py` script:

1. Queries the USAspending.gov API for CBP and ICE contract transactions
2. Paginates through all results (100 transactions per page)
3. Extracts key fields: Award ID, Recipient, Amount, Date, PSC, NAICS, Description
4. Includes the `generated_internal_id` field for linking to USAspending.gov award pages
5. Saves data to CSV files organized by fiscal year

### Dashboard (HTML/JavaScript)

The `index.html` file is a self-contained single-page application that:

1. Loads CSV data files using [PapaParse](https://www.papaparse.com/)
2. Renders interactive charts using [Chart.js](https://www.chartjs.org/)
3. Provides client-side filtering, sorting, and search
4. Generates USAspending.gov links using the Generated Award ID field

## Updating the Data

### Fetch a specific fiscal year:
```bash
python3 fetch_and_build.py 2026
```

### Fetch multiple years:
```bash
python3 fetch_and_build.py 2026 2025 2024
```

### Fetch all years (FY2021-2026):
```bash
python3 fetch_and_build.py all
```

After fetching, commit and push to update the live dashboard:
```bash
git add -A
git commit -m "Update spending data"
git push
```

## Technical Details

### API Fields Retrieved

| Field | Description |
|-------|-------------|
| Award ID | Contract/award identifier (PIID) |
| Recipient Name | Contractor/vendor name |
| Transaction Amount | Federal action obligation amount |
| Action Date | Date of the transaction |
| Mod | Modification number |
| product_or_service_description | PSC description |
| naics_description | NAICS industry description |
| Transaction Description | Detailed description of the contract action |
| generated_internal_id | Unique ID for USAspending.gov award page links |

### Fiscal Year Date Ranges

| Fiscal Year | Start Date | End Date |
|-------------|------------|----------|
| FY2021 | 2020-10-01 | 2021-09-30 |
| FY2022 | 2021-10-01 | 2022-09-30 |
| FY2023 | 2022-10-01 | 2023-09-30 |
| FY2024 | 2023-10-01 | 2024-09-30 |
| FY2025 | 2024-10-01 | 2025-09-30 |
| FY2026 | 2025-10-01 | 2026-09-30 |

### Dependencies

**Python (for data fetching):**
- `requests` - HTTP library for API calls
- `csv` - CSV file handling (standard library)

**JavaScript (loaded via CDN):**
- [Chart.js](https://www.chartjs.org/) - Charting library
- [PapaParse](https://www.papaparse.com/) - CSV parsing

## Hosting

The dashboard is hosted on GitHub Pages. Any push to the `main` branch automatically updates the live site.

## License

This project uses publicly available federal spending data from USAspending.gov.
