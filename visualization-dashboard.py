# dashboard_creator.py - Create an HTML dashboard for the Washington State Wildfire Project
import os
import pandas as pd
import numpy as np
import json
from datetime import datetime
import base64

# Create output directory for dashboard
os.makedirs('dashboard', exist_ok=True)

def create_html_dashboard():
    """
    Create an HTML dashboard showcasing all visualizations and data
    """
    # List of visualization files
    visualization_files = []
    
    # Check for files in data/output
    if os.path.exists('data/output'):
        visualization_files.extend([
            os.path.join('data/output', file) 
            for file in os.listdir('data/output') 
            if file.endswith(('.png', '.jpg'))
        ])
    
    # Check for files in data/output_fahrenheit
    if os.path.exists('data/output_fahrenheit'):
        visualization_files.extend([
            os.path.join('data/output_fahrenheit', file) 
            for file in os.listdir('data/output_fahrenheit') 
            if file.endswith(('.png', '.jpg'))
        ])
    
    # Create dashboard HTML
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Washington State Wildfire Analysis Dashboard</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f5f5f5;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            header {
                background-color: #8b0000; /* Dark red */
                color: white;
                padding: 20px;
                text-align: center;
                margin-bottom: 20px;
            }
            .dashboard-section {
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                margin-bottom: 20px;
                padding: 20px;
            }
            .section-title {
                border-bottom: 2px solid #8b0000;
                color: #8b0000;
                padding-bottom: 10px;
                margin-top: 0;
            }
            .visualization-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
                gap: 20px;
            }
            .visualization-card {
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                padding: 15px;
            }
            .visualization-card img {
                max-width: 100%;
                height: auto;
                border: 1px solid #ddd;
            }
            .visualization-card h3 {
                margin-top: 15px;
                color: #333;
            }
            .visualization-card p {
                color: #666;
                font-size: 14px;
            }
            .summary-text {
                line-height: 1.6;
            }
            .key-findings {
                background-color: #f9f9f9;
                border-left: 4px solid #8b0000;
                padding: 15px;
                margin: 20px 0;
            }
            .key-findings h3 {
                margin-top: 0;
                color: #8b0000;
            }
            footer {
                text-align: center;
                padding: 20px;
                color: #666;
                font-size: 14px;
                margin-top: 20px;
            }
            @media (max-width: 768px) {
                .visualization-grid {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <header>
            <h1>Washington State Wildfire Susceptibility Analysis</h1>
            <p>Interactive dashboard displaying wildfire patterns, climate correlations, and risk analysis</p>
        </header>
        
        <div class="container">
            <div class="dashboard-section">
                <h2 class="section-title">Project Overview</h2>
                <div class="summary-text">
                    <p>This dashboard presents the results of a comprehensive analysis of wildfire patterns and susceptibility in Washington State. 
                    The project combines historical wildfire data from NOAA, FEMA disaster declarations, and climate data to identify patterns and 
                    correlations that can help predict future wildfire risks.</p>
                    
                    <div class="key-findings">
                        <h3>Key Findings</h3>
                        <ul>
                            <li>Eastern Washington experiences significantly more wildfires than the western region, aligning with its drier climate.</li>
                            <li>FEMA disaster declarations for wildfires have increased dramatically since 2014, with peak activity in 2015.</li>
                            <li>Temperature shows a strong positive correlation with wildfire incidents, indicating climate change may increase fire risk.</li>
                            <li>Precipitation levels are inversely correlated with fire frequency, highlighting drought conditions as a key risk factor.</li>
                        </ul>
                    </div>
                </div>
            </div>
            
            <div class="dashboard-section">
                <h2 class="section-title">Wildfire Historical Data</h2>
                <div class="visualization-grid">
    """
    
    # Function to get image info
    def get_image_info(filename):
        base_filename = os.path.basename(filename)
        title = ' '.join(word.capitalize() for word in base_filename.replace('.png', '').replace('_', ' ').split())
        
        # Customize descriptions based on filename keywords
        description = ""
        if 'fema' in filename.lower():
            description = "Shows historical FEMA wildfire disaster declarations in Washington State, highlighting a significant increase in recent years."
        elif 'regional' in filename.lower() or 'region' in filename.lower():
            description = "Compares fire incidents between Eastern and Western Washington, showing the regional distribution patterns."
        elif 'temperature' in filename.lower() and 'trend' in filename.lower():
            description = "Visualizes temperature trends in Washington State, which may correlate with increased wildfire activity."
        elif 'correlation' in filename.lower():
            description = "Displays the statistical relationship between climate factors and wildfire frequency."
        elif 'location' in filename.lower():
            description = "Maps the spatial distribution of wildfire incidents across Washington State."
        elif 'incident' in filename.lower() and 'year' in filename.lower():
            description = "Shows the annual count of wildfire incidents in Washington State over time."
        else:
            description = "Visualization of wildfire data patterns in Washington State."
            
        return {
            "filename": filename,
            "title": title,
            "description": description
        }
    
    # Get info for all visualization files
    viz_info = [get_image_info(file) for file in visualization_files]
    
    # Sort into categories
    fire_history_viz = [info for info in viz_info if 'incident' in info['filename'].lower() or 'location' in info['filename'].lower() or 'fema' in info['filename'].lower()]
    climate_viz = [info for info in viz_info if 'temperature' in info['filename'].lower() or 'precipitation' in info['filename'].lower()]
    correlation_viz = [info for info in viz_info if 'correlation' in info['filename'].lower()]
    
    # Add fire history visualizations
    for info in fire_history_viz:
        if os.path.exists(info['filename']):
            with open(info['filename'], 'rb') as img_file:
                img_data = base64.b64encode(img_file.read()).decode('utf-8')
                
            html_content += f"""
                <div class="visualization-card">
                    <img src="data:image/png;base64,{img_data}" alt="{info['title']}">
                    <h3>{info['title']}</h3>
                    <p>{info['description']}</p>
                </div>
            """
    
    html_content += """
                </div>
            </div>
            
            <div class="dashboard-section">
                <h2 class="section-title">Climate Data Analysis</h2>
                <div class="visualization-grid">
    """
    
    # Add climate visualizations
    for info in climate_viz:
        if os.path.exists(info['filename']):
            with open(info['filename'], 'rb') as img_file:
                img_data = base64.b64encode(img_file.read()).decode('utf-8')
                
            html_content += f"""
                <div class="visualization-card">
                    <img src="data:image/png;base64,{img_data}" alt="{info['title']}">
                    <h3>{info['title']}</h3>
                    <p>{info['description']}</p>
                </div>
            """
    
    html_content += """
                </div>
            </div>
            
            <div class="dashboard-section">
                <h2 class="section-title">Wildfire-Climate Correlations</h2>
                <div class="visualization-grid">
    """
    
    # Add correlation visualizations
    for info in correlation_viz:
        if os.path.exists(info['filename']):
            with open(info['filename'], 'rb') as img_file:
                img_data = base64.b64encode(img_file.read()).decode('utf-8')
                
            html_content += f"""
                <div class="visualization-card">
                    <img src="data:image/png;base64,{img_data}" alt="{info['title']}">
                    <h3>{info['title']}</h3>
                    <p>{info['description']}</p>
                </div>
            """
    
    html_content += """
                </div>
            </div>
            
            <div class="dashboard-section">
                <h2 class="section-title">Conclusions & Recommendations</h2>
                <div class="summary-text">
                    <p>Our analysis reveals several important patterns in Washington State's wildfire history and susceptibility:</p>
                    
                    <ol>
                        <li><strong>Regional Disparity:</strong> Eastern Washington consistently experiences more wildfires than Western Washington, 
                        reflecting the region's drier climate and vegetation types that are more prone to burning.</li>
                        
                        <li><strong>Climate Correlation:</strong> Temperature shows a strong positive correlation with wildfire frequency, while 
                        precipitation shows a negative correlation. This suggests that as climate change leads to warmer and potentially drier conditions, 
                        wildfire risk may increase.</li>
                        
                        <li><strong>Temporal Patterns:</strong> FEMA disaster declarations for wildfires have increased dramatically in recent years, 
                        particularly since 2014, indicating either increasing fire severity or improved recognition of fire impacts.</li>
                    </ol>
                    
                    <h3>Recommendations:</h3>
                    <ul>
                        <li>Focus fire prevention resources in Eastern Washington, particularly during summer months when fire risk is highest.</li>
                        <li>Develop early warning systems based on climate forecasts, especially for periods of high temperature and low precipitation.</li>
                        <li>Increase public education about fire risks, particularly in the wildland-urban interface areas where human activities can trigger fires.</li>
                        <li>Implement more aggressive forest management practices in high-risk areas, including controlled burns and thinning.</li>
                        <li>Prepare communities for longer and more severe fire seasons as climate change progresses.</li>
                    </ul>
                </div>
            </div>
        </div>
        
        <footer>
            <p>Washington State Wildfire Susceptibility Analysis Dashboard | Created: """ + datetime.now().strftime('%Y-%m-%d') + """</p>
        </footer>
    </body>
    </html>
    """
    
    # Write HTML to file
    dashboard_path = 'dashboard/index.html'
    with open(dashboard_path, 'w') as f:
        f.write(html_content)
    
    print(f"Dashboard created at {os.path.abspath(dashboard_path)}")
    return dashboard_path

if __name__ == "__main__":
    print("Creating Washington State Wildfire Analysis Dashboard...")
    dashboard_path = create_html_dashboard()
    print(f"Dashboard creation complete! Open {dashboard_path} in a web browser to view.")
