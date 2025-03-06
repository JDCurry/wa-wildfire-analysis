# modis_improved.py - Fire history data collection using geopandas
import os
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# Create directory if it doesn't exist
os.makedirs('data/raw', exist_ok=True)
os.makedirs('data/output', exist_ok=True)

def download_wa_boundary():
    """
    Download Washington state boundary for clipping
    """
    print("Downloading Washington state boundary...")
    
    try:
        # This is a URL for US state boundaries
        url = "https://eric.clst.org/assets/wiki/uploads/Stuff/gz_2010_us_040_00_500k.json"
        
        # Read directly with geopandas
        boundaries = gpd.read_file(url)
        
        # Filter for Washington
        wa_boundary = boundaries[boundaries['STATE'] == 'WA']
        
        if len(wa_boundary) == 0:
            print("Error: Washington state boundary not found")
            return None
        
        # Save to file
        wa_boundary.to_file('data/raw/wa_boundary.shp')
        print(f"Washington boundary saved to data/raw/wa_boundary.shp")
        
        return wa_boundary
    
    except Exception as e:
        print(f"Error downloading Washington boundary: {e}")
        return None

def create_fire_data(wa_boundary=None):
    """
    Create a fire dataset for Washington state
    """
    print("Creating a fire history dataset for Washington state...")
    
    # If we don't have a boundary, try to load it
    if wa_boundary is None:
        try:
            if os.path.exists('data/raw/wa_boundary.shp'):
                wa_boundary = gpd.read_file('data/raw/wa_boundary.shp')
                print("Loaded Washington boundary from file")
            else:
                wa_boundary = download_wa_boundary()
                if wa_boundary is None:
                    raise Exception("Could not get Washington boundary")
        except Exception as e:
            print(f"Error loading Washington boundary: {e}")
            # Use a bounding box instead
            wa_bbox = {
                'min_lon': -124.85,
                'max_lon': -116.92,
                'min_lat': 45.54,
                'max_lat': 49.0
            }
            print("Using bounding box instead of proper boundary")
    
    # Generate random fire points
    np.random.seed(42)  # For reproducibility
    
    num_points = 1000
    
    if wa_boundary is not None:
        # Get the boundary's bounds
        minx, miny, maxx, maxy = wa_boundary.total_bounds
        
        # Generate random points within the bounding box
        longitudes = np.random.uniform(minx, maxx, num_points * 2)
        latitudes = np.random.uniform(miny, maxy, num_points * 2)
        
        # Create Points
        points = [Point(lon, lat) for lon, lat in zip(longitudes, latitudes)]
        points_gdf = gpd.GeoDataFrame(geometry=points, crs=wa_boundary.crs)
        
        # Clip to WA boundary
        within_wa = points_gdf.within(wa_boundary.unary_union)
        points_gdf = points_gdf[within_wa]
        
        # Take the first num_points if we have more
        if len(points_gdf) > num_points:
            points_gdf = points_gdf.iloc[:num_points]
        
        # Get the coordinates
        longitudes = [p.x for p in points_gdf.geometry]
        latitudes = [p.y for p in points_gdf.geometry]
    else:
        # Use the bounding box
        wa_bbox = {
            'min_lon': -124.85,
            'max_lon': -116.92,
            'min_lat': 45.54,
            'max_lat': 49.0
        }
        
        longitudes = np.random.uniform(wa_bbox['min_lon'], wa_bbox['max_lon'], num_points)
        latitudes = np.random.uniform(wa_bbox['min_lat'], wa_bbox['max_lat'], num_points)
    
    # Assign random dates between 1990 and present
    start_date = datetime(1990, 1, 1)
    end_date = datetime.now()
    days_range = (end_date - start_date).days
    
    # Convert numpy int64 to regular int for timedelta
    random_days = [int(x) for x in np.random.randint(0, days_range, len(latitudes))]
    dates = [start_date + timedelta(days=days) for days in random_days]
    
    # Make eastern WA have more summer fires to reflect reality
    # Anything east of -120.85 is roughly east of the Cascades
    is_eastern = [lon > -120.85 for lon in longitudes]
    
    # For eastern WA, bias dates towards summer months (Jun-Sep)
    for i, eastern in enumerate(is_eastern):
        if eastern:
            # 70% chance of being in summer for eastern WA fires
            if np.random.random() < 0.7:
                # Generate a random summer date
                year = np.random.randint(1990, end_date.year + 1)
                month = np.random.randint(6, 10)  # June-September
                day = np.random.randint(1, 31)
                # Ensure valid date
                try:
                    dates[i] = datetime(year, month, min(day, 30 if month in [6, 9] else 31))
                except ValueError:
                    # Handle February
                    dates[i] = datetime(year, month, 28)
    
    # Create DataFrame
    fire_data = {
        'latitude': latitudes,
        'longitude': longitudes,
        'acq_date': [d.strftime("%Y-%m-%d") for d in dates],
        'confidence': np.random.choice(['nominal', 'high'], len(latitudes)),
        'frp': np.random.exponential(50, len(latitudes)),  # Fire Radiative Power
        'brightness': np.random.normal(315, 10, len(latitudes)),
        'is_eastern': is_eastern  # Add this for analysis
    }
    
    fire_df = pd.DataFrame(fire_data)
    
    # Create GeoDataFrame
    geometry = [Point(xy) for xy in zip(fire_df['longitude'], fire_df['latitude'])]
    fire_gdf = gpd.GeoDataFrame(fire_df, geometry=geometry, crs="EPSG:4326")
    
    # Save to CSV and Shapefile
    fire_df.to_csv('data/raw/wa_fire_history.csv', index=False)
    fire_gdf.to_file('data/raw/wa_fire_history.shp')
    
    print(f"Created dataset with {len(fire_df)} fire points")
    print(f"Data saved to data/raw/wa_fire_history.csv and data/raw/wa_fire_history.shp")
    
    # Create a visualization of the fire locations
    create_fire_visualization(fire_gdf, wa_boundary)
    
    return fire_gdf

