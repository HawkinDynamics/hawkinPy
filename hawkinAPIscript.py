# Suggested to create a environmental variable to store your API key, so that it is not left in the script
# You can do this in the terminal by running the code below:
# setx your_token_variale_name 'Your_API_Token'

import os
import requests
from datetime import datetime

# Securely retrieve API token from environment variables
# api_token = '50UI0O.LHofQ0pPorgmIlpI2qVtqBlK8qhI9'

# Function to fetch the access token
def fetch_access_token(api_token):
    url = 'https://cloud.hawkindynamics.com/api/token'
    headers = {'Authorization': f'Bearer {api_token}'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        response.raise_for_status()


# Function to query test data using the access token
def query_test_data(access_token):
    url = 'https://cloud.hawkindynamics.com/api/dev'
    headers = {'Authorization': f'Bearer {access_token}'}
    timestamp = int(datetime(2024, 3, 1).timestamp())
    params = {'date_from': timestamp}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return print(response.text)
    else:
        response.raise_for_status()

# Example usage (commented out to prevent execution)
access_token = fetch_access_token('50UI0O.LHofQ0pPorgmIlpI2qVtqBlK8qhI9')
test_data = query_test_data(access_token)

print(test_data)
