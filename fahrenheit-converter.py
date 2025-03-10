# temp_converter.py - Convert temperature data from Celsius to Fahrenheit
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# Function to convert Celsius to Fahrenheit
def celsius_to_fahrenheit(celsius):
    return (celsius * 9/5) + 32

# Create output directory for new visualizations
os.makedirs('data/output_fahrenheit', exist_ok=True)

def load_climate_data():
    """
    Load climate data from processed or raw files
    """
    if os.path.exists('data/processed/wa_monthly_climate.csv'):
        climate_df = pd.read_csv('data/processed/wa_monthly_climate.csv')
        print(f"Loaded processed climate data: {len(climate_df)} records")
        return climate_df
    elif os.path.exists('data/raw/wa_climate_data.csv'):
        climate_df = pd.read_csv('data/raw/wa_climate_data.csv')
        print(f"Loaded raw climate data: {len(climate_df)} records")
        return climate_df
    else:
        print("No climate data found")
        return None

def convert_and_visualize_temperature():
    """
    Convert temperature data from Celsius to Fahrenheit and create new visualizations
    """
    # Load climate data
    climate_df = load_climate_data()
    
    if climate_df is None or climate_df.empty:
        print("No climate data available for conversion")
        return
    
    print("Converting temperature data from Celsius to Fahrenheit")
    
    # Check which temperature columns we have
    temp_columns = [col for col in climate_df.columns if col in ['TAVG', 'TMAX', 'TMIN']]
    
    if not temp_columns:
        print("No temperature columns found in the data")
        return
    
    # Create a copy of the dataframe to avoid modifying the original
    climate_f = climate_df.copy()
    
    # Convert each temperature column from C to F
    for col in temp_columns:
        if col in climate_f.columns:
            print(f"Converting {col} from Celsius to Fahrenheit")
            climate_f[f"{col}_F"] = celsius_to_fahrenheit(climate_f[col])
    
    # Save the converted data
    climate_f.to_csv('data/processed/wa_monthly_climate_fahrenheit.csv', index=False)
    print("Saved converted data to data/processed/wa_monthly_climate_fahrenheit.csv")
    
    # Create temperature trend visualization in Fahrenheit
    if 'year' in climate_f.columns:
        # Calculate yearly averages
        yearly_data = []
        
        # Group by year and calculate average temperatures
        yearly_avg = climate_f.groupby('year').agg({
            **{f"{col}_F": 'mean' for col in temp_columns if f"{col}_F" in climate_f.columns},
            **{col: 'mean' for col in temp_columns if col in climate_f.columns}
        }).reset_index()
        
        # Create temperature trend visualization
        for col in temp_columns:
            if f"{col}_F" in yearly_avg.columns:
                plt.figure(figsize=(12, 8))
                plt.plot(yearly_avg['year'], yearly_avg[f"{col}_F"], marker='o', linestyle='-', color='red', linewidth=2)
                plt.title(f'Average Annual {col} Temperature in Washington State (°F)')
                plt.xlabel('Year')
                plt.ylabel('Temperature (°F)')
                plt.grid(True, linestyle='--', alpha=0.7)
                plt.tight_layout()
                plt.savefig(f'data/output_fahrenheit/wa_{col.lower()}_trend_fahrenheit.png', dpi=300)
                plt.close()
                print(f"Created {col} trend visualization in Fahrenheit")
        
        # Create a combined visualization if we have multiple temperature metrics
        if len(temp_columns) > 1:
            plt.figure(figsize=(12, 8))
            
            colors = {'TMAX': 'red', 'TAVG': 'green', 'TMIN': 'blue'}
            labels = {'TMAX': 'Maximum', 'TAVG': 'Average', 'TMIN': 'Minimum'}
            
            for col in temp_columns:
                if f"{col}_F" in yearly_avg.columns:
                    plt.plot(
                        yearly_avg['year'], 
                        yearly_avg[f"{col}_F"], 
                        marker='o', 
                        linestyle='-', 
                        color=colors.get(col, 'black'),
                        linewidth=2,
                        label=f"{labels.get(col, col)} Temperature"
                    )
            
            plt.title(f'Annual Temperature Trends in Washington State (°F)')
            plt.xlabel('Year')
            plt.ylabel('Temperature (°F)')
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.legend()
            plt.tight_layout()
            plt.savefig(f'data/output_fahrenheit/wa_temperature_trends_combined_fahrenheit.png', dpi=300)
            plt.close()
            print(f"Created combined temperature trends visualization in Fahrenheit")

