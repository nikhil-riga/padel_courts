import requests
import json
import pandas as pd
import folium
from folium import plugins
import time
import math
from typing import List, Dict, Tuple, Optional
import csv

# OneMap API configuration
TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo3OTU4LCJmb3JldmVyIjpmYWxzZSwiaXNzIjoiT25lTWFwIiwiaWF0IjoxNzUyODEwODEwLCJuYmYiOjE3NTI4MTA4MTAsImV4cCI6MTc1MzA3MDAxMCwianRpIjoiNGViODFmNzMtZjQ2NS00NjA2LWJhYjUtOThmODY0M2EyODdiIn0.ckZLe4RbQcYhY_ezalON1Fx4Xa9qVYr__Yn5HhtXv2zvu37XTzzbLNJ-QoWcdlFYn53MqqVTrAZiRHEL9LJ6VGgECPtAQjRPCAEzUJ7nfXNgtSGRNn9WfPdiPPRNwuSc5kzCzgXfUV_t3zYMEaUnRwjnQNxaai2p44DmT18Pw24TK0ZC6e4tSiiEZexb-3j0V6Wtow7BnEc3klZA3WrzOxAkmvA2qImWjhMo2C9Io01RxSD7bRzw2DpHi_c0HVsFcY3Q-p290wx1-9ktUdfwAXtf3jbIA_ooQflpT3tP7W71OTMbyehloq2PLvwJdE-HDI_mAj3HJ3Sr9FSpGEuYig"

# Singapore planning areas (residential focus)
PLANNING_AREAS = [
    "Ang Mo Kio", "Bedok", "Bishan", "Bukit Batok", "Bukit Merah",
    "Bukit Panjang", "Bukit Timah", "Changi", "Clementi", "Downtown Core", "Geylang",
    "Hougang", "Jurong East", "Jurong West", "Kallang", "Mandai", "Marine Parade",
    "Novena", "Orchard", "Outram", "Pasir Ris", "Punggol", "Queenstown",
    "River Valley", "Rochor", "Sembawang", "Sengkang", "Serangoon", "Singapore River", 
    "Tampines", "Tanglin", "Toa Payoh", "Woodlands", "Yishun"
]

# Padel court requirements
PADEL_COURT_MIN_AREA = 200  # sqm
PADEL_COURT_DIMENSIONS = (20, 10)  # meters (length, width)

def robust_request(url, headers=None, params=None, max_retries=3):
    """Make a robust request with retries"""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            return response
        except Exception as e:
            wait = 2 ** attempt
            print(f"Request failed ({e}), retrying in {wait}s...")
            time.sleep(wait)
    print(f"Failed to fetch after {max_retries} attempts: {url}")
    return None

def search_recreation_centres(planning_area: str) -> List[Dict]:
    """Search for recreation centres and community clubs"""
    print(f"Searching recreation centres in {planning_area}...")
    
    search_url = f"https://www.onemap.gov.sg/api/common/elastic/search"
    params = {
        'searchVal': f'recreation centre {planning_area}',
        'returnGeom': 'Y',
        'getAddrDetails': 'Y',
        'pageNum': 1
    }
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    response = robust_request(search_url, headers=headers, params=params)
    if not response or response.status_code != 200:
        return []
    
    try:
        data = response.json()
        results = data.get('results', [])
        
        filtered_results = []
        for result in results:
            name = result.get('SEARCHVAL', '').lower()
            if any(keyword in name for keyword in ['recreation', 'community club', 'cc', 'sports hall']):
                filtered_results.append({
                    'name': result.get('SEARCHVAL', ''),
                    'address': result.get('ADDRESS', ''),
                    'lat': float(result.get('LATITUDE', 0)),
                    'lng': float(result.get('LONGITUDE', 0)),
                    'type': 'recreation_centre',
                    'planning_area': planning_area
                })
        
        return filtered_results
    except Exception as e:
        print(f"Error processing recreation centres data for {planning_area}: {e}")
        return []

