import pandas as pd

# Load postal codes
print("Loading SG_postal.csv...")
postal_df = pd.read_csv('Visualization w ceased/SG_postal.csv')
print(f"Loaded {len(postal_df)} postal codes")

# Create postal code mapping
postal_coords = {}
for _, row in postal_df.iterrows():
    postal_code = str(row['postal_code']).strip()
    lat = float(row['lat'])
    lng = float(row['lon'])
    postal_coords[postal_code] = [lat, lng]

print(f"Created mapping with {len(postal_coords)} postal codes")

# Load dental clinics
print("\nLoading dental clinics...")
clinics_df = pd.read_csv('Visualization w ceased/Dental_Clinics_Acra.csv')
print(f"Loaded {len(clinics_df)} clinics")

# Test matching
test_postal_codes = ['247909', '81007', '106', '208928', '198733']
print(f"\nTesting postal code matching:")
for postal in test_postal_codes:
    if postal in postal_coords:
        print(f"✓ {postal} -> {postal_coords[postal]}")
    else:
        print(f"✗ {postal} -> NOT FOUND")

# Count matches
matches = 0
for _, clinic in clinics_df.iterrows():
    postal_code = str(clinic['postal_code']).strip()
    if postal_code in postal_coords:
        matches += 1

print(f"\nTotal clinics: {len(clinics_df)}")
print(f"Clinics with matching postal codes: {matches}")
print(f"Match rate: {matches/len(clinics_df)*100:.1f}%")
