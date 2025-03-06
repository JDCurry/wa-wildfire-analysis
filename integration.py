# data_integration.py - Fixed script for climate and fire data
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# Create directory for processed data and visualizations
os.makedirs('data/processed', exist_ok=True)
os.makedirs('data/output', exist_ok=True)

def load_data():
    """
    Load all collected data sources
    """
    data_files = {
        'fema': 'data/raw/wa_fema_wildfire_declarations.csv',
        'climate': 'data/raw/wa_climate_data.csv',
        'fires': 'data/raw/wa_fire_history.csv'
    }
    
    data = {}
    
    # Check if files exist and load them
    for key, file_path in data_files.items():
        if os.path.exists(file_path):
            print(f"Loading {key} data from {file_path}")
            data[key] = pd.read_csv(file_path)
            print(f"  {len(data[key])} records loaded")
        else:
            print(f"Warning: {file_path} not found")
            data[key] = pd.DataFrame()  # Empty dataframe
    
    return data

def process_fema_data(fema_df):
    """
    Process and analyze FEMA disaster declarations
    """
    if fema_df.empty:
        print("No FEMA data available to process")
        return fema_df
    
    print("\nProcessing FEMA disaster declarations...")
    
    # Convert date columns to datetime
    date_columns = ['declarationDate', 'incidentBeginDate', 'incidentEndDate']
    for col in date_columns:
        if col in fema_df.columns:
            fema_df[col] = pd.to_datetime(fema_df[col])
    
    # Extract year from incident begin date
    if 'incidentBeginDate' in fema_df.columns:
        fema_df['incident_year'] = fema_df['incidentBeginDate'].dt.year
        
        # Count declarations by year
        yearly_counts = fema_df['incident_year'].value_counts().sort_index()
        
        # Create a visualization
        plt.figure(figsize=(12, 6))
        yearly_counts.plot(kind='bar', color='firebrick')
        plt.title('FEMA Wildfire Disaster Declarations in Washington State by Year')
        plt.xlabel('Year')
        plt.ylabel('Number of Declarations')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig('data/output/fema_declarations_by_year.png')
        print(f"Visualization saved to data/output/fema_declarations_by_year.png")
    
    return fema_df

