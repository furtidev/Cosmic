# Libraries
import json
import requests

# Functions	
def use_rest_api(url: str):
	response = requests.get(url)
	return response.json()
