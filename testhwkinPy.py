
import requests

# Your API token
myToken = '50UI0O.LHofQ0pPorgmIlpI2qVtqBlK8qhI9'

# API token request URL
tokenUrl = 'https://cloud.hawkindynamics.com/api/token'

# header for request
head = {'Authorization': 'bearer {}'.format(myToken)}

# request repsone
tokenResponse = requests.get(tokenUrl, headers=head)

# use json package to parse reponse for access token
import json

# Parse JSON text
data = json.loads(tokenResponse.text)

# Extract access token
access_token = data['access_token']

# create access token object
myToken = access_token

# URL to call for test data
myUrl = 'https://cloud.hawkindynamics.com/api/dev'

# query parameters (from Feb 7, 2024 GMT)
querystring = {"from":"1707264000"}

# header for query, including access token
head = {'Authorization': 'bearer {}'.format(myToken)}

# query response
response = requests.get(myUrl, headers=head, params=querystring)

# respone as text
print(response.text)


