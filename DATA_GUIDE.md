# Data Guide

This document provides detailed information about the data sources used in this project, their formats, and how to obtain or prepare the data files.

## Data Sources

### 1. NOAA Climate Data (`wa_climate_data.csv`)

#### Description
Historical temperature and precipitation data from NOAA weather stations across Washington State.

#### How to Obtain
1. Visit the NOAA Climate Data Online portal: https://www.ncdc.noaa.gov/cdo-web/
2. Request daily summaries for Washington State stations
3. Select the following elements:
   - TMAX (Maximum temperature)
   - TMIN (Minimum temperature)
   - PRCP (Precipitation)
4. Download the data in CSV format
5. Save as `wa_climate_data.csv` in the `data/raw` directory

#### Format Specifications
The script expects the following columns:
- `date` - Date of observation (YYYY-MM-DD)
- `datatype` - Type of measurement (TMAX, TMIN, PRCP)
- `value` - Measured value (tenths of degrees C for temperature, tenths of mm for precipitation)
- `station` - Station identifier

Additional useful columns (if available):
- `station_name` - Weather station name
- `station_latitude` - Station latitude coordinates
- `station_longitude` - Station longitude coordinates

#### Example Data
```
date,station,datatype,value
2015-01-01,GHCND:USW00024233,TMAX,82
2015-01-01,GHCND:USW00024233,TMIN,33
2015-01-01,GHCND:USW00024233,PRCP,142
```

### 2. Fire History Data (`wa_fire_history.csv`)

#### Description
Historical fire incident data for Washington State, typically sourced from satellite detection systems or state agency records.

#### How to Obtain
1. Visit the NASA FIRMS (Fire Information for Resource Management System): https://firms.modaps.eosdis.nasa.gov/
2. Filter for Washington State boundaries
3. Download historical fire data
4. Process and save as `wa_fire_history.csv` in the `data/raw` directory

Alternatively, data may be available from:
- Washington Department of Natural Resources
- U.S. Forest Service Fire Detection and Monitoring

#### Format Specifications
The script expects the following columns:
- `acq_date` - Date fire was detected/reported (YYYY-MM-DD)

Optional but useful columns:
- `is_eastern` - Boolean (True/False) indicating if the fire was in Eastern Washington
- `latitude` - Latitude coordinates
- `longitude` - Longitude coordinates
- `confidence` - Detection confidence level
- `brightness` - Fire brightness
- `frp` - Fire Radiative Power

#### Example Data
```
acq_date,latitude,longitude,is_eastern,confidence
2018-07-15,47.8825,-120.1234,True,high
2018-07-16,47.9001,-120.1532,True,nominal
2018-07-17,48.1235,-122.3421,False,high
```

### 3. FEMA Disaster Declarations (`wa_fema_wildfire_declarations.csv`)

#### Description
Records of FEMA disaster declarations related to wildfires in Washington State.

#### How to Obtain
1. Visit the FEMA Disaster Declarations Summary: https://www.fema.gov/openfema-data-page/disaster-declarations-summaries-v2
2. Filter for Washington State and wildfire/fire disaster types
3. Download the filtered data
4. Save as `wa_fema_wildfire_declarations.csv` in the `data/raw` directory

#### Format Specifications
The script expects the following columns:
- `declarationDate` - Date of disaster declaration (YYYY-MM-DD)
- `incidentBeginDate` - Start date of the incident (YYYY-MM-DD)
- `incidentEndDate` - End date of the incident (YYYY-MM-DD)

Additional useful columns:
- `disasterNumber` - FEMA disaster identifier
- `county` - Affected county/counties
- `designatedArea` - Specific area designation
- `declarationType` - Type of declaration (Major Disaster, Emergency, etc.)

#### Example Data
```
disasterNumber,declarationDate,incidentBeginDate,incidentEndDate,county
4792,2020-09-17,2020-09-01,2020-09-19,Whitman
4751,2019-07-31,2019-07-15,2019-07-25,Okanogan
```

## Data Processing

The `data_integration.py` script performs the following transformations on the raw data:

### Climate Data Processing
1. Converts temperature values from tenths of degrees C to degrees C
2. Converts precipitation values from tenths of mm to mm
3. Calculates average temperature (TAVG) from maximum (TMAX) and minimum (TMIN)
4. Aggregates data to monthly and yearly averages

### Fire Data Processing
1. Extracts year and month from acquisition date
2. Counts fire incidents by year and region
3. Creates visualizations of temporal and regional patterns

### FEMA Data Processing
1. Extracts year from incident begin date
2. Counts disaster declarations by year
3. Creates temporal visualizations

### Integrated Analysis
1. Merges climate and fire data on year
2. Calculates correlations between climate factors and fire incidents
3. Compares fire incidents with FEMA disaster declarations
4. Generates visualizations of relationships between datasets

## Output Files

The script generates the following processed data files:

1. `wa_monthly_climate.csv` - Monthly climate averages
2. `wa_yearly_fires.csv` - Yearly fire incident counts
3. `wa_fire_climate_correlation.csv` - Merged fire and climate data
4. `wa_fire_fema_comparison.csv` - Comparison of fire incidents and disaster declarations

And the following visualizations:

1. `wa_temperature_trend.png` - Annual temperature trends
2. `fire_incidents_by_year.png` - Yearly fire incidents
3. `fire_incidents_by_region.png` - Regional fire analysis
4. `temperature_fire_correlation.png` - Correlation between temperature and fires
5. `precipitation_fire_correlation.png` - Correlation between precipitation and fires
6. `fire_fema_comparison.png` - Comparison of fire incidents and disaster declarations