def process_climate_data(climate_df):
    """
    Process and analyze NOAA climate data - FIXED version
    """
    if climate_df.empty:
        print("No climate data available to process")
        return climate_df
    
    print("\nProcessing NOAA climate data...")
    
    # Print available columns for debugging
    print(f"Available climate data columns: {climate_df.columns.tolist()}")
    
    # Convert date column to datetime if it exists
    if 'date' in climate_df.columns:
        climate_df['date'] = pd.to_datetime(climate_df['date'])
        climate_df['year'] = climate_df['date'].dt.year
        climate_df['month'] = climate_df['date'].dt.month
    
    # Process temperature and precipitation data if we have datatype and value columns
    if 'datatype' in climate_df.columns and 'value' in climate_df.columns:
        print("Processing climate data by data type...")
        
        # Check what fields we have for pivot
        pivot_fields = ['date']
        if 'station' in climate_df.columns:
            pivot_fields.append('station')
        if 'station_name' in climate_df.columns:
            pivot_fields.append('station_name')
        
        # Only include latitude/longitude if they're in the data
        if 'station_latitude' in climate_df.columns:
            pivot_fields.append('station_latitude')
        if 'station_longitude' in climate_df.columns:
            pivot_fields.append('station_longitude')
        elif 'latitude' in climate_df.columns:
            pivot_fields.append('latitude')
        elif 'longitude' in climate_df.columns:
            pivot_fields.append('longitude')
        
        print(f"Using pivot fields: {pivot_fields}")
        
        # Pivot the data to get temperature and precipitation in separate columns
        if pivot_fields:
            climate_pivot = climate_df.pivot_table(
                index=pivot_fields,
                columns='datatype',
                values='value',
                aggfunc='first'
            ).reset_index()
            
            # If we have temperature data, convert from tenths of degrees C to degrees C
            if 'TMAX' in climate_pivot.columns:
                climate_pivot['TMAX'] = climate_pivot['TMAX'] / 10.0
            if 'TMIN' in climate_pivot.columns:
                climate_pivot['TMIN'] = climate_pivot['TMIN'] / 10.0
            
            # If we have precipitation data, convert from tenths of mm to mm
            if 'PRCP' in climate_pivot.columns:
                climate_pivot['PRCP'] = climate_pivot['PRCP'] / 10.0
            
            # Add derived columns
            if 'TMAX' in climate_pivot.columns and 'TMIN' in climate_pivot.columns:
                climate_pivot['TAVG'] = (climate_pivot['TMAX'] + climate_pivot['TMIN']) / 2
            
            # Add year and month columns for aggregation if not in index
            if 'date' in climate_pivot.columns:
                climate_pivot['year'] = pd.to_datetime(climate_pivot['date']).dt.year
                climate_pivot['month'] = pd.to_datetime(climate_pivot['date']).dt.month
            
            # Calculate monthly averages
            monthly_agg = {}
            if 'TMAX' in climate_pivot.columns:
                monthly_agg['TMAX'] = 'mean'
            if 'TMIN' in climate_pivot.columns:
                monthly_agg['TMIN'] = 'mean'
            if 'TAVG' in climate_pivot.columns:
                monthly_agg['TAVG'] = 'mean'
            if 'PRCP' in climate_pivot.columns:
                monthly_agg['PRCP'] = 'sum'
            
            if monthly_agg and 'year' in climate_pivot.columns and 'month' in climate_pivot.columns:
                monthly_avg = climate_pivot.groupby(['year', 'month']).agg(monthly_agg).reset_index()
                
                # Save processed climate data
                monthly_avg.to_csv('data/processed/wa_monthly_climate.csv', index=False)
                print(f"Processed climate data saved to data/processed/wa_monthly_climate.csv")
                
                # Create visualization of temperature trends
                if not monthly_avg.empty and 'TAVG' in monthly_avg.columns:
                    yearly_avg = monthly_avg.groupby('year').agg({
                        'TAVG': 'mean',
                        'PRCP': 'mean' if 'PRCP' in monthly_avg.columns else None
                    }).reset_index()
                    
                    # Temperature trend
                    plt.figure(figsize=(12, 6))
                    plt.plot(yearly_avg['year'], yearly_avg['TAVG'], marker='o', linestyle='-', color='red')
                    plt.title('Average Annual Temperature in Washington State')
                    plt.xlabel('Year')
                    plt.ylabel('Temperature (°C)')
                    plt.grid(True, linestyle='--', alpha=0.7)
                    plt.tight_layout()
                    plt.savefig('data/output/wa_temperature_trend.png')
                    print(f"Temperature trend visualization saved to data/output/wa_temperature_trend.png")
                
                return monthly_avg
        
        # If pivot table approach didn't work, fall back to simpler aggregation
        print("Falling back to simple aggregation method for climate data")
        
        if 'datatype' in climate_df.columns and 'value' in climate_df.columns:
            # Create separate dataframes for each data type
            tmax_df = climate_df[climate_df['datatype'] == 'TMAX'].copy()
            tmin_df = climate_df[climate_df['datatype'] == 'TMIN'].copy()
            prcp_df = climate_df[climate_df['datatype'] == 'PRCP'].copy()
            
            # Process by type if we have the data
            dfs_by_type = {}
            
            if not tmax_df.empty and 'date' in tmax_df.columns:
                tmax_df['date'] = pd.to_datetime(tmax_df['date'])
                tmax_df['year'] = tmax_df['date'].dt.year
                tmax_df['month'] = tmax_df['date'].dt.month
                tmax_df['TMAX'] = tmax_df['value'] / 10.0  # Convert from tenths of degrees
                tmax_monthly = tmax_df.groupby(['year', 'month'])['TMAX'].mean().reset_index()
                dfs_by_type['TMAX'] = tmax_monthly
            
            if not tmin_df.empty and 'date' in tmin_df.columns:
                tmin_df['date'] = pd.to_datetime(tmin_df['date'])
                tmin_df['year'] = tmin_df['date'].dt.year
                tmin_df['month'] = tmin_df['date'].dt.month
                tmin_df['TMIN'] = tmin_df['value'] / 10.0  # Convert from tenths of degrees
                tmin_monthly = tmin_df.groupby(['year', 'month'])['TMIN'].mean().reset_index()
                dfs_by_type['TMIN'] = tmin_monthly
            
            if not prcp_df.empty and 'date' in prcp_df.columns:
                prcp_df['date'] = pd.to_datetime(prcp_df['date'])
                prcp_df['year'] = prcp_df['date'].dt.year
                prcp_df['month'] = prcp_df['date'].dt.month
                prcp_df['PRCP'] = prcp_df['value'] / 10.0  # Convert from tenths of mm
                prcp_monthly = prcp_df.groupby(['year', 'month'])['PRCP'].sum().reset_index()
                dfs_by_type['PRCP'] = prcp_monthly
            
            # Merge the dataframes if we have any
            if dfs_by_type:
                merged_df = None
                for key, df in dfs_by_type.items():
                    if merged_df is None:
                        merged_df = df
                    else:
                        merged_df = pd.merge(merged_df, df, on=['year', 'month'], how='outer')
                
                if merged_df is not None:
                    # Add TAVG if we have TMAX and TMIN
                    if 'TMAX' in merged_df.columns and 'TMIN' in merged_df.columns:
                        merged_df['TAVG'] = (merged_df['TMAX'] + merged_df['TMIN']) / 2
                    
                    # Save processed climate data
                    merged_df.to_csv('data/processed/wa_monthly_climate.csv', index=False)
                    print(f"Processed climate data saved to data/processed/wa_monthly_climate.csv")
                    
                    return merged_df
    
    # If none of the above methods worked, return the original dataframe
    print("Warning: Could not process climate data with the expected structure")
    return climate_df

