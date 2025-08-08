# make_city_gz.py
import json
import gzip

INPUT_FILE = "city.list.json"       # your original file
OUTPUT_FILE = "citynames.json.gz"   # optimized file

with open(INPUT_FILE, encoding="utf-8") as f:
    data = json.load(f)

# Extract only city names
city_names = [c["name"] for c in data]

# Save as compressed gz file
with gzip.open(OUTPUT_FILE, "wt", encoding="utf-8") as gz:
    json.dump(city_names, gz)

print(f"✅ Created {OUTPUT_FILE} with {len(city_names)} city names.")
