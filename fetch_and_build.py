#!/usr/bin/env python3
"""
Fetch CBP & ICE FY26 data and prepare for dashboard
"""

import requests
import json
import csv
import os
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")

FY_START = "2025-10-01"
FY_END = "2026-09-30"

def fetch_all_transactions(agency_name, agency_abbrev):
    """Fetch all transaction data for an agency"""
    url = "https://api.usaspending.gov/api/v2/search/spending_by_transaction/"
    all_results = []
    page = 1

    print(f"\nFetching {agency_abbrev} contract transactions...")

    while True:
        payload = {
            "filters": {
                "agencies": [{
                    "type": "awarding",
                    "tier": "subtier",
                    "name": agency_name
                }],
                "time_period": [{
                    "start_date": FY_START,
                    "end_date": FY_END
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
            print(f"  Error on page {page}: {e}")
            break

        results = data.get("results", [])
        all_results.extend(results)
        print(f"  Page {page}: {len(results)} transactions (total: {len(all_results)})")

        if not data.get("page_metadata", {}).get("hasNext", False) or len(results) == 0:
            break
        page += 1

    return all_results

def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    print("=" * 60)
    print("CBP & ICE FY26 Dashboard Data Fetcher")
    print("=" * 60)

    cbp_data = fetch_all_transactions("U.S. Customs and Border Protection", "CBP")
    ice_data = fetch_all_transactions("U.S. Immigration and Customs Enforcement", "ICE")

    # Write CSV
    csv_path = os.path.join(DATA_DIR, "CBP_ICE_FY26_Contract_Obligations_Itemized.csv")
    print(f"\nWriting {csv_path}...")

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

    cbp_total = sum(t.get("Transaction Amount", 0) or 0 for t in cbp_data)
    ice_total = sum(t.get("Transaction Amount", 0) or 0 for t in ice_data)

    print("\n" + "=" * 60)
    print("COMPLETE!")
    print("=" * 60)
    print(f"CBP: ${cbp_total:,.2f} ({len(cbp_data)} transactions)")
    print(f"ICE: ${ice_total:,.2f} ({len(ice_data)} transactions)")
    print(f"Total: ${cbp_total + ice_total:,.2f}")
    print(f"\nData saved to: {csv_path}")

if __name__ == "__main__":
    main()
