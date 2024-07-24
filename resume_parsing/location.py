import requests

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