def search_schools(planning_area: str) -> List[Dict]:
    """Search for schools with potential rooftop or underutilized spaces"""
    print(f"Searching schools in {planning_area}...")
    
    search_url = f"https://www.onemap.gov.sg/api/common/elastic/search"
    params = {
        'searchVal': f'school {planning_area}',
        'returnGeom': 'Y',
        'getAddrDetails': 'Y',
        'pageNum': 1
    }
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    response = robust_request(search_url, headers=headers, params=params)
    if not response or response.status_code != 200:
        return []
    
    try:
        data = response.json()
        results = data.get('results', [])
        
        filtered_results = []
        for result in results:
            name = result.get('SEARCHVAL', '').lower()
            if any(keyword in name for keyword in ['school', 'primary', 'secondary', 'junior college', 'jc']):
                filtered_results.append({
                    'name': result.get('SEARCHVAL', ''),
                    'address': result.get('ADDRESS', ''),
                    'lat': float(result.get('LATITUDE', 0)),
                    'lng': float(result.get('LONGITUDE', 0)),
                    'type': 'school',
                    'planning_area': planning_area
                })
        
        return filtered_results
    except Exception as e:
        print(f"Error processing schools data for {planning_area}: {e}")
        return []

def search_soccer_courts(planning_area: str) -> List[Dict]:
    """Search for soccer courts and football fields"""
    print(f"Searching soccer courts in {planning_area}...")
    
    search_url = f"https://www.onemap.gov.sg/api/common/elastic/search"
    params = {
        'searchVal': f'soccer court {planning_area}',
        'returnGeom': 'Y',
        'getAddrDetails': 'Y',
        'pageNum': 1
    }
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    response = robust_request(search_url, headers=headers, params=params)
    if not response or response.status_code != 200:
        return []
    
    try:
        data = response.json()
        results = data.get('results', [])
        
        filtered_results = []
        for result in results:
            name = result.get('SEARCHVAL', '').lower()
            if any(keyword in name for keyword in ['soccer', 'football', 'field', 'court']):
                filtered_results.append({
                    'name': result.get('SEARCHVAL', ''),
                    'address': result.get('ADDRESS', ''),
                    'lat': float(result.get('LATITUDE', 0)),
                    'lng': float(result.get('LONGITUDE', 0)),
                    'type': 'soccer_court',
                    'planning_area': planning_area
                })
        
        return filtered_results
    except Exception as e:
        print(f"Error processing soccer courts data for {planning_area}: {e}")
        return []

def search_rooftops(planning_area: str) -> List[Dict]:
    """Search for rooftop spaces and terraces"""
    print(f"Searching rooftop spaces in {planning_area}...")
    
    search_url = f"https://www.onemap.gov.sg/api/common/elastic/search"
    params = {
        'searchVal': f'rooftop {planning_area}',
        'returnGeom': 'Y',
        'getAddrDetails': 'Y',
        'pageNum': 1
    }
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    response = robust_request(search_url, headers=headers, params=params)
    if not response or response.status_code != 200:
        return []
    
    try:
        data = response.json()
        results = data.get('results', [])
        
        filtered_results = []
        for result in results:
            name = result.get('SEARCHVAL', '').lower()
            if any(keyword in name for keyword in ['rooftop', 'roof', 'terrace', 'sky']):
                filtered_results.append({
                    'name': result.get('SEARCHVAL', ''),
                    'address': result.get('ADDRESS', ''),
                    'lat': float(result.get('LATITUDE', 0)),
                    'lng': float(result.get('LONGITUDE', 0)),
                    'type': 'rooftop',
                    'planning_area': planning_area
                })
        
        return filtered_results
    except Exception as e:
        print(f"Error processing rooftop data for {planning_area}: {e}")
        return []

