# Washington State Wildfire Data Analysis

## Overview
This project analyzes the relationship between climate factors and wildfire occurrences in Washington State. By integrating data from multiple sources including NOAA climate records, fire incident reports, and FEMA disaster declarations, this analysis aims to identify patterns and correlations that could inform wildfire prevention and management strategies.

## Features
- Data integration from multiple sources (climate, fire incidents, FEMA declarations)
- Automated processing of raw data into analysis-ready formats
- Visualization of temporal trends in fire incidents and climate variables
- Correlation analysis between climate factors and wildfire occurrences
- Regional breakdown of fire incidents (Eastern vs. Western Washington)
- Comparison of fire incidents with official disaster declarations

## Installation

### Prerequisites
- Python 3.7+
- pandas
- numpy
- matplotlib

### Setup
1. Clone this repository:
```bash
git clone https://github.com/yourusername/wa-wildfire-analysis.git
cd wa-wildfire-analysis
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Create the necessary directory structure:
```bash
mkdir -p data/raw data/processed data/output
```

## Data Sources
To use this project, you'll need to place the following data files in the `data/raw` directory:

1. `wa_climate_data.csv` - NOAA climate data for Washington State
2. `wa_fire_history.csv` - Historical fire incident data
3. `wa_fema_wildfire_declarations.csv` - FEMA disaster declarations related to wildfires

### Data Format Requirements

#### Climate Data (`wa_climate_data.csv`)
Should contain columns including:
- `date` - Date of measurement
- `datatype` - Type of climate data (TMAX, TMIN, PRCP)
- `value` - Measured value
- `station` - Weather station identifier

#### Fire Data (`wa_fire_history.csv`)
Should contain columns including:
- `acq_date` - Date of fire detection
- `is_eastern` (optional) - Boolean indicating if the fire was in Eastern Washington

#### FEMA Data (`wa_fema_wildfire_declarations.csv`)
Should contain columns including:
- `declarationDate` - Date of disaster declaration
- `incidentBeginDate` - Date the fire incident began
- `incidentEndDate` - Date the fire incident ended

## Usage
Run the main analysis script:
```bash
python data_integration.py
```

The script will:
1. Load data from the `data/raw` directory
2. Process and clean each dataset
3. Generate visualizations and save them to `data/output`
4. Save processed data to `data/processed`

## Output
The analysis generates several visualizations:

- **Temperature trends** - Annual average temperatures in Washington
- **Fire incidents by year** - Yearly count of fire incidents
- **Regional fire analysis** - Comparison of Eastern vs. Western Washington fire incidents
- **Temperature-fire correlation** - Scatter plot with trend line
- **Precipitation-fire correlation** - Scatter plot with trend line
- **Fire-FEMA comparison** - Dual-axis chart comparing fire incidents with disaster declarations

## Project Structure
```
wa-wildfire-analysis/
├── data/
│   ├── raw/             # Input data files
│   ├── processed/       # Cleaned and processed data
│   └── output/          # Visualizations and analysis results
├── data_integration.py  # Main analysis script
├── requirements.txt     # Project dependencies
├── LICENSE              # License information
└── README.md           # Project documentation
```

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- NOAA for climate data
- FEMA for disaster declaration records
- [Add other data sources or inspirations]
