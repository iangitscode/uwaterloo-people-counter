import json
import psycopg2
import threading
from psycopg2 import sql
from flask import Flask, jsonify
from flask_restful import Api
from flask_cors import CORS
from shared import *

FIVE_MINUTE_DELAY = 60 * 5
LONG_DELAY = 60 * 60 * 24

BUILDING_CODE = "building_code"
CLIENTS = "clients"

# Caches the number of clients for each building for an hour
building_client_count_cache = {}

# Which column in the db should be updated
currcol = 1

# Flask App
app = Flask(__name__)
api = Api(app)
CORS(app)

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
  cursor.execute(sql.SQL("SELECT * FROM " + config["relationname"]))
  result = cursor.fetchall()
  json = {}
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
  while True:
    data = get_json_data()
    if data != None:
      for d in data:
        building_client_count_cache[d[BUILDING_CODE]].append(d[CLIENTS])
    five_minute_event.wait(FIVE_MINUTE_DELAY)

# Runs everyday
# Takes the minimum of all client numbers for the day and dumps it in the database
def long_timer():
  long_event = threading.Event()
  while True:
    (conn, cursor) = connectToDB()
    # Map of building names to minimum number of clients connected in that hour
    to_write = {}

    # Get the minimum number of connected clients that day
    for building in building_client_count_cache:
      to_write[building] = min(building_client_count_cache[building])

    # Write each minimum for the day into the database
    for building in to_write:
      cursor.execute(sql.SQL("UPDATE "+ config["relationname"]+" SET {} = %s WHERE building_name = %s;")
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
    long_event.wait(LONG_DELAY)


# Calculates the number of people in each building
# Based on the historical data
@app.route('/peoplecount')
def countPeople():
  current_data = get_json_data()
  output = get_baselines()
  for d in current_data:
    building_name = d[BUILDING_CODE]
    client_count = d[CLIENTS]
    output[building_name]["people_count"] = max(client_count - output[building_name]["baseline"], 0)
  return jsonify(list(output.values()))

@app.route('/')
def sayHi():
  return "Hello world!"




# Copied from db_setup

# (conn, cursor) = connectToDB()

# cursor.execute("DROP TABLE IF EXISTS " + config["relationname"] + ";")
# cursor.execute("CREATE TABLE "+config["relationname"]+"();")

# for i in range(31 * 4):
#   colName = "col" + str(i)
#   cursor.execute(sql.SQL("ALTER TABLE " + config["relationname"] + " ADD COLUMN {} INT;").format(sql.Identifier(colName)))

# cursor.execute(sql.SQL("ALTER TABLE " + config["relationname"] + " ADD COLUMN building_name VARCHAR;"))

# data = get_json_data()
# if data != None:
#   for d in data:
#     building_client_count_cache[d[BUILDING_CODE]] = [d[CLIENTS]]
#     cursor.execute(sql.SQL("INSERT INTO " + config["relationname"] + "(building_name, col0) VALUES (%s, %s);"),(d[BUILDING_CODE], d[CLIENTS]))

# conn.commit()
# cursor.close()
# conn.close()

# End copy


reset_daily_cache()

five_minute_thread = threading.Thread(None, five_minute_timer)
five_minute_thread.start()

long_thread = threading.Thread(None, long_timer)
long_thread.start()

if __name__ == '__main__':
  app.run(debug=False)