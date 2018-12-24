import psycopg2
from psycopg2 import sql

conn = psycopg2.connect("dbname=postgres user=snipower host='localhost' password=thisismypassword")
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS buildingdb;")
cursor.execute("CREATE TABLE buildingdb();")

for i in range(31 * 4):
  colName = "col" + str(i)
  cursor.execute(sql.SQL("ALTER TABLE buildingdb ADD COLUMN {} INT;").format(sql.Identifier(colName)))

cursor.execute(sql.SQL("ALTER TABLE buildingdb ADD COLUMN building_name VARCHAR;"))

conn.commit()
cursor.close()
conn.close()