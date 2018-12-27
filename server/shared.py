import requests
from psycopg2 import sql
import json
import psycopg2

BUILDING_CODE = "building_code"
CLIENTS = "clients"

# Makes a request to uWaterloo API and returns the data in JSON format
def get_json_data():
  URL = "https://api.uwaterloo.ca/v2/wireless/usage.json?key=" + config["api"]
  response = requests.get(URL)
  if response.status_code == 200:
    data = response.json()["data"]
    return data
  else:
    return None

def connectToDB():
  conn = psycopg2.connect("dbname=" + config["dbname"] + " user=" + config["user"] + " host=" + config["host"] + " password=" + config["password"])
  cursor = conn.cursor()
  return (conn, cursor)

f = open("config","r")
file_contents = f.read()
file_contents = file_contents.split("\n")
config = {}
for line in file_contents:
  spl = line.split("=")
  config[spl[0]] = spl[1]