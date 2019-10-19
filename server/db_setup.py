import psycopg2
from psycopg2 import sql
from shared import *

(conn, cursor) = connectToDB()

cursor.execute("DROP TABLE IF EXISTS buildingdb;")
cursor.execute("CREATE TABLE buildingdb();")

for i in range(31 * 4):
  colName = "col" + str(i)
  cursor.execute(sql.SQL("ALTER TABLE buildingdb ADD COLUMN {} INT;").format(sql.Identifier(colName)))

cursor.execute(sql.SQL("ALTER TABLE buildingdb ADD COLUMN building_name VARCHAR;"))

# data = get_json_data()
# if data != None:
#   for d in data:
#     building_client_count_cache[d[BUILDING_CODE]] = [d[CLIENTS]]
#     cursor.execute(sql.SQL("INSERT INTO buildingdb(building_name, col0) VALUES (%s, %s);"),(d[BUILDING_CODE], d[CLIENTS]))

conn.commit()
cursor.close()
conn.close()