def create_fire_visualization(fire_gdf, wa_boundary=None):
    """
    Create a visualization of fire locations in Washington
    """
    try:
        # Set up the plot
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Plot Washington boundary if available
        if wa_boundary is not None:
            wa_boundary.boundary.plot(ax=ax, linewidth=1, color='black')
        
        # Plot fire points, colored by east/west
        if 'is_eastern' in fire_gdf.columns:
            west_fires = fire_gdf[~fire_gdf['is_eastern']]
            east_fires = fire_gdf[fire_gdf['is_eastern']]
            
            west_fires.plot(ax=ax, markersize=5, color='blue', alpha=0.5, label='Western WA')
            east_fires.plot(ax=ax, markersize=5, color='red', alpha=0.5, label='Eastern WA')
        else:
            fire_gdf.plot(ax=ax, markersize=5, color='red', alpha=0.5)
        
        # Add Cascade mountains approximate line
        ax.axvline(x=-120.85, color='green', linestyle='--', linewidth=2, alpha=0.7, 
                   label='Cascade Mountains (approx.)')
        
        # Add labels and title
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.set_title('Simulated Wildfire Locations in Washington State (1990-present)')
        ax.legend()
        
        # Add grid
        ax.grid(True, linestyle='--', alpha=0.3)
        
        # Save the figure
        plt.tight_layout()
        plt.savefig('data/output/wa_fire_locations.png', dpi=300)
        plt.close()
        
        print("Fire location visualization saved to data/output/wa_fire_locations.png")
        
        # Create a histogram of fires by year
        fire_gdf['year'] = pd.to_datetime(fire_gdf['acq_date']).dt.year
        
        east_counts = fire_gdf[fire_gdf['is_eastern']].groupby('year').size()
        west_counts = fire_gdf[~fire_gdf['is_eastern']].groupby('year').size()
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        if not east_counts.empty and not west_counts.empty:
            # Combine into a DataFrame
            counts_df = pd.DataFrame({'Eastern WA': east_counts, 'Western WA': west_counts})
            counts_df.fillna(0, inplace=True)
            
            # Plot as a stacked bar chart
            counts_df.plot(kind='bar', stacked=True, ax=ax, color=['red', 'blue'])
            
            ax.set_xlabel('Year')
            ax.set_ylabel('Number of Fires')
            ax.set_title('Simulated Wildfires by Year and Region')
            ax.legend(title='Region')
            
            # Add grid
            ax.grid(True, linestyle='--', alpha=0.3, axis='y')
            
            # Save the figure
            plt.tight_layout()
            plt.savefig('data/output/wa_fires_by_year.png', dpi=300)
            plt.close()
            
            print("Fire trends visualization saved to data/output/wa_fires_by_year.png")
    
    except Exception as e:
        print(f"Error creating fire visualization: {e}")

if __name__ == "__main__":
    print("Starting Washington state fire history data generation...")
    
    # First try to get the Washington boundary
    wa_boundary = download_wa_boundary()
    
    # Generate fire data
    fire_gdf = create_fire_data(wa_boundary)
    
    print("Fire history data generation complete!")
