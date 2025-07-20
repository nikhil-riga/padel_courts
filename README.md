# Singapore Padel Court Location Finder 🏓

A comprehensive analysis tool to identify potential locations for pop-up padel courts across Singapore using OneMap APIs and ultra high-resolution satellite imagery.

## 🎯 Project Overview

This project analyzes 555 potential locations across Singapore suitable for installing pop-up padel courts (~200 sqm), focusing on areas near HDB estates, condominiums, and public open land. The analysis includes detailed site identification, suitability scoring, and interactive mapping with ultra high-resolution satellite imagery.

## 📊 Key Findings

- **555 unique locations** identified across all 34 planning areas
- **347 high suitability** locations (≥70 score)
- **208 medium suitability** locations (50-69 score)
- **Multiple location types** analyzed: parks, carparks, schools, industrial spaces, recreation centres, rooftops, and HDB blocks

## 🗺️ Interactive Maps

### Main Map: `SIMPLE_ULTRA_MAP_BY_TYPE.html`
- **Ultra high-resolution satellite imagery** (Google + Esri)
- **Color-coded markers** by location type
- **555 padel court locations** with detailed popups
- **Maximum zoom level 20** for street-level analysis
- **Layer control** to switch between satellite and street views

### Location Types & Colors:
- 🟢 **GREEN**: Park Open Space (208 locations)
- 🔵 **BLUE**: Carpark (131 locations)
- 🔴 **RED**: HDB Block
- 🟣 **PURPLE**: Recreation Centre (5 locations)
- 🟠 **ORANGE**: School (100 locations)
- 🟢 **DARKGREEN**: Soccer Court
- 🔵 **DARKBLUE**: Rooftop
- ⚫ **GRAY**: Industrial Space (111 locations)

## 📁 Project Structure

```
├── SIMPLE_ULTRA_MAP_BY_TYPE.html          # Main interactive map
├── padel_court_locations_CLEAN_HIGHRES.csv # Clean location data (555 locations)
├── simple_ultra_map.py                    # Main mapping script
├── padel_court_finder_clean_highres.py    # Data collection script
├── requirements.txt                       # Python dependencies
└── README.md                             # This file
```

## 🚀 Quick Start

1. **View the Map**: Open `SIMPLE_ULTRA_MAP_BY_TYPE.html` in your browser
2. **Explore Locations**: Click markers for detailed information
3. **Switch Views**: Use layer control for different satellite imagery
4. **Zoom In**: Use maximum zoom (20x) for detailed site analysis

## 🔧 Technical Details

### Data Sources
- **OneMap APIs**: Singapore's national geospatial platform
- **URA SPACE**: Urban Redevelopment Authority planning data
- **Google Satellite**: Ultra high-resolution imagery
- **Esri World Imagery**: Professional grade satellite data

### Analysis Criteria
- **Minimum Area**: 200 sqm (padel court requirement)
- **Surface Type**: Concrete, asphalt, or grass
- **Accessibility**: Public access preferred
- **Residential Proximity**: Near HDB blocks and residential areas
- **Current Use**: Underutilized spaces prioritized

### Suitability Scoring (0-100)
- **Area Sufficiency** (30 points)
- **Surface Type** (25 points)
- **Accessibility** (20 points)
- **Residential Proximity** (15 points)
- **Current Use** (10 points)

## 📈 Location Distribution

| Location Type | Count | Percentage |
|---------------|-------|------------|
| Park Open Space | 208 | 37.5% |
| Carpark | 131 | 23.6% |
| Industrial Space | 111 | 20.0% |
| School | 100 | 18.0% |
| Recreation Centre | 5 | 0.9% |

## 🎯 Next Steps

The analysis provides actionable insights for:
- **NParks**: Temporary recreational use permits
- **HDB/Town Councils**: Void deck and community space usage
- **Schools**: After-hours facility utilization
- **Private Owners**: Commercial space optimization

## 🔍 Features

- **Ultra High-Resolution Satellite**: Zoom to street level for detailed analysis
- **Multiple Satellite Providers**: Google, Esri, and Bing imagery
- **Interactive Popups**: Detailed location information
- **Feature Groups**: Filter by location type
- **Measurement Tools**: Area and distance calculations
- **Fullscreen Mode**: Enhanced viewing experience
- **Minimap**: Navigation assistance

## 📋 Requirements

```bash
pip install -r requirements.txt
```

## 🤝 Contributing

This project is open for contributions. Please feel free to:
- Improve the analysis algorithms
- Add new data sources
- Enhance the mapping interface
- Suggest additional location types

## 📄 License

This project is for educational and research purposes. Please respect Singapore's data usage policies and OneMap API terms of service.

---

**Created for Singapore Padel Court Location Analysis** 🏓🇸🇬 