def process_fire_data(fire_df):
    """
    Process and analyze fire history data
    """
    if fire_df.empty:
        print("No fire history data available to process")
        return fire_df
    
    print("\nProcessing fire history data...")
    
    # Convert date column to datetime
    if 'acq_date' in fire_df.columns:
        fire_df['acq_date'] = pd.to_datetime(fire_df['acq_date'])
        fire_df['year'] = fire_df['acq_date'].dt.year
        fire_df['month'] = fire_df['acq_date'].dt.month
        
        # Count fires by year
        yearly_fires = fire_df.groupby('year').size().reset_index(name='fire_count')
        
        # Save processed fire data
        yearly_fires.to_csv('data/processed/wa_yearly_fires.csv', index=False)
        print(f"Processed fire data saved to data/processed/wa_yearly_fires.csv")
        
        # Create visualization
        plt.figure(figsize=(12, 6))
        plt.bar(yearly_fires['year'], yearly_fires['fire_count'], color='orange')
        plt.title('Fire Incidents in Washington State by Year')
        plt.xlabel('Year')
        plt.ylabel('Number of Fire Incidents')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig('data/output/fire_incidents_by_year.png')
        print(f"Fire incidents visualization saved to data/output/fire_incidents_by_year.png")
        
        # Also analyze by region if we have the data
        if 'is_eastern' in fire_df.columns:
            # Group by year and region
            region_fires = fire_df.groupby(['year', 'is_eastern']).size().reset_index(name='fire_count')
            
            # Create a more informative column for region
            region_fires['region'] = region_fires['is_eastern'].map({True: 'Eastern WA', False: 'Western WA'})
            
            # Create visualization
            plt.figure(figsize=(12, 6))
            
            # Get data for each region
            east_data = region_fires[region_fires['region'] == 'Eastern WA']
            west_data = region_fires[region_fires['region'] == 'Western WA']
            
            # Plot as side-by-side bars
            bar_width = 0.35
            years = sorted(region_fires['year'].unique())
            
            # Create index positions for bars
            indices = np.arange(len(years))
            
            # Fill in zero values for missing years
            east_values = []
            west_values = []
            
            for year in years:
                east_count = east_data[east_data['year'] == year]['fire_count'].values
                east_values.append(east_count[0] if len(east_count) > 0 else 0)
                
                west_count = west_data[west_data['year'] == year]['fire_count'].values
                west_values.append(west_count[0] if len(west_count) > 0 else 0)
            
            # Plot bars
            plt.bar(indices - bar_width/2, east_values, bar_width, color='red', label='Eastern WA')
            plt.bar(indices + bar_width/2, west_values, bar_width, color='blue', label='Western WA')
            
            plt.xlabel('Year')
            plt.ylabel('Number of Fire Incidents')
            plt.title('Fire Incidents in Washington State by Year and Region')
            plt.xticks(indices, years, rotation=45)
            plt.legend()
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            plt.tight_layout()
            plt.savefig('data/output/fire_incidents_by_region.png')
            print(f"Regional fire incidents visualization saved to data/output/fire_incidents_by_region.png")
        
        return yearly_fires
    else:
        print("Warning: Fire data doesn't have expected date column")
        return fire_df

