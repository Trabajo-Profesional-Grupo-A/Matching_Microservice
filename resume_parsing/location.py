import time
import requests
from geopy.distance import geodesic

def get_coordinates_locationiq(address, api_key):
    # Construct the request URL
    url = f"https://us1.locationiq.com/v1/search"
    params = {
        'key': api_key,
        'q': address,
        'format': 'json'
    }
    # Send the request
    response = requests.get(url, params=params)
    
    # Extract latitude and longitude
    if response.status_code == 200:
        data = response.json()
        if data:
            return data[0]['lat'], data[0]['lon']
    return None

# Replace with your LocationIQ API key
api_key = 'your_api_key_here'
user_address = "Capello 820, Banfield, Buenos Aires, Argentina"
company_address = "Colombres 353, Lomas de Zamora, Buenos Aires, Argentina"
user_coordinates = get_coordinates_locationiq(user_address, api_key)
time.sleep(1)  # Sleep for 1 second to avoid rate limits
company_coordinates = get_coordinates_locationiq(company_address, api_key)

# Calculate distance
distance_km = geodesic(user_coordinates, company_coordinates).kilometers
print(f"Distance: {distance_km:.2f} km")