import requests
import json
import psycopg2
import threading
from psycopg2 import sql
FIVE_MINUTE_DELAY = 1
LONG_DELAY = 2
BUILDING_CODE = "building_code"
CLIENTS = "clients"

# Caches the number of clients for each building for an hour
building_client_count_cache = {}

# Which column in the db should be updated
currcol = 1

def connectToDB():
  conn = psycopg2.connect("dbname=" + config["dbname"] + " user=" + config["user"] + " host=" + config["host"] + " password=" + config["password"])
  cursor = conn.cursor()
  return (conn, cursor)

# Gets the current column name as a string
def getCurrcol():
  global currcol
  return "col" + str(currcol)

# Increments the current column number, with a max of 31 * 4 (4 months)
def incrementCurrcol():
  global currcol
  currcol = (currcol + 1) % (31 * 4)

# Makes a request to uWaterloo API and returns the data in JSON format
def get_json_data():
  URL = "https://api.uwaterloo.ca/v2/wireless/usage.json?key=" + config["api"]
  response = requests.get(URL)
  if response.status_code == 200:
    data = response.json()["data"]
    return data
  else:
    return None

# Runs every 5 minutes
# Makes a request for data and stores it in a temporary cache
def five_minute_timer():
  five_minute_event = threading.Event()
  while not five_minute_event.wait(FIVE_MINUTE_DELAY):
    data = get_json_data()
    if data != None:
      for d in data:
        building_client_count_cache[d[BUILDING_CODE]].append(d[CLIENTS])

# Runs everyday
# Takes the minimum of all client numbers for the day and dumps it in the database
def long_timer():
  (conn, cursor) = connectToDB()

  long_event = threading.Event()
  while not long_event.wait(LONG_DELAY):
    # Map of building names to minimum number of clients connected in that hour
    to_write = {}

    # Get the minimum number of connected clients that day
    for building in building_client_count_cache:
      to_write[building] = min(building_client_count_cache[building])

    # Write each minimum for the day into the database
    for building in to_write:
      cursor.execute(sql.SQL("UPDATE buildingdb SET {} = %s WHERE building_name = %s;")
        .format(sql.Identifier(getCurrcol())),
                (str(to_write[building]), building))

    # Increment the currCol
    incrementCurrcol()

    # Commit changes to db
    conn.commit()

    print("Wrote to db!")

f = open("config","r")
file_contents = f.read()
file_contents = file_contents.split("\n")
config = {}
for line in file_contents:
  spl = line.split("=")
  config[spl[0]] = spl[1]

(conn, cursor) = connectToDB()

data = get_json_data()
if data != None:
  for d in data:
    building_client_count_cache[d[BUILDING_CODE]] = [d[CLIENTS]]
    cursor.execute(sql.SQL("INSERT INTO buildingdb(building_name, col0) VALUES (%s, %s);"),(d[BUILDING_CODE], d[CLIENTS]))

conn.commit()
cursor.close()
conn.close()


five_minute_thread = threading.Thread(None, five_minute_timer)
five_minute_thread.start()

long_thread = threading.Thread(None, long_timer)
long_thread.start()