def integrate_datasets(datasets):
    """
    Integrate the different datasets for combined analysis
    """
    print("\nIntegrating datasets for analysis...")
    
    # Check what data we have available
    available_data = {k: not v.empty for k, v in datasets.items()}
    print(f"Available datasets: {available_data}")
    
    # If we have fire data and climate data, we can correlate them
    if 'fires' in datasets and not datasets['fires'].empty and 'climate' in datasets and not datasets['climate'].empty:
        # Get yearly fire counts
        if 'year' not in datasets['fires'].columns:
            print("Processing fire data...")
            fire_df = process_fire_data(datasets['fires'])
        else:
            print("Using pre-processed fire data")
            fire_df = datasets['fires']
            
            # Ensure we have a fire_count column
            if 'fire_count' not in fire_df.columns:
                if 'year' in fire_df.columns:
                    fire_df = fire_df.groupby('year').size().reset_index(name='fire_count')
                else:
                    print("Cannot create fire counts without year column")
                    return None
        
        # Get yearly climate averages
        climate_yearly = None
        if 'climate' in datasets and not datasets['climate'].empty:
            if 'year' in datasets['climate'].columns:
                print("Using pre-processed climate data")
                
                # Determine what variables we have
                climate_vars = []
                for var in ['TAVG', 'TMAX', 'TMIN', 'PRCP']:
                    if var in datasets['climate'].columns:
                        climate_vars.append(var)
                
                if climate_vars:
                    agg_dict = {var: 'mean' for var in climate_vars}
                    climate_yearly = datasets['climate'].groupby('year').agg(agg_dict).reset_index()
                else:
                    print("No temperature or precipitation variables in climate data")
            else:
                print("Cannot create climate averages without year column")
                return None
        
        # Skip integration if either dataset is missing or has issues
        if fire_df is None or climate_yearly is None:
            print("Cannot integrate datasets due to missing data")
            return None
        
        # Merge the datasets on year
        combined = pd.merge(fire_df, climate_yearly, on='year', how='inner')
        
        if not combined.empty:
            # Save the combined dataset
            combined.to_csv('data/processed/wa_fire_climate_correlation.csv', index=False)
            print(f"Combined dataset saved to data/processed/wa_fire_climate_correlation.csv")
            
            # Create correlation visualization if we have temperature data
            if 'TAVG' in combined.columns:
                plt.figure(figsize=(10, 6))
                plt.scatter(combined['TAVG'], combined['fire_count'], alpha=0.7, s=50, c='red')
                plt.title('Correlation between Average Temperature and Fire Incidents')
                plt.xlabel('Average Temperature (°C)')
                plt.ylabel('Number of Fire Incidents')
                plt.grid(True, linestyle='--', alpha=0.7)
                
                # Add a trend line
                z = np.polyfit(combined['TAVG'], combined['fire_count'], 1)
                p = np.poly1d(z)
                plt.plot(combined['TAVG'], p(combined['TAVG']), "b--", alpha=0.7)
                
                # Add correlation coefficient
                correlation = combined['TAVG'].corr(combined['fire_count'])
                plt.annotate(f"Correlation: {correlation:.2f}", 
                            xy=(0.05, 0.95), xycoords='axes fraction',
                            fontsize=12, ha='left', va='top',
                            bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5))
                
                plt.tight_layout()
                plt.savefig('data/output/temperature_fire_correlation.png')
                print(f"Temperature-fire correlation visualization saved to data/output/temperature_fire_correlation.png")
            
            # Create correlation visualization for precipitation if available
            if 'PRCP' in combined.columns:
                plt.figure(figsize=(10, 6))
                plt.scatter(combined['PRCP'], combined['fire_count'], alpha=0.7, s=50, c='blue')
                plt.title('Correlation between Precipitation and Fire Incidents')
                plt.xlabel('Average Precipitation (mm)')
                plt.ylabel('Number of Fire Incidents')
                plt.grid(True, linestyle='--', alpha=0.7)
                
                # Add a trend line
                z = np.polyfit(combined['PRCP'], combined['fire_count'], 1)
                p = np.poly1d(z)
                plt.plot(combined['PRCP'], p(combined['PRCP']), "r--", alpha=0.7)
                
                # Add correlation coefficient
                correlation = combined['PRCP'].corr(combined['fire_count'])
                plt.annotate(f"Correlation: {correlation:.2f}", 
                            xy=(0.05, 0.95), xycoords='axes fraction',
                            fontsize=12, ha='left', va='top',
                            bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5))
                
                plt.tight_layout()
                plt.savefig('data/output/precipitation_fire_correlation.png')
                print(f"Precipitation-fire correlation visualization saved to data/output/precipitation_fire_correlation.png")
            
            return combined
    
    # If we have fire data and FEMA data, we can compare them
    if ('fires' in datasets and not datasets['fires'].empty and 
        'fema' in datasets and not datasets['fema'].empty):
        
        # Get yearly fire counts if not already processed
        if 'year' not in datasets['fires'].columns:
            print("Processing fire data...")
            fire_df = process_fire_data(datasets['fires'])
        else:
            print("Using pre-processed fire data")
            fire_df = datasets['fires']
            
            # Ensure we have a fire_count column
            if 'fire_count' not in fire_df.columns:
                if 'year' in fire_df.columns:
                    fire_df = fire_df.groupby('year').size().reset_index(name='fire_count')
                else:
                    print("Cannot create fire counts without year column")
                    return None
        
        # Get yearly FEMA disaster counts
        fema_df = datasets['fema']
        if 'incident_year' not in fema_df.columns and 'incidentBeginDate' in fema_df.columns:
            print("Processing FEMA data...")
            fema_df = process_fema_data(fema_df)
        
        if 'incident_year' in fema_df.columns:
            fema_yearly = fema_df.groupby('incident_year').size().reset_index(name='declaration_count')
            
            # Merge the fire and FEMA data
            merged = pd.merge(fire_df, fema_yearly, 
                             left_on='year', right_on='incident_year', 
                             how='outer').fillna(0)
            
            if not merged.empty:
                # Save the merged dataset
                merged.to_csv('data/processed/wa_fire_fema_comparison.csv', index=False)
                print(f"Fire-FEMA comparison data saved to data/processed/wa_fire_fema_comparison.csv")
                
                # Create a visualization comparing fire incidents and disaster declarations
                plt.figure(figsize=(12, 6))
                
                # Create two y-axes
                ax1 = plt.gca()
                ax2 = ax1.twinx()
                
                # Plot fire incidents on the first y-axis
                bars = ax1.bar(merged['year'], merged['fire_count'], color='orange', alpha=0.7, label='Fire Incidents')
                ax1.set_xlabel('Year')
                ax1.set_ylabel('Number of Fire Incidents', color='orange')
                ax1.tick_params(axis='y', labelcolor='orange')
                
                # Plot disaster declarations on the second y-axis
                line = ax2.plot(merged['year'], merged['declaration_count'], color='red', marker='o', 
                              linestyle='-', linewidth=2, label='FEMA Disaster Declarations')
                ax2.set_ylabel('Number of FEMA Disaster Declarations', color='red')
                ax2.tick_params(axis='y', labelcolor='red')
                
                # Add a title
                plt.title('Fire Incidents vs. FEMA Disaster Declarations in Washington State')
                
                # Add a legend
                lines, labels = ax1.get_legend_handles_labels()
                lines2, labels2 = ax2.get_legend_handles_labels()
                ax1.legend(lines + lines2, labels + labels2, loc='upper left')
                
                plt.grid(True, linestyle='--', alpha=0.7)
                plt.tight_layout()
                plt.savefig('data/output/fire_fema_comparison.png')
                print(f"Fire-FEMA comparison visualization saved to data/output/fire_fema_comparison.png")
                
                return merged
    
    print("No suitable datasets available for integration")
    return None

def main():
    """
    Main function to run all analysis
    """
    print("Starting Washington State Wildfire Data Analysis")
    print("=" * 50)
    
    # Load all data
    data = load_data()
    
    # Process each dataset
    if 'fema' in data and not data['fema'].empty:
        data['fema'] = process_fema_data(data['fema'])
    
    if 'climate' in data and not data['climate'].empty:
        data['climate'] = process_climate_data(data['climate'])
    
    if 'fires' in data and not data['fires'].empty:
        data['fires'] = process_fire_data(data['fires'])
    
    # Integrate and analyze across datasets
    integrated_data = integrate_datasets(data)
    
    if integrated_data is not None:
        print("\nData integration successful!")
    else:
        print("\nData integration produced no results.")
    
    print("\nAnalysis complete. Results saved to data/processed and data/output directories.")

if __name__ == "__main__":
    main()
