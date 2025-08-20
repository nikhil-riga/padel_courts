# Singapore Dental Clinics Visualization

An interactive map visualization showing dental clinics across Singapore overlaid with household income data, using exact postal code coordinates.

## 🗺️ Features

- **Exact Coordinates**: Uses comprehensive Singapore postal code dataset (121,135 postal codes) for precise clinic locations
- **Interactive Map**: Built with Folium for zoom, pan, and layer controls
- **Household Income Background**: Choropleth map showing average household income by planning area
- **Clinic Classification**: 
  - 🟢 **Green markers**: Active dental clinics
  - 🔴 **Red markers**: Non-active dental clinics  
  - ⭐ **Purple stars**: Ashford clinics (special highlighting)
- **High Accuracy**: 97.4% of clinics (1,873 out of 1,923) have exact coordinates

## 📊 Data Sources

- **Dental Clinics**: `Visualization w ceased/Dental_Clinics_Acra.csv` (1,923 clinics)
- **Postal Codes**: `Visualization w ceased/SG_postal.csv` (121,135 postal codes with exact lat/lng)
- **Household Income**: `singapore_household_income_data.csv` (2020 data by planning area)
- **Boundaries**: `planning_areas_boundaries.geojson` (Singapore planning area boundaries)

## 🚀 Quick Start

1. **Install Dependencies**:
   ```bash
   pip install folium pandas requests
   ```

2. **Run the Visualization**:
   ```bash
   python3 use_kaggle_postal_data.py
   ```

3. **View the Map**:
   ```bash
   python3 -m http.server 8000
   ```
   Then open: `http://localhost:8000/dental_clinics_exact_coordinates.html`

## 📁 Key Files

- `use_kaggle_postal_data.py` - Main visualization script
- `dental_clinics_exact_coordinates.html` - Final interactive map
- `debug_postal_matching.py` - Debug script for postal code matching
- `Visualization w ceased/` - Contains source data files

## 🎨 Color Scheme

**Household Income (Background)**:
- 🔵 Very Light Blue: < $5,000
- 🔵 Light Blue: $5,000 - $8,000
- 🔵 Medium Blue: $8,000 - $12,000
- 🔵 Dark Blue: $12,000 - $15,000
- 🔵 Very Dark Blue: > $15,000

**Dental Clinics (Markers)**:
- 🟢 Green: Active clinics
- 🔴 Red: Non-active clinics
- ⭐ Purple: Ashford clinics

## 📈 Statistics

- **Total Clinics**: 1,923
- **Clinics with Exact Coordinates**: 1,873 (97.4%)
- **Active Clinics**: 1,074
- **Non-Active Clinics**: 799
- **Ashford Clinics**: 5
- **Clinics without Coordinates**: 50

## 🔧 Technical Details

- **Geocoding**: Uses exact postal code coordinates from SG_postal.csv
- **Mapping**: Folium with OpenStreetMap tiles
- **Data Processing**: Pandas for CSV handling and data manipulation
- **Visualization**: Choropleth for income data, markers for clinics

## 📝 Notes

- Areas without income data (water catchments, islands, industrial areas) appear in default color
- Some clinics may not have coordinates if their postal codes aren't in the dataset
- The visualization uses 2020 household income data

## 🤝 Contributing

Feel free to submit issues and enhancement requests!