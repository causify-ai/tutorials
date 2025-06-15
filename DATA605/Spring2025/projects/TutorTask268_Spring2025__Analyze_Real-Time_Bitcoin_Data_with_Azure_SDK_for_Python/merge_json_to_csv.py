import os
import json
import pandas as pd

folder_path = folder_path = "D:\\VS_Code\\DATA605\\tutorials\\DATA605\\Spring2025\\projects\\TutorTask268_Spring2025__Analyze_Real-Time_Bitcoin_Data_with_Azure_SDK_for_Python\\json_files"
output_csv = os.path.join(folder_path, "merged_bitcoin_data.csv")

# Store parsed records
records = []

# Iterate through JSON files
for filename in os.listdir(folder_path):
    if filename.endswith(".json"):
        full_path = os.path.join(folder_path, filename)
        with open(full_path, 'r') as infile:
            for line in infile:
                try:
                    obj = json.loads(line.strip())
                    records.append({
                        "currency": obj.get("currency"),
                        "price_usd": obj.get("price_usd"),
                        "timestamp": obj.get("timestamp")
                    })
                except Exception as e:
                    print(f"Skipped a line in {filename}: {e}")

# Convert to DataFrame and save to CSV
df = pd.DataFrame(records)
df.to_csv(output_csv, index=False)

print(f"✅ Merged CSV saved to: {output_csv}")