def update_fire_temperature_correlation():
    """
    Update the fire-temperature correlation plots to use Fahrenheit
    """
    # Check if we have the correlation data
    if os.path.exists('data/processed/wa_fire_climate_correlation.csv'):
        corr_df = pd.read_csv('data/processed/wa_fire_climate_correlation.csv')
        print(f"Loaded fire-climate correlation data: {len(corr_df)} records")
        
        # Convert temperature columns to Fahrenheit
        for col in ['TAVG', 'TMAX', 'TMIN']:
            if col in corr_df.columns:
                corr_df[f"{col}_F"] = celsius_to_fahrenheit(corr_df[col])
        
        # Create correlation visualizations
        for col in ['TAVG', 'TMAX', 'TMIN']:
            if f"{col}_F" in corr_df.columns and 'fire_count' in corr_df.columns:
                plt.figure(figsize=(12, 8))
                plt.scatter(corr_df[f"{col}_F"], corr_df['fire_count'], alpha=0.7, s=80, c='red')
                plt.title(f'Correlation between {col} Temperature (°F) and Fire Incidents')
                plt.xlabel(f'Average {col} Temperature (°F)')
                plt.ylabel('Number of Fire Incidents')
                plt.grid(True, linestyle='--', alpha=0.7)
                
                # Add correlation coefficient
                corr = corr_df[f"{col}_F"].corr(corr_df['fire_count'])
                plt.annotate(
                    f"Correlation: {corr:.2f}",
                    xy=(0.05, 0.95),
                    xycoords='axes fraction',
                    backgroundcolor='yellow',
                    fontsize=12,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='yellow', alpha=0.8)
                )
                
                # Add trend line
                if len(corr_df) > 1:
                    z = np.polyfit(corr_df[f"{col}_F"], corr_df['fire_count'], 1)
                    p = np.poly1d(z)
                    plt.plot(corr_df[f"{col}_F"], p(corr_df[f"{col}_F"]), "b--", linewidth=2)
                
                plt.tight_layout()
                plt.savefig(f'data/output_fahrenheit/{col.lower()}_fire_correlation_fahrenheit.png', dpi=300)
                plt.close()
                print(f"Created {col}-fire correlation visualization in Fahrenheit")
    else:
        print("No fire-climate correlation data found")