def search_industrial_spaces(planning_area: str) -> List[Dict]:
    """Search for industrial areas with potential underutilized spaces"""
    print(f"Searching industrial spaces in {planning_area}...")
    
    search_url = f"https://www.onemap.gov.sg/api/common/elastic/search"
    params = {
        'searchVal': f'industrial {planning_area}',
        'returnGeom': 'Y',
        'getAddrDetails': 'Y',
        'pageNum': 1
    }
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    response = robust_request(search_url, headers=headers, params=params)
    if not response or response.status_code != 200:
        return []
    
    try:
        data = response.json()
        results = data.get('results', [])
        
        filtered_results = []
        for result in results:
            name = result.get('SEARCHVAL', '').lower()
            if any(keyword in name for keyword in ['industrial', 'factory', 'warehouse', 'logistics']):
                filtered_results.append({
                    'name': result.get('SEARCHVAL', ''),
                    'address': result.get('ADDRESS', ''),
                    'lat': float(result.get('LATITUDE', 0)),
                    'lng': float(result.get('LONGITUDE', 0)),
                    'type': 'industrial_space',
                    'planning_area': planning_area
                })
        
        return filtered_results
    except Exception as e:
        print(f"Error processing industrial spaces data for {planning_area}: {e}")
        return []

def search_parks_and_open_spaces(planning_area: str) -> List[Dict]:
    """Search for parks and open spaces in a planning area using OneMap API"""
    print(f"Searching parks and open spaces in {planning_area}...")
    
    search_url = f"https://www.onemap.gov.sg/api/common/elastic/search"
    params = {
        'searchVal': f'park {planning_area}',
        'returnGeom': 'Y',
        'getAddrDetails': 'Y',
        'pageNum': 1
    }
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    response = robust_request(search_url, headers=headers, params=params)
    if not response or response.status_code != 200:
        return []
    
    try:
        data = response.json()
        results = data.get('results', [])
        
        filtered_results = []
        for result in results:
            name = result.get('SEARCHVAL', '').lower()
            if any(keyword in name for keyword in ['park', 'garden', 'playground', 'open space', 'lawn']):
                filtered_results.append({
                    'name': result.get('SEARCHVAL', ''),
                    'address': result.get('ADDRESS', ''),
                    'lat': float(result.get('LATITUDE', 0)),
                    'lng': float(result.get('LONGITUDE', 0)),
                    'type': 'park_open_space',
                    'planning_area': planning_area
                })
        
        return filtered_results
    except Exception as e:
        print(f"Error processing parks data for {planning_area}: {e}")
        return []

def search_carparks(planning_area: str) -> List[Dict]:
    """Search for carparks in a planning area"""
    print(f"Searching carparks in {planning_area}...")
    
    search_url = f"https://www.onemap.gov.sg/api/common/elastic/search"
    params = {
        'searchVal': f'car park {planning_area}',
        'returnGeom': 'Y',
        'getAddrDetails': 'Y',
        'pageNum': 1
    }
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    response = robust_request(search_url, headers=headers, params=params)
    if not response or response.status_code != 200:
        return []
    
    try:
        data = response.json()
        results = data.get('results', [])
        
        filtered_results = []
        for result in results:
            name = result.get('SEARCHVAL', '').lower()
            if any(keyword in name for keyword in ['car park', 'parking', 'carpark']):
                filtered_results.append({
                    'name': result.get('SEARCHVAL', ''),
                    'address': result.get('ADDRESS', ''),
                    'lat': float(result.get('LATITUDE', 0)),
                    'lng': float(result.get('LONGITUDE', 0)),
                    'type': 'carpark',
                    'planning_area': planning_area
                })
        
        return filtered_results
    except Exception as e:
        print(f"Error processing carpark data for {planning_area}: {e}")
        return []

def search_hdb_blocks(planning_area: str) -> List[Dict]:
    """Search for HDB blocks in a planning area"""
    print(f"Searching HDB blocks in {planning_area}...")
    
    search_url = f"https://www.onemap.gov.sg/api/common/elastic/search"
    params = {
        'searchVal': f'HDB {planning_area}',
        'returnGeom': 'Y',
        'getAddrDetails': 'Y',
        'pageNum': 1
    }
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    response = robust_request(search_url, headers=headers, params=params)
    if not response or response.status_code != 200:
        return []
    
    try:
        data = response.json()
        results = data.get('results', [])
        
        filtered_results = []
        for result in results:
            name = result.get('SEARCHVAL', '').lower()
            if 'hdb' in name and any(char.isdigit() for char in name):
                filtered_results.append({
                    'name': result.get('SEARCHVAL', ''),
                    'address': result.get('ADDRESS', ''),
                    'lat': float(result.get('LATITUDE', 0)),
                    'lng': float(result.get('LONGITUDE', 0)),
                    'type': 'hdb_block',
                    'planning_area': planning_area
                })
        
        return filtered_results
    except Exception as e:
        print(f"Error processing HDB data for {planning_area}: {e}")
        return []

