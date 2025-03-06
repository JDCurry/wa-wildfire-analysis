import requests
import pandas as pd
import json

# OpenFEMA API endpoint for disaster declarations
url = "https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries"

# Filter for Washington State wildfires from 1990 to present
params = {
    "$filter": "state eq 'WA' and incidentType eq 'Fire' and declarationDate ge '1990-01-01T00:00:00.000Z'",
    "$format": "json",
    "$top": 1000  # Maximum records to return
}

# Make the API request
response = requests.get(url, params=params)
data = response.json()

# Convert to DataFrame
fema_df = pd.DataFrame(data['DisasterDeclarationsSummaries'])

# Save to CSV
fema_df.to_csv('wa_fema_wildfire_declarations.csv', index=False)
