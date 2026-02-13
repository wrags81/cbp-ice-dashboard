#!/usr/bin/env python3
"""
Fetch CBP & ICE contract data for multiple fiscal years
Saves data to CSV files for the dashboard
"""

import requests
import csv
import os
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")

# Fiscal year configurations
FISCAL_YEARS = {
    2026: {"start": "2025-10-01", "end": "2026-09-30"},
    2025: {"start": "2024-10-01", "end": "2025-09-30"},
    2024: {"start": "2023-10-01", "end": "2024-09-30"},
    2023: {"start": "2022-10-01", "end": "2023-09-30"},
    2022: {"start": "2021-10-01", "end": "2022-09-30"},
    2021: {"start": "2020-10-01", "end": "2021-09-30"},
}

AGENCIES = [
    ("CBP", "U.S. Customs and Border Protection"),
    ("ICE", "U.S. Immigration and Customs Enforcement"),
]


def fetch_transactions(agency_name, agency_abbrev, fy_start, fy_end):
    """Fetch all transaction data for an agency and fiscal year"""
    url = "https://api.usaspending.gov/api/v2/search/spending_by_transaction/"
    all_results = []
    page = 1

    while True:
        payload = {
            "filters": {
                "agencies": [{
                    "type": "awarding",
                    "tier": "subtier",
                    "name": agency_name
                }],
                "time_period": [{
                    "start_date": fy_start,
                    "end_date": fy_end
                }],
                "award_type_codes": ["A", "B", "C", "D"]
            },
            "fields": [
                "Award ID", "Recipient Name", "Transaction Amount",
                "Action Date", "Awarding Sub Agency", "Transaction Description",
                "Mod", "product_or_service_description", "naics_description"
            ],
            "page": page,
            "limit": 100,
            "sort": "Transaction Amount",
            "order": "desc"
        }

        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"    Error on page {page}: {e}")
            break

        results = data.get("results", [])
        all_results.extend(results)
        print(f"    Page {page}: {len(results)} transactions (total: {len(all_results)})")

        if not data.get("page_metadata", {}).get("hasNext", False) or len(results) == 0:
            break
        page += 1

    return all_results


def save_to_csv(cbp_data, ice_data, fiscal_year):
    """Save data to CSV file"""
    csv_path = os.path.join(DATA_DIR, f"CBP_ICE_FY{fiscal_year}_Contract_Obligations.csv")

    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Agency", "Award ID", "Recipient Name", "Federal Action Obligation",
            "Action Date", "Modification", "Product/Service Description",
            "NAICS Description", "Transaction Description"
        ])

        for t in cbp_data:
            writer.writerow([
                "CBP", t.get("Award ID", ""), t.get("Recipient Name", ""),
                t.get("Transaction Amount", 0), t.get("Action Date", ""),
                t.get("Mod", ""), t.get("product_or_service_description", ""),
                t.get("naics_description", ""), t.get("Transaction Description", "")
            ])

        for t in ice_data:
            writer.writerow([
                "ICE", t.get("Award ID", ""), t.get("Recipient Name", ""),
                t.get("Transaction Amount", 0), t.get("Action Date", ""),
                t.get("Mod", ""), t.get("product_or_service_description", ""),
                t.get("naics_description", ""), t.get("Transaction Description", "")
            ])

    return csv_path


def fetch_fiscal_year(fy):
    """Fetch all data for a single fiscal year"""
    fy_config = FISCAL_YEARS[fy]
    print(f"\n{'='*60}")
    print(f"FISCAL YEAR {fy}")
    print(f"{'='*60}")
    print(f"Date range: {fy_config['start']} to {fy_config['end']}")

    cbp_data = []
    ice_data = []

    for abbrev, name in AGENCIES:
        print(f"\n  Fetching {abbrev}...")
        data = fetch_transactions(name, abbrev, fy_config['start'], fy_config['end'])
        if abbrev == "CBP":
            cbp_data = data
        else:
            ice_data = data

    csv_path = save_to_csv(cbp_data, ice_data, fy)

    cbp_total = sum(t.get("Transaction Amount", 0) or 0 for t in cbp_data)
    ice_total = sum(t.get("Transaction Amount", 0) or 0 for t in ice_data)

    print(f"\n  Results:")
    print(f"    CBP: ${cbp_total:,.2f} ({len(cbp_data)} transactions)")
    print(f"    ICE: ${ice_total:,.2f} ({len(ice_data)} transactions)")
    print(f"    Saved to: {csv_path}")

    return {
        "fy": fy,
        "cbp_total": cbp_total,
        "cbp_count": len(cbp_data),
        "ice_total": ice_total,
        "ice_count": len(ice_data)
    }


def main():
    import sys

    os.makedirs(DATA_DIR, exist_ok=True)

    print("=" * 60)
    print("CBP & ICE Contract Spending Data Fetcher")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Check for command line arguments
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'all':
        years_to_fetch = sorted(FISCAL_YEARS.keys(), reverse=True)
        print(f"\nFetching ALL fiscal years: {', '.join(f'FY{y}' for y in years_to_fetch)}")
    elif len(sys.argv) > 1:
        # Fetch specific fiscal years
        years_to_fetch = [int(y) for y in sys.argv[1:] if y.isdigit() and int(y) in FISCAL_YEARS]
        if not years_to_fetch:
            print(f"\nUsage: python {sys.argv[0]} [year1] [year2] ...")
            print(f"Available years: {', '.join(str(y) for y in sorted(FISCAL_YEARS.keys(), reverse=True))}")
            print(f"\nExample: python {sys.argv[0]} 2026 2025")
            print(f"         python {sys.argv[0]} all  # Fetch all years")
            return
    else:
        # Default: just fetch the most recent year
        years_to_fetch = [max(FISCAL_YEARS.keys())]
        print(f"\nNo year specified. Fetching FY{years_to_fetch[0]} only.")
        print(f"To fetch all years, run: python {sys.argv[0]} all")
        print(f"To fetch specific years: python {sys.argv[0]} 2026 2025 2024")

    results = []
    for fy in years_to_fetch:
        result = fetch_fiscal_year(fy)
        results.append(result)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"{'FY':<6} {'CBP Total':>18} {'CBP #':>8} {'ICE Total':>18} {'ICE #':>8}")
    print("-" * 60)
    for r in results:
        print(f"FY{r['fy']:<4} ${r['cbp_total']:>16,.0f} {r['cbp_count']:>8,} ${r['ice_total']:>16,.0f} {r['ice_count']:>8,}")

    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Data saved to: {DATA_DIR}")


if __name__ == "__main__":
    main()