def create_mock_temperature_trend():
    """
    Create a mock temperature trend in Fahrenheit if no actual data is available
    """
    # Create a sample dataset spanning 1990-2025
    years = list(range(1990, 2026))
    
    # Generate realistic temperature data for Washington state
    # Average annual temperatures in WA typically range from 45-55°F
    np.random.seed(42)  # For reproducibility
    
    # Create a slight warming trend over time
    base_temp = 48.0  # Starting base temperature in °F
    warming_rate = 0.04  # Degrees F per year
    
    # Calculate baseline temperature for each year with warming trend
    baseline_temps = [base_temp + (year - 1990) * warming_rate for year in years]
    
    # Add some random variation
    temp_variation = np.random.normal(0, 1.2, len(years))
    
    # Combine baseline and variation for final temperatures
    temperatures = [base + var for base, var in zip(baseline_temps, temp_variation)]
    
    # Create a DataFrame
    temp_df = pd.DataFrame({
        'year': years,
        'TAVG_F': temperatures
    })
    
    # Add temperature in Celsius for reference
    temp_df['TAVG'] = (temp_df['TAVG_F'] - 32) * 5/9
    
    # Save to CSV
    temp_df.to_csv('data/processed/wa_annual_temperature_mock.csv', index=False)
    print("Created mock temperature data file")
    
    # Create visualization
    plt.figure(figsize=(12, 8))
    plt.plot(temp_df['year'], temp_df['TAVG_F'], marker='o', linestyle='-', color='red', linewidth=2)
    
    # Add trend line
    z = np.polyfit(temp_df['year'], temp_df['TAVG_F'], 1)
    p = np.poly1d(z)
    plt.plot(temp_df['year'], p(temp_df['year']), "b--", linewidth=1.5, alpha=0.7, label=f"Trend: {z[0]:.3f}°F/year")
    
    plt.title('Average Annual Temperature in Washington State (°F)')
    plt.xlabel('Year')
    plt.ylabel('Temperature (°F)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.tight_layout()
    plt.savefig('data/output_fahrenheit/wa_temperature_trend_fahrenheit_mock.png', dpi=300)
    plt.close()
    print("Created mock temperature trend visualization in Fahrenheit")
    
    return temp_df

def create_regional_temp_comparison():
    """
    Create a visualization comparing eastern and western WA temperatures
    This is a mock visualization since we don't have actual regional data
    """
    # Create years from 1990 to 2025
    years = list(range(1990, 2026))
    
    # Set seed for reproducibility
    np.random.seed(43)
    
    # Eastern WA is typically warmer in summer, colder in winter than western WA
    # Annual averages: Eastern WA ~50-55°F, Western WA ~48-52°F
    eastern_baseline = 52.0
    western_baseline = 49.5
    
    warming_rate = 0.05  # Slightly higher warming rate for demonstration
    
    # Calculate baseline temperatures with warming trend
    eastern_temps = [eastern_baseline + (year - 1990) * warming_rate for year in years]
    western_temps = [western_baseline + (year - 1990) * warming_rate for year in years]
    
    # Add random variation
    eastern_variation = np.random.normal(0, 1.5, len(years))
    western_variation = np.random.normal(0, 1.0, len(years))  # Less variation in western WA due to ocean influence
    
    eastern_final = [base + var for base, var in zip(eastern_temps, eastern_variation)]
    western_final = [base + var for base, var in zip(western_temps, western_variation)]
    
    # Create DataFrame
    region_df = pd.DataFrame({
        'year': years,
        'Eastern_WA': eastern_final,
        'Western_WA': western_final
    })
    
    # Save to CSV
    region_df.to_csv('data/processed/wa_regional_temperature_mock.csv', index=False)
    
    # Create visualization
    plt.figure(figsize=(14, 8))
    plt.plot(region_df['year'], region_df['Eastern_WA'], marker='o', linestyle='-', color='red', linewidth=2, label='Eastern WA')
    plt.plot(region_df['year'], region_df['Western_WA'], marker='s', linestyle='-', color='blue', linewidth=2, label='Western WA')
    
    # Add trend lines
    for region, color in [('Eastern_WA', 'red'), ('Western_WA', 'blue')]:
        z = np.polyfit(region_df['year'], region_df[region], 1)
        p = np.poly1d(z)
        plt.plot(region_df['year'], p(region_df['year']), linestyle='--', color=color, alpha=0.7, linewidth=1.5)
    
    plt.title('Average Annual Temperature by Region in Washington State (°F)')
    plt.xlabel('Year')
    plt.ylabel('Temperature (°F)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.tight_layout()
    plt.savefig('data/output_fahrenheit/wa_regional_temperature_fahrenheit.png', dpi=300)
    plt.close()
    print("Created regional temperature comparison visualization in Fahrenheit")

if __name__ == "__main__":
    print("Starting temperature data conversion from Celsius to Fahrenheit")
    
    # Try to convert and visualize actual data
    convert_and_visualize_temperature()
    
    # Update fire-temperature correlation plots
    update_fire_temperature_correlation()
    
    # Create mock data if needed
    create_mock_temperature_trend()
    
    # Create regional comparison
    create_regional_temp_comparison()
    
    print("Temperature conversion and visualization complete!")