def estimate_area_for_location(location: Dict) -> float:
    """Estimate area for a location based on its type"""
    location_type = location.get('type', '')
    
    # Enhanced area estimates based on location type
    area_estimates = {
        'park_open_space': 300,  # sqm
        'carpark': 250,  # sqm
        'hdb_block': 200,  # sqm (void deck)
        'recreation_centre': 280,  # sqm (sports hall)
        'school': 320,  # sqm (rooftop/underutilized space)
        'soccer_court': 400,  # sqm (existing court)
        'rooftop': 300,  # sqm (rooftop space)
        'industrial_space': 350,  # sqm (warehouse/industrial area)
    }
    
    return area_estimates.get(location_type, 200)

def determine_surface_type(location: Dict) -> str:
    """Determine surface type based on location type"""
    location_type = location.get('type', '')
    
    surface_types = {
        'park_open_space': 'grass field',
        'carpark': 'asphalt',
        'hdb_block': 'concrete void deck',
        'recreation_centre': 'concrete sports hall',
        'school': 'concrete rooftop/asphalt',
        'soccer_court': 'grass field',
        'rooftop': 'concrete rooftop',
        'industrial_space': 'concrete/asphalt',
    }
    
    return surface_types.get(location_type, 'unknown')

def determine_current_use(location: Dict) -> str:
    """Determine current use based on location type"""
    location_type = location.get('type', '')
    
    current_uses = {
        'park_open_space': 'open recreational space',
        'carpark': 'parking (potentially underutilized)',
        'hdb_block': 'community space (void deck)',
        'recreation_centre': 'sports facilities (may be underutilized)',
        'school': 'school facilities (after-hours potential)',
        'soccer_court': 'soccer field (may be underutilized)',
        'rooftop': 'rooftop space (underutilized)',
        'industrial_space': 'industrial/commercial space (may be underutilized)',
    }
    
    return current_uses.get(location_type, 'unknown')

def determine_land_owner(location: Dict) -> str:
    """Determine likely land owner based on location type"""
    location_type = location.get('type', '')
    
    owners = {
        'park_open_space': 'NParks',
        'carpark': 'NParks/HDB/Private',
        'hdb_block': 'HDB',
        'recreation_centre': 'PA (People\'s Association)',
        'school': 'MOE/Private School',
        'soccer_court': 'NParks/HDB/Private',
        'rooftop': 'Private/Commercial',
        'industrial_space': 'Private/Industrial',
    }
    
    return owners.get(location_type, 'Unknown')

def determine_permission_required(location: Dict) -> str:
    """Determine who permission is required from"""
    location_type = location.get('type', '')
    
    permissions = {
        'park_open_space': 'NParks',
        'carpark': 'NParks/HDB/Private Management',
        'hdb_block': 'Town Council',
        'recreation_centre': 'PA (People\'s Association)',
        'school': 'School Management/MOE',
        'soccer_court': 'NParks/HDB/Private Management',
        'rooftop': 'Building Management/Private Owner',
        'industrial_space': 'Industrial Estate Management/Private Owner',
    }
    
    return permissions.get(location_type, 'Unknown')

