import json
import psycopg2
import threading
from psycopg2 import sql
from flask import Flask, jsonify
from flask_restful import Api
from shared import *

FIVE_MINUTE_DELAY = 1
LONG_DELAY = 2

BUILDING_CODE = "building_code"
CLIENTS = "clients"

# Caches the number of clients for each building for an hour
building_client_count_cache = {}

# Which column in the db should be updated
currcol = 1

# Resets the daily cache for each building
def reset_daily_cache():
  data = get_json_data()
  if data != None:
    for d in data:
      building_client_count_cache[d[BUILDING_CODE]] = [d[CLIENTS]]


# Gets the current column name as a string
def getCurrcol():
  global currcol
  return "col" + str(currcol)

# Increments the current column number, with a max of 31 * 4 (4 months)
def incrementCurrcol():
  global currcol
  currcol = (currcol + 1) % (31 * 4)

def get_baselines():
  (conn, cursor) = connectToDB()
  cursor.execute(sql.SQL("SELECT * FROM buildingdb"))
  result = cursor.fetchall()
  json = {}
  print(result)
  for building_data in result:

    # Last index is building name
    building_name = building_data[-1]

    # Filter out all None types
    filtered = [x for x in building_data[:-1] if x is not None]
    baseline = min(filtered)
    json[building_name] = {"building_name": building_name,
                 "baseline": baseline
                 }
  return json


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
  long_event = threading.Event()
  while not long_event.wait(LONG_DELAY):
    (conn, cursor) = connectToDB()
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

    # Reset the daily cache
    reset_daily_cache()

    # Commit changes to db
    conn.commit()
    conn.close()
    cursor.close()
    print("Wrote to db!")

# Calculates the number of people in each building
# Based on the historical data
@app.route('/peoplecount')
def countPeople():
  current_data = get_json_data()
  output = get_baselines()
  for d in current_data:
    building_name = d[BUILDING_CODE]
    client_count = d[CLIENTS]
    output[building_name]["baseline"] = client_count - output[building_name]["baseline"]

  return jsonify(list(output.values()))


# Flask App
app = Flask(__name__)
api = Api(app)
reset_daily_cache()

five_minute_thread = threading.Thread(None, five_minute_timer)
five_minute_thread.start()

long_thread = threading.Thread(None, long_timer)
long_thread.start()

if __name__ == '__main__':
  app.run(debug=True)