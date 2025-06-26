import os
import pandas as pd
from pathlib import Path

# Folder where your 50 CSV files are stored
input_folder = r"C:\Users\91902\Desktop\Vs_code\Data-Driven Stock Analysis\fiftyfiles_output"

# Output folder for the combined CSV
output_folder = os.path.join(os.path.dirname(input_folder), "new")
Path(output_folder).mkdir(exist_ok=True)

# Initialize an empty list to collect all DataFrames
all_data = []

# Loop through all CSV files in the folder
for file_name in os.listdir(input_folder):
    if file_name.endswith(".csv"):
        file_path = os.path.join(input_folder, file_name)
        print(f"📄 Reading: {file_name}")
        df = pd.read_csv(file_path)
        all_data.append(df)

# Concatenate all DataFrames into one
combined_df = pd.concat(all_data, ignore_index=True)

# Save to a new CSV file
output_path = os.path.join(output_folder, "combined.csv")
combined_df.to_csv(output_path, index=False)
print(f"\n✅ Combined CSV saved to: {output_path}")
