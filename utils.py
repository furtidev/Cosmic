# Libraries
import json
import requests
import urllib.request

# Functions	
def use_rest_api(url: str):
	response = requests.get(url)
	return response.json()