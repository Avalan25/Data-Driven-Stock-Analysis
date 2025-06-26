import os
import yaml  # instead of json
import pandas as pd
from collections import defaultdict
from pathlib import Path

# Base path containing all YAML files
base_path = r"C:\Users\91902\Desktop\Vs_code\Data-Driven Stock Analysis\data"
output_path = "fiftyfiles_output"
Path(output_path).mkdir(exist_ok=True)

# Dictionary to hold all entries grouped by Ticker
ticker_data = defaultdict(list)

# Loop through files in base folder
for file_name in os.listdir(base_path):
    if file_name.endswith("_05-30-00.yaml"):
        file_path = os.path.join(base_path, file_name)
        print(f"📄 Reading file: {file_path}")
        
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)  # Use PyYAML to read
        except Exception as e:
            print(f"❌ Error loading YAML: {file_path}: {e}")
            continue

        if not data:
            print(f"⚠️ Empty data in file: {file_path}")
            continue

        for entry in data:
            ticker = entry.get("Ticker")
            if ticker:
                filtered_entry = {
                    "date": entry.get("date"),
                    "open": entry.get("open"),
                    "high": entry.get("high"),
                    "low": entry.get("low"),
                    "close": entry.get("close"),
                    "volume": entry.get("volume"),
                    "Ticker": ticker
                }
                ticker_data[ticker].append(filtered_entry)
            else:
                print(f"⚠️ Missing Ticker in entry: {entry}")
    else:
        print(f"⏩ Skipped file (name mismatch): {file_name}")

# Write each Ticker's data to a CSV
for ticker, records in ticker_data.items():
    df = pd.DataFrame(records)

    if df.empty:
        print(f"⚠️ No data for ticker {ticker}, skipping.")
        continue

    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.sort_values(by='date')
    df = df[['date', 'open', 'high', 'low', 'close', 'volume', 'Ticker']]

    output_file = os.path.join(output_path, f"{ticker}.csv")
    df.to_csv(output_file, index=False)
    print(f"✅ Saved: {output_file}")
