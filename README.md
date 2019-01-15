## UWaterloo People Counter

This is a Python service that provides an estimate of the number of people in each building on the University of Waterloo campus. It uses UW API to grab the number of devices connected to each building's wireless router, and compares it to a baseline for each building. This process accounts for devices that are always connected to the router, such as printers. The basic premise of this service is that on average, each person in the building has a phone connected to the wireless.

----

## Running the service

1. Clone the repo, and install the necessary requirements through pip3 (flask, flask_cors, flask_restful, psycopg2)
2. Create a database
3. Create a config file with the contents

```
dbname={database name}
host={database host ip}
user={username}
password={password}
api={api key}
```

4. Run the db_setup.py script with python3 db_setup.py. This will create the necessary rows and columns in the database
5. Run the app with python3 server.py
6. You can now access the endpoint at /peoplecount
7. (Optional) From the /client/ directory, run ng serve to launch a frontend demonstration of this service, and access it from localhost:4200