def assess_residential_proximity(location: Dict, hdb_blocks: List[Dict]) -> str:
    """Assess residential proximity to HDB blocks"""
    if not hdb_blocks:
        return "Unknown"
    
    location_coords = (location['lat'], location['lng'])
    min_distance = float('inf')
    
    for hdb in hdb_blocks:
        hdb_coords = (hdb['lat'], hdb['lng'])
        # Simple distance calculation using Haversine formula
        lat1, lon1 = math.radians(location_coords[0]), math.radians(location_coords[1])
        lat2, lon2 = math.radians(hdb_coords[0]), math.radians(hdb_coords[1])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        distance = 6371 * c * 1000  # Convert to meters
        
        if distance < min_distance:
            min_distance = distance
    
    if min_distance < 200:
        return f"HDB within {min_distance:.0f}m"
    elif min_distance < 500:
        return f"HDB within {min_distance:.0f}m"
    else:
        return f"HDB within {min_distance:.0f}m"

def assess_site_suitability(location: Dict) -> Dict:
    """Assess the suitability of a site for a padel court"""
    suitability_score = 0
    reasons = []
    
    # Check area
    area = location.get('area_estimate_sqm', 0)
    if area >= PADEL_COURT_MIN_AREA:
        suitability_score += 30
        reasons.append(f"Sufficient area ({area:.0f} sqm)")
    else:
        reasons.append(f"Insufficient area ({area:.0f} sqm)")
    
    # Check surface type
    surface_type = location.get('surface_type', '').lower()
    if 'concrete' in surface_type or 'asphalt' in surface_type:
        suitability_score += 25
        reasons.append("Suitable surface type")
    elif 'grass' in surface_type:
        suitability_score += 15
        reasons.append("Grass surface (may need modification)")
    else:
        reasons.append(f"Surface type: {surface_type}")
    
    # Check accessibility
    accessibility = location.get('accessibility', 'public access')
    if 'public' in accessibility.lower():
        suitability_score += 20
        reasons.append("Good accessibility")
    else:
        reasons.append(f"Accessibility: {accessibility}")
    
    # Check residential proximity
    residential_proximity = location.get('residential_proximity', '')
    if 'HDB' in residential_proximity and 'within' in residential_proximity:
        distance_str = residential_proximity.split('within')[1].strip()
        try:
            distance = float(distance_str.replace('m', ''))
            if distance <= 300:
                suitability_score += 15
                reasons.append("Near residential areas")
            else:
                reasons.append(f"Residential proximity: {residential_proximity}")
        except:
            reasons.append(f"Residential proximity: {residential_proximity}")
    else:
        reasons.append(f"Residential proximity: {residential_proximity}")
    
    # Check current use
    current_use = location.get('current_use', '').lower()
    if 'underutilized' in current_use or 'parking' in current_use or 'after-hours' in current_use:
        suitability_score += 10
        reasons.append("Underutilized space")
    else:
        reasons.append(f"Current use: {current_use}")
    
    return {
        'suitability_score': suitability_score,
        'reasons': reasons,
        'recommendation': 'High' if suitability_score >= 70 else 'Medium' if suitability_score >= 50 else 'Low'
    }

def remove_duplicates(locations: List[Dict]) -> List[Dict]:
    """Remove duplicate locations based on name, coordinates, and type"""
    print("Removing duplicates...")
    
    # Create a set to track unique combinations
    seen = set()
    unique_locations = []
    
    for location in locations:
        # Create a unique key based on name, coordinates, and type
        name = location.get('name', '').lower().strip()
        lat = round(location.get('lat', 0), 6)  # Round to 6 decimal places (~1 meter precision)
        lng = round(location.get('lng', 0), 6)
        loc_type = location.get('type', '')
        
        # Create unique key
        unique_key = f"{name}_{lat}_{lng}_{loc_type}"
        
        if unique_key not in seen:
            seen.add(unique_key)
            unique_locations.append(location)
        else:
            print(f"Removed duplicate: {location.get('name', 'Unknown')}")
    
    print(f"Removed {len(locations) - len(unique_locations)} duplicates")
    return unique_locations

def search_all_locations_for_area(planning_area: str) -> List[Dict]:
    """Search for all potential locations in a planning area"""
    print(f"\n=== Searching {planning_area} ===")
    
    all_locations = []
    
    # Search for different types of locations
    parks = search_parks_and_open_spaces(planning_area)
    carparks = search_carparks(planning_area)
    hdb_blocks = search_hdb_blocks(planning_area)
    recreation_centres = search_recreation_centres(planning_area)
    schools = search_schools(planning_area)
    soccer_courts = search_soccer_courts(planning_area)
    rooftops = search_rooftops(planning_area)
    industrial_spaces = search_industrial_spaces(planning_area)
    
    # Combine all locations
    all_raw_locations = (parks + carparks + hdb_blocks + recreation_centres + 
                        schools + soccer_courts + rooftops + industrial_spaces)
    
    # Process each location
    for location in all_raw_locations:
        # Add additional information
        location['area_estimate_sqm'] = estimate_area_for_location(location)
        location['surface_type'] = determine_surface_type(location)
        location['current_use'] = determine_current_use(location)
        location['land_owner'] = determine_land_owner(location)
        location['likely_permission_required_from'] = determine_permission_required(location)
        location['accessibility'] = 'public access'
        location['residential_proximity'] = assess_residential_proximity(location, hdb_blocks)
        
        # Add links
        location['ura_space_link'] = "https://www.ura.gov.sg/maps/"
        location['onemap_link'] = f"https://www.onemap.gov.sg/main/v2/?lat={location['lat']}&lng={location['lng']}"
        
        # Assess suitability
        assessment = assess_site_suitability(location)
        location.update(assessment)
        
        all_locations.append(location)
    
    print(f"Found {len(all_locations)} potential locations in {planning_area}")
    return all_locations

def create_interactive_map(locations: List[Dict]):
    """Create an interactive map showing potential padel court locations with high-resolution satellite"""
    # Create base map centered on Singapore
    m = folium.Map(
        location=[1.3521, 103.8198], 
        zoom_start=11
    )
    
    # Add high-resolution satellite layers
    # Google Satellite (highest resolution)
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        attr='Google Satellite',
        name='Google Satellite (High Res)',
        overlay=False
    ).add_to(m)
    
    # Bing Satellite (alternative high-resolution option)
    folium.TileLayer(
        tiles='https://ecn.t3.tiles.virtualearth.net/tiles/a{q}.jpeg?g=1',
        attr='Bing Satellite',
        name='Bing Satellite',
        overlay=False
    ).add_to(m)
    
    # Esri World Imagery (another high-resolution option)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri World Imagery',
        name='Esri World Imagery',
        overlay=False
    ).add_to(m)
    
    # Google Streets as reference
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
        attr='Google Streets',
        name='Google Streets',
        overlay=False
    ).add_to(m)
    
    # Add planning area boundaries
    try:
        with open('planning_areas_boundaries.geojson', 'r') as f:
            boundaries = json.load(f)
        folium.GeoJson(
            boundaries,
            name='Planning Areas',
            style_function=lambda x: {
                'fillColor': '#ffffcc',
                'color': '#000000',
                'weight': 1,
                'fillOpacity': 0.1
            }
        ).add_to(m)
    except FileNotFoundError:
        print("Planning area boundaries file not found")
    
    # Group locations by type for different colors
    location_types = {
        'park_open_space': 'green',
        'carpark': 'blue',
        'hdb_block': 'red',
        'recreation_centre': 'purple',
        'school': 'orange',
        'soccer_court': 'darkgreen',
        'rooftop': 'darkblue',
        'industrial_space': 'gray'
    }
    
    # Add padel court locations
    for i, location in enumerate(locations):
        # Determine marker color based on type and suitability
        location_type = location.get('type', '')
        base_color = location_types.get(location_type, 'gray')
        score = location.get('suitability_score', 0)
        
        # Adjust color based on suitability score
        if score >= 70:
            color = base_color
        elif score >= 50:
            color = 'orange'
        else:
            color = 'red'
        
        # Create popup content with enhanced information
        popup_content = f"""
        <div style="width: 300px;">
            <h4 style="margin: 0 0 10px 0; color: #333;">{location['name']}</h4>
            <table style="width: 100%; font-size: 12px;">
                <tr><td><strong>Type:</strong></td><td>{location_type.replace('_', ' ').title()}</td></tr>
                <tr><td><strong>Score:</strong></td><td>{score}/100 ({location.get('recommendation', 'Unknown')})</td></tr>
                <tr><td><strong>Area:</strong></td><td>{location['area_estimate_sqm']} sqm</td></tr>
                <tr><td><strong>Surface:</strong></td><td>{location['surface_type']}</td></tr>
                <tr><td><strong>Current Use:</strong></td><td>{location['current_use']}</td></tr>
                <tr><td><strong>Residential:</strong></td><td>{location['residential_proximity']}</td></tr>
                <tr><td><strong>Accessibility:</strong></td><td>{location['accessibility']}</td></tr>
                <tr><td><strong>Land Owner:</strong></td><td>{location['land_owner']}</td></tr>
                <tr><td><strong>Permission:</strong></td><td>{location['likely_permission_required_from']}</td></tr>
                <tr><td><strong>Address:</strong></td><td>{location['address']}</td></tr>
            </table>
            <div style="margin-top: 10px; font-size: 11px; color: #666;">
                <strong>Reasons:</strong> {', '.join(location.get('reasons', []))}
            </div>
        </div>
        """
        
        folium.Marker(
            location=[location['lat'], location['lng']],
            popup=folium.Popup(popup_content, max_width=350),
            tooltip=f"{location['name']} (Score: {score})",
            icon=folium.Icon(color=color, icon='info-sign')
        ).add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Add fullscreen option
    plugins.Fullscreen().add_to(m)
    
    # Add minimap
    minimap = plugins.MiniMap(toggle_display=True)
    m.add_child(minimap)
    
    return m

def save_results_to_csv(locations: List[Dict], filename: str = 'padel_court_locations_CLEAN_HIGHRES.csv'):
    """Save the results to a CSV file"""
    df = pd.DataFrame(locations)
    df.to_csv(filename, index=False)
    print(f"Results saved to {filename}")

def generate_next_steps_report(locations: List[Dict]) -> str:
    """Generate a report with next steps for each location"""
    report = "# Padel Court Location Analysis - Clean Data with High-Resolution Satellite\n\n"
    
    # Group by land owner
    owners = {}
    for location in locations:
        owner = location['land_owner']
        if owner not in owners:
            owners[owner] = []
        owners[owner].append(location)
    
    for owner, owner_locations in owners.items():
        report += f"## {owner} Properties ({len(owner_locations)} locations)\n\n"
        
        for location in owner_locations:
            report += f"### {location['name']}\n"
            report += f"- **Type:** {location['type'].replace('_', ' ').title()}\n"
            report += f"- **Suitability Score:** {location['suitability_score']}/100\n"
            report += f"- **Area:** {location['area_estimate_sqm']} sqm\n"
            report += f"- **Surface:** {location['surface_type']}\n"
            report += f"- **Current Use:** {location['current_use']}\n"
            report += f"- **Address:** {location['address']}\n"
            report += f"- **Permission Required From:** {location['likely_permission_required_from']}\n\n"
            
            # Add specific next steps based on owner
            if 'NParks' in owner:
                report += "**Next Steps:**\n"
                report += "1. Contact NParks for temporary recreational use permit\n"
                report += "2. Submit detailed proposal including safety measures\n"
                report += "3. Consider seasonal or off-peak usage to minimize disruption\n"
                report += "4. Ensure compliance with park regulations and noise restrictions\n\n"
            elif 'HDB' in owner:
                report += "**Next Steps:**\n"
                report += "1. Contact Town Council for void deck usage approval\n"
                report += "2. Submit community benefit proposal\n"
                report += "3. Address resident concerns about noise and access\n"
                report += "4. Consider timing restrictions (e.g., 9 AM - 9 PM)\n\n"
            elif 'PA' in owner:
                report += "**Next Steps:**\n"
                report += "1. Contact People's Association for recreation centre usage\n"
                report += "2. Propose community sports program integration\n"
                report += "3. Demonstrate community engagement benefits\n"
                report += "4. Consider after-hours or weekend usage\n\n"
            elif 'MOE' in owner or 'School' in owner:
                report += "**Next Steps:**\n"
                report += "1. Contact school management for after-hours facility usage\n"
                report += "2. Propose community education and sports program\n"
                report += "3. Address security and access control requirements\n"
                report += "4. Consider revenue-sharing with school\n\n"
            elif 'Private' in owner:
                report += "**Next Steps:**\n"
                report += "1. Contact building/property management\n"
                report += "2. Propose revenue-sharing or rental agreement\n"
                report += "3. Demonstrate commercial viability and community benefit\n"
                report += "4. Address security and access control requirements\n\n"
            else:
                report += "**Next Steps:**\n"
                report += "1. Research specific approval process for this land owner\n"
                report += "2. Contact relevant government agency or private entity\n"
                report += "3. Prepare comprehensive proposal with community benefits\n"
                report += "4. Address any specific requirements or restrictions\n\n"
    
    return report

def main():
    print("=== Singapore Padel Court Location Finder (Clean Data + High-Resolution Satellite) ===\n")
    
    all_locations = []
    
    # Search in all planning areas
    selected_areas = PLANNING_AREAS
    
    for area in selected_areas:
        try:
            locations = search_all_locations_for_area(area)
            all_locations.extend(locations)
            time.sleep(1)  # Be respectful to the API
        except Exception as e:
            print(f"Error searching {area}: {e}")
            continue
    
    # Remove duplicates
    all_locations = remove_duplicates(all_locations)
    
    # Sort by suitability score (highest first)
    all_locations.sort(key=lambda x: x['suitability_score'], reverse=True)
    
    # Show all locations
    top_locations = all_locations
    
    print(f"\nFound {len(all_locations)} total unique locations")
    print(f"Selected {len(top_locations)} locations for analysis")
    
    # Create interactive map
    print("Creating interactive map with high-resolution satellite view...")
    m = create_interactive_map(top_locations)
    m.save('padel_court_locations_CLEAN_HIGHRES_SATELLITE.html')
    print("Map saved as padel_court_locations_CLEAN_HIGHRES_SATELLITE.html")
    
    # Save results to CSV
    save_results_to_csv(top_locations)
    
    # Generate next steps report
    print("Generating next steps report...")
    report = generate_next_steps_report(top_locations)
    with open('padel_court_next_steps_CLEAN_HIGHRES.md', 'w') as f:
        f.write(report)
    print("Next steps report saved as padel_court_next_steps_CLEAN_HIGHRES.md")
    
    # Print summary
    print("\n=== SUMMARY ===")
    print(f"Total unique locations analyzed: {len(all_locations)}")
    print(f"Locations selected: {len(top_locations)}")
    print(f"High suitability (≥70): {len([l for l in top_locations if l['suitability_score'] >= 70])}")
    print(f"Medium suitability (50-69): {len([l for l in top_locations if 50 <= l['suitability_score'] < 70])}")
    print(f"Low suitability (<50): {len([l for l in top_locations if l['suitability_score'] < 50])}")
    
    # Group by type
    type_counts = {}
    for location in top_locations:
        loc_type = location.get('type', 'unknown')
        type_counts[loc_type] = type_counts.get(loc_type, 0) + 1
    
    print("\nLocations by type:")
    for loc_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"- {loc_type.replace('_', ' ').title()}: {count}")
    
    print("\nTop 5 locations by suitability:")
    for i, location in enumerate(top_locations[:5]):
        print(f"{i+1}. {location['name']} ({location['type'].replace('_', ' ').title()}) (Score: {location['suitability_score']})")
    
    print("\n=== FILES GENERATED ===")
    print("- padel_court_locations_CLEAN_HIGHRES_SATELLITE.html (Interactive map with high-res satellite)")
    print("- padel_court_locations_CLEAN_HIGHRES.csv (Clean data for all unique locations)")
    print("- padel_court_next_steps_CLEAN_HIGHRES.md (Next steps report)")

if __name__ == "__main__":
    main() 