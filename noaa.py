# noaa_fixed.py - With smaller date range
import os
import requests
import pandas as pd
from datetime import datetime, timedelta
import json

# Make sure data directory exists
os.makedirs('data/raw', exist_ok=True)

# NOAA's Climate Data Online API
base_url = "https://www.ncdc.noaa.gov/cdo-web/api/v2/"
token = "afkLiuFjadLNNSohCAwjaBBgeJKJHUDR"  # Get yours from https://www.ncdc.noaa.gov/cdo-web/token

# Set headers with token
headers = {"token": token}

def test_api_connection():
    """Test if we can connect to the NOAA API"""
    try:
        # Try a simple request to test connection
        test_url = f"{base_url}datasets"
        response = requests.get(test_url, headers=headers, timeout=10)
        if response.status_code == 200:
            print("Successfully connected to NOAA API!")
            return True
        else:
            print(f"API connection error: Status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return False

def get_washington_stations():
    """Get weather stations in Washington state with error handling"""
    try:
        # The API requires a date range even for station queries
        # Use a 1-year period for station query
        current_year = datetime.now().year
        start_date = f"{current_year-1}-01-01"
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        # Get Washington state stations that record temperature, precipitation
        stations_url = f"{base_url}stations"
        station_params = {
            "locationid": "FIPS:53",  # Washington State FIPS code
            "datatypeid": "TMAX,TMIN,PRCP",
            "startdate": start_date,
            "enddate": end_date,
            "limit": 1000
        }
        
        print(f"Fetching stations data for period {start_date} to {end_date}...")
        station_response = requests.get(stations_url, headers=headers, params=station_params, timeout=30)
        
        # Check response status
        if station_response.status_code != 200:
            print(f"API Error: Status code {station_response.status_code}")
            print(f"Response: {station_response.text}")
            return None
            
        # Parse response
        stations_data = station_response.json()
        
        # Check if results key exists
        if 'results' not in stations_data:
            print("API response doesn't contain 'results' key")
            print(f"Response keys: {stations_data.keys()}")
            return []
        
        # Success - get station IDs
        stations = stations_data["results"]
        print(f"Found {len(stations)} NOAA weather stations in Washington")
        
        # Save stations to file
        with open('data/raw/wa_noaa_stations.json', 'w') as f:
            json.dump(stations, f)
            
        # Return stations with their IDs and names
        return [(station["id"], station.get("name", "Unnamed Station")) for station in stations]
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching station data: {e}")
        return None

def get_station_data_by_month(station_id, station_name, year, month):
    """
    Get climate data for a specific station for a single month
    """
    try:
        # Create start and end dates for the month
        if month == 12:
            next_month_year = year + 1
            next_month = 1
        else:
            next_month_year = year
            next_month = month + 1
            
        start_date = f"{year}-{month:02d}-01"
        
        # Calculate end date (first day of next month - 1 day)
        temp_end_date = datetime(next_month_year, next_month, 1) - timedelta(days=1)
        end_date = temp_end_date.strftime("%Y-%m-%d")
        
        print(f"  Requesting data for {start_date} to {end_date}")
        
        data_url = f"{base_url}data"
        data_params = {
            "datasetid": "GHCND",  # Global Historical Climatology Network Daily
            "stationid": station_id,
            "startdate": start_date,
            "enddate": end_date,
            "datatypeid": "TMAX,TMIN,PRCP",
            "units": "standard",
            "limit": 1000
        }
        
        data_response = requests.get(data_url, headers=headers, params=data_params, timeout=30)
        
        if data_response.status_code != 200:
            print(f"  Error fetching data: {data_response.status_code}")
            print(f"  Response: {data_response.text[:200]}...")  # Print first 200 chars of response
            return []
            
        station_data = data_response.json()
        
        if 'results' not in station_data:
            print(f"  No results found for this period")
            return []
            
        # Add station name to each record
        for record in station_data['results']:
            record['station_name'] = station_name
            
        print(f"  Retrieved {len(station_data['results'])} records")
        return station_data['results']
        
    except requests.exceptions.RequestException as e:
        print(f"  Network error: {e}")
        return []
    except Exception as e:
        print(f"  Unexpected error: {e}")
        return []

def get_multi_station_data():
    """Get climate data for multiple stations with proper date handling"""
    # Get stations
    stations = get_washington_stations()
    
    if not stations:
        print("No stations found")
        return
    
    all_data = []
    
    # Process only first 2 stations and last 2 years for testing
    # Use a much smaller period than before
    current_year = datetime.now().year
    years_to_process = [current_year - 1, current_year]  # Last 2 years only
    
    # Process first 2 stations only
    for i, (station_id, station_name) in enumerate(stations[:2]):
        print(f"Processing station {i+1}/2: {station_id} ({station_name})")
        
        station_data = []
        
        # Get data month by month to stay within API limits
        for year in years_to_process:
            for month in range(1, 13):
                # Skip future months
                if year == current_year and month > datetime.now().month:
                    continue
                    
                print(f"  Fetching data for {year}-{month:02d}")
                month_data = get_station_data_by_month(station_id, station_name, year, month)
                station_data.extend(month_data)
                
                # Add a small delay to avoid overwhelming the API
                import time
                time.sleep(0.5)
        
        print(f"  Total records for station {station_id}: {len(station_data)}")
        all_data.extend(station_data)
    
    # Convert to DataFrame and save
    if all_data:
        climate_df = pd.DataFrame(all_data)
        print(f"Total records retrieved: {len(climate_df)}")
        climate_df.to_csv('data/raw/wa_climate_data.csv', index=False)
        return climate_df
    else:
        print("No climate data retrieved")
        return pd.DataFrame()

# Main execution flow
if __name__ == "__main__":
    print("Testing API connection...")
    if not test_api_connection():
        print("Exiting due to connection issues")
        exit(1)
    
    print("\nFetching and processing NOAA climate data...")
    climate_data = get_multi_station_data()
    
    if not climate_data.empty:
        print("\nData retrieval successful!")
        print(f"Data saved to data/raw/wa_climate_data.csv")
        
        # Print a summary of the data
        print("\nData Summary:")
        print(f"Time period: {climate_data['date'].min()} to {climate_data['date'].max()}")
        
        # Count records by data type
        if 'datatype' in climate_data.columns:
            datatype_counts = climate_data['datatype'].value_counts()
            print("\nRecord counts by data type:")
            for dtype, count in datatype_counts.items():
                print(f"  {dtype}: {count}")
    else:
        print("\nNo data was retrieved. Please check the error messages above.")
