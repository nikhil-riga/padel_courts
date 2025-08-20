import pandas as pd
import folium
import json
import csv
from folium import plugins

def load_postal_coordinates(postal_data_file):
    """Load postal code coordinates from Kaggle dataset"""
    try:
        # Read the Kaggle postal code dataset
        # Expected columns: postal_code, latitude, longitude (or similar)
        postal_df = pd.read_csv(postal_data_file)
        
        # Print column names to understand the structure
        print("Postal data columns:", postal_df.columns.tolist())
        print("First few rows:")
        print(postal_df.head())
        
        # Create a mapping from postal code to coordinates
        # Adjust column names based on the actual dataset structure
        postal_coords = {}
        
        # Use the exact column names from SG_postal.csv
        for _, row in postal_df.iterrows():
            postal_code = str(row['postal_code']).strip()
            lat = float(row['lat'])
            lng = float(row['lon'])
            postal_coords[postal_code] = [lat, lng]
        
        print(f"Successfully loaded {len(postal_coords)} postal code coordinates")
        return postal_coords
            
    except FileNotFoundError:
        print(f"Error: {postal_data_file} not found")
        print("Please ensure SG_postal.csv is in the 'Visualization w ceased' folder.")
        return {}
    except Exception as e:
        print(f"Error loading postal data: {e}")
        return {}

def get_coordinates_from_postal_code(postal_code, postal_coords):
    """Get exact coordinates from postal code using Kaggle data"""
    if not postal_code or postal_code == 'na':
        return None, None
    
    postal_code = str(postal_code).strip()
    
    # Try exact match first
    if postal_code in postal_coords:
        return postal_coords[postal_code]
    
    # Try with leading zeros removed
    postal_code_no_zeros = postal_code.lstrip('0')
    if postal_code_no_zeros in postal_coords:
        return postal_coords[postal_code_no_zeros]
    
    # Try with leading zeros added (6 digits)
    postal_code_padded = postal_code.zfill(6)
    if postal_code_padded in postal_coords:
        return postal_coords[postal_code_padded]
    
    # If no exact match, return None
    return None, None

def load_household_income_data():
    """Load household income data from CSV"""
    try:
        df = pd.read_csv('singapore_household_income_data.csv')
        return df
    except FileNotFoundError:
        print("Warning: singapore_household_income_data.csv not found")
        return None

def load_planning_area_boundaries():
    """Load planning area boundaries from GeoJSON"""
    try:
        with open('planning_areas_boundaries.geojson', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Warning: planning_areas_boundaries.geojson not found")
        return None

def load_dental_clinics(postal_coords):
    """Load dental clinics data from the new CSV file"""
    clinics = []
    geocoded_count = 0
    
    try:
        with open('Visualization w ceased/Dental_Clinics_Acra.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Extract address components from columns P to S
                street_name = row.get('street_name', '')
                building_name = row.get('building_name', '')
                unit_no = row.get('unit_no', '')
                postal_code = row.get('postal_code', '')
                
                # Construct full address
                address_parts = []
                if street_name:
                    address_parts.append(street_name)
                if building_name and building_name != 'na':
                    address_parts.append(building_name)
                if unit_no and unit_no != 'na':
                    address_parts.append(f"#{unit_no}")
                if postal_code and postal_code != 'na':
                    address_parts.append(postal_code)
                
                full_address = ', '.join(address_parts) if address_parts else 'Address not available'
                
                # Get exact coordinates from postal code using Kaggle data
                lat, lng = get_coordinates_from_postal_code(postal_code, postal_coords)
                if lat and lng:
                    geocoded_count += 1
                
                clinic = {
                    'uen': row.get('uen', ''),
                    'entity_name': row.get('entity_name', ''),
                    'entity_active': row.get('entity_active', ''),
                    'address': full_address,
                    'street_name': street_name,
                    'building_name': building_name,
                    'unit_no': unit_no,
                    'postal_code': postal_code,
                    'entity_status_description': row.get('entity_status_description', ''),
                    'registration_incorporation_date': row.get('registration_incorporation_date', ''),
                    'lat': lat,
                    'lng': lng
                }
                clinics.append(clinic)
        
        print(f"Loaded {len(clinics)} dental clinics from CSV")
        print(f"Successfully geocoded {geocoded_count} clinics with exact coordinates")
        return clinics
    except FileNotFoundError:
        print("Error: Dental_Clinics_Acra.csv not found in 'Visualization w ceased' folder")
        return []

def get_color_by_income(income):
    """Get color based on household income - using blue color scheme for better contrast"""
    if income < 5000:
        return '#e3f2fd'  # Very light blue
    elif income < 8000:
        return '#90caf9'  # Light blue
    elif income < 12000:
        return '#42a5f5'  # Medium blue
    elif income < 15000:
        return '#1976d2'  # Dark blue
    else:
        return '#0d47a1'  # Very dark blue

def create_interactive_map(income_data, boundaries, clinics):
    """Create interactive map with household income and dental clinics"""
    
    # Create base map centered on Singapore
    m = folium.Map(location=[1.3521, 103.8198], zoom_start=11)
    
    # Add household income choropleth layer
    if income_data is not None and boundaries is not None:
        # Create a mapping from planning area names to income data
        # Handle case mismatch between income data and GeoJSON
        income_dict = {}
        for area, income in zip(income_data['planning_area'], income_data['avg_household_income']):
            # Store both title case and uppercase versions
            income_dict[area] = income
            income_dict[area.upper()] = income
        
        print(f"Available planning areas in income data: {list(income_data['planning_area'])}")
        print(f"Sample income mapping: {dict(list(income_dict.items())[:5])}")
        
        # Style function for the choropleth
        def style_function(feature):
            area_name = feature['properties']['PLN_AREA_N']
            income = income_dict.get(area_name, 0)
            if income == 0:
                print(f"No income data found for area: {area_name}")
            return {
                'fillColor': get_color_by_income(income),
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.7
            }
        
        # Add choropleth layer
        folium.GeoJson(
            boundaries,
            name='Household Income',
            style_function=style_function,
            tooltip=folium.GeoJsonTooltip(
                fields=['PLN_AREA_N'],
                aliases=['Planning Area:'],
                style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
            )
        ).add_to(m)
    
    # Add dental clinics markers
    if clinics:
        # Separate clinics by status and type
        active_clinics = []
        non_active_clinics = []
        ashford_clinics = []
        geocoded_clinics = []
        non_geocoded_clinics = []
        
        for clinic in clinics:
            entity_name = clinic['entity_name'].lower() if clinic['entity_name'] else ''
            is_ashford = 'ashford' in entity_name
            has_coords = clinic.get('lat') and clinic.get('lng')
            
            if has_coords:
                geocoded_clinics.append(clinic)
            else:
                non_geocoded_clinics.append(clinic)
                continue  # Skip clinics without coordinates
            
            if is_ashford:
                ashford_clinics.append(clinic)
            elif clinic['entity_active'] == 'Active':
                active_clinics.append(clinic)
            else:
                non_active_clinics.append(clinic)
        
        # Add active clinics (green)
        fg_active = folium.FeatureGroup(name="Active Clinics", show=True)
        for clinic in active_clinics:
            popup_text = f"""
            <b>{clinic['entity_name']}</b><br>
            <b>Status:</b> {clinic['entity_active']}<br>
            <b>Address:</b> {clinic['address']}<br>
            <b>Registration Date:</b> {clinic['registration_incorporation_date']}<br>
            <b>UEN:</b> {clinic['uen']}<br>
            <b>Postal Code:</b> {clinic['postal_code']}
            """
            
            location = [clinic['lat'], clinic['lng']]
            
            folium.Marker(
                location=location,
                popup=folium.Popup(popup_text, max_width=300),
                tooltip=clinic['entity_name'],
                icon=folium.Icon(color='green', icon='check-circle', prefix='fa')
            ).add_to(fg_active)
        fg_active.add_to(m)
        
        # Add non-active clinics (red)
        fg_non_active = folium.FeatureGroup(name="Non-Active Clinics", show=False)
        for clinic in non_active_clinics:
            popup_text = f"""
            <b>{clinic['entity_name']}</b><br>
            <b>Status:</b> {clinic['entity_active']}<br>
            <b>Address:</b> {clinic['address']}<br>
            <b>Registration Date:</b> {clinic['registration_incorporation_date']}<br>
            <b>UEN:</b> {clinic['uen']}<br>
            <b>Postal Code:</b> {clinic['postal_code']}
            """
            
            location = [clinic['lat'], clinic['lng']]
            
            folium.Marker(
                location=location,
                popup=folium.Popup(popup_text, max_width=300),
                tooltip=clinic['entity_name'],
                icon=folium.Icon(color='red', icon='times-circle', prefix='fa')
            ).add_to(fg_non_active)
        fg_non_active.add_to(m)
        
        # Add Ashford clinics (purple)
        fg_ashford = folium.FeatureGroup(name="Ashford Clinics", show=True)
        for clinic in ashford_clinics:
            popup_text = f"""
            <b>{clinic['entity_name']}</b><br>
            <b>Status:</b> {clinic['entity_active']}<br>
            <b>Address:</b> {clinic['address']}<br>
            <b>Registration Date:</b> {clinic['registration_incorporation_date']}<br>
            <b>UEN:</b> {clinic['uen']}<br>
            <b>Postal Code:</b> {clinic['postal_code']}
            """
            
            location = [clinic['lat'], clinic['lng']]
            
            folium.Marker(
                location=location,
                popup=folium.Popup(popup_text, max_width=300),
                tooltip=clinic['entity_name'],
                icon=folium.Icon(color='purple', icon='star', prefix='fa')
            ).add_to(fg_ashford)
        fg_ashford.add_to(m)
        
        print(f"Added {len(active_clinics)} active clinics")
        print(f"Added {len(non_active_clinics)} non-active clinics")
        print(f"Added {len(ashford_clinics)} Ashford clinics")
        print(f"Total geocoded clinics: {len(geocoded_clinics)}")
        print(f"Clinics without coordinates: {len(non_geocoded_clinics)}")
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Add legend
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 350px; height: 220px; 
                background-color: white; z-index:9999; font-size:14px; border:2px solid grey; border-radius: 8px; box-shadow: 2px 2px 8px #888; padding: 14px;">
    <b>Dental Clinics Overlay</b><br><br>
    <i class="fa fa-check-circle fa-2x" style="color:green"></i> Active Clinics<br>
    <i class="fa fa-times-circle fa-2x" style="color:red"></i> Non-Active Clinics<br>
    <i class="fa fa-star fa-2x" style="color:purple"></i> Ashford Clinics<br><br>
    <b>Household Income (Background)</b><br>
    <div style="width:20px; height:20px; background-color:#e3f2fd; display:inline-block; border:1px solid black;"></div> &lt; $5,000<br>
    <div style="width:20px; height:20px; background-color:#90caf9; display:inline-block; border:1px solid black;"></div> $5,000 - $8,000<br>
    <div style="width:20px; height:20px; background-color:#42a5f5; display:inline-block; border:1px solid black;"></div> $8,000 - $12,000<br>
    <div style="width:20px; height:20px; background-color:#1976d2; display:inline-block; border:1px solid black;"></div> $12,000 - $15,000<br>
    <div style="width:20px; height:20px; background-color:#0d47a1; display:inline-block; border:1px solid black;"></div> &gt; $15,000<br>
    <small>*Using exact coordinates from SG postal dataset</small>
    </div>
    '''
    m.get_root().add_child(folium.Element(legend_html))
    
    return m

def main():
    print("Creating dental clinics visualization with exact SG postal coordinates...")
    
    # Load the Singapore postal code dataset
    postal_data_file = 'Visualization w ceased/SG_postal.csv'
    
    postal_coords = load_postal_coordinates(postal_data_file)
    
    if not postal_coords:
        print("\nERROR: Could not load postal code coordinates.")
        print("Please ensure SG_postal.csv is in the 'Visualization w ceased' folder.")
        return
    
    # Load other data
    income_data = load_household_income_data()
    boundaries = load_planning_area_boundaries()
    clinics = load_dental_clinics(postal_coords)
    
    if not clinics:
        print("No dental clinics data found. Exiting.")
        return
    
    # Create interactive map
    print("Creating interactive map...")
    m = create_interactive_map(income_data, boundaries, clinics)
    
    # Save map
    output_file = 'dental_clinics_exact_coordinates.html'
    m.save(output_file)
    print(f"Map saved as {output_file}")
    
    # Print summary statistics
    if clinics:
        active_count = sum(1 for c in clinics if c['entity_active'] == 'Active' and c.get('lat') and c.get('lng'))
        non_active_count = sum(1 for c in clinics if c['entity_active'] != 'Active' and c.get('lat') and c.get('lng'))
        ashford_count = sum(1 for c in clinics if 'ashford' in c['entity_name'].lower() and c.get('lat') and c.get('lng'))
        geocoded_count = sum(1 for c in clinics if c.get('lat') and c.get('lng'))
        
        print(f"\nSummary:")
        print(f"Total clinics: {len(clinics)}")
        print(f"Clinics with exact coordinates: {geocoded_count}")
        print(f"Active clinics (geocoded): {active_count}")
        print(f"Non-active clinics (geocoded): {non_active_count}")
        print(f"Ashford clinics (geocoded): {ashford_count}")

if __name__ == "__main__":
    main()
