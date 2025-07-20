import pandas as pd
import folium
from folium import plugins

def create_simple_ultra_map():
    """Create a simple ultra high-resolution map with existing CSV data"""
    print("Loading CSV data...")
    
    # Load the CSV file
    try:
        df = pd.read_csv('padel_court_locations_CLEAN_HIGHRES.csv')
        print(f"✅ Loaded {len(df)} locations from CSV")
    except FileNotFoundError:
        print("❌ CSV file not found. Please ensure the file exists.")
        return
    
    # Clean the data - remove any rows with missing coordinates
    df_clean = df.dropna(subset=['lat', 'lng'])
    df_clean = df_clean[(df_clean['lat'] != 0) & (df_clean['lng'] != 0)]
    print(f"✅ Cleaned data: {len(df_clean)} valid locations")
    
    # Create the base map
    print("Creating map...")
    m = folium.Map(
        location=[1.3521, 103.8198],  # Singapore center
        zoom_start=11,
        max_zoom=20
    )
    
    # Add satellite layers
    # Google Satellite
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        attr='Google Satellite',
        name='Google Satellite',
        overlay=False
    ).add_to(m)
    
    # Esri Satellite
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri World Imagery',
        name='Esri Satellite',
        overlay=False
    ).add_to(m)
    
    # OpenStreetMap (street view)
    folium.TileLayer(
        tiles='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        attr='OpenStreetMap',
        name='Street Map',
        overlay=False
    ).add_to(m)
    
    # Define color scheme by location type
    location_colors = {
        'park_open_space': 'green',      # Parks and open spaces
        'carpark': 'blue',               # Car parks
        'hdb_block': 'red',              # HDB blocks
        'recreation_centre': 'purple',   # Recreation centres
        'school': 'orange',              # Schools
        'soccer_court': 'darkgreen',     # Soccer courts
        'rooftop': 'darkblue',           # Rooftops
        'industrial_space': 'gray',      # Industrial spaces
        'unknown': 'lightgray'           # Unknown types
    }
    
    # Create feature groups for each location type
    feature_groups = {}
    for loc_type in location_colors.keys():
        feature_groups[loc_type] = folium.FeatureGroup(name=f"{loc_type.replace('_', ' ').title()}")
    
    # Add markers for each location
    print("Adding markers...")
    markers_added = 0
    type_counts = {}
    
    for index, row in df_clean.iterrows():
        try:
            # Convert to dictionary to avoid pandas type issues
            row_dict = row.to_dict()
            
            lat = float(row_dict['lat'])
            lng = float(row_dict['lng'])
            name = str(row_dict.get('name', 'Unknown'))
            score = int(row_dict.get('suitability_score', 0))
            loc_type = str(row_dict.get('type', 'unknown'))
            
            # Count location types
            type_counts[loc_type] = type_counts.get(loc_type, 0) + 1
            
            # Determine marker color based on location type
            color = location_colors.get(loc_type, 'lightgray')
            
            # Create popup content
            popup_html = f"""
            <div style="width: 300px;">
                <h4>{name}</h4>
                <p><strong>Type:</strong> {loc_type.replace('_', ' ').title()}</p>
                <p><strong>Score:</strong> {score}/100</p>
                <p><strong>Area:</strong> {row_dict.get('area_estimate_sqm', 'Unknown')} sqm</p>
                <p><strong>Surface:</strong> {row_dict.get('surface_type', 'Unknown')}</p>
                <p><strong>Current Use:</strong> {row_dict.get('current_use', 'Unknown')}</p>
                <p><strong>Address:</strong> {row_dict.get('address', 'Unknown')}</p>
                <p><strong>Planning Area:</strong> {row_dict.get('planning_area', 'Unknown')}</p>
                <p><strong>Land Owner:</strong> {row_dict.get('land_owner', 'Unknown')}</p>
                <p><strong>Permission Required:</strong> {row_dict.get('likely_permission_required_from', 'Unknown')}</p>
            </div>
            """
            
            # Create marker
            marker = folium.Marker(
                location=[lat, lng],
                popup=folium.Popup(popup_html, max_width=350),
                tooltip=f"{name} ({loc_type.replace('_', ' ').title()})",
                icon=folium.Icon(color=color, icon='info-sign')
            )
            
            # Add to appropriate feature group
            if loc_type in feature_groups:
                marker.add_to(feature_groups[loc_type])
            else:
                marker.add_to(m)
            
            markers_added += 1
            
        except Exception as e:
            print(f"Error adding marker for row {index}: {e}")
            continue
    
    # Add all feature groups to map
    for feature_group in feature_groups.values():
        feature_group.add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Add fullscreen
    plugins.Fullscreen().add_to(m)
    
    # Add minimap
    minimap = plugins.MiniMap(toggle_display=True)
    m.add_child(minimap)
    
    # Add legend using a different approach - create dummy markers for legend
    legend_locations = [
        (1.2000, 103.6000),  # Bottom left of Singapore
        (1.2000, 103.6500),
        (1.2000, 103.7000),
        (1.2000, 103.7500),
        (1.2000, 103.8000),
        (1.2000, 103.8500),
        (1.2000, 103.9000),
        (1.2000, 103.9500),
        (1.2000, 104.0000),
    ]
    
    legend_types = list(location_colors.keys())
    for i, (lat, lng) in enumerate(legend_locations):
        if i < len(legend_types):
            loc_type = legend_types[i]
            color = location_colors[loc_type]
            
            # Create legend marker
            folium.Marker(
                location=[lat, lng],
                popup=f"<b>{loc_type.replace('_', ' ').title()}</b>",
                tooltip=f"{loc_type.replace('_', ' ').title()}",
                icon=folium.Icon(color=color, icon='info-sign')
            ).add_to(m)
    
    # Save the map
    output_file = 'SIMPLE_ULTRA_MAP_BY_TYPE.html'
    m.save(output_file)
    
    print(f"✅ Map created successfully!")
    print(f"📊 Added {markers_added} markers")
    print(f"🗺️  Saved as: {output_file}")
    print(f"🌐 Open {output_file} in your browser to view the map")
    
    # Print location type summary
    print("\n=== LOCATION TYPES ===")
    for loc_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        color = location_colors.get(loc_type, 'lightgray')
        print(f"🔸 {loc_type.replace('_', ' ').title()}: {count} locations ({color} markers)")
    
    print("\n=== COLOR LEGEND ===")
    for loc_type, color in location_colors.items():
        print(f"🔸 {color.upper()}: {loc_type.replace('_', ' ').title()}")
    
    return m

if __name__ == "__main__":
    create_simple_ultra_map() 