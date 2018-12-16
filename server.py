import requests
import json

URL = "https://api.uwaterloo.ca/v2/wireless/usage.json?key=016e13bdee8e91aa67f8e09043778e84&fbclid=IwAR3ImFTFO3Iy4p1ezM0Y51iFSohKyyAF4duDWh2AHsh9XwrCoVGrG8oc6VI"
response = requests.get(URL)
if response.status_code == 200:
  data = response.json()["data"]
  for d in data:
    if d["building_code"] == "AL":
      print(d)
