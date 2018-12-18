import psycopg2
from psycopg2 import sql

conn = psycopg2.connect("dbname=postgres user=snipower host='localhost' password=thisismypassword")
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS buildingdb;")
cursor.execute("CREATE TABLE buildingdb();")

for i in range(24 * 7):
  # cursor.execute("ALTER TABLE buildingdb ADD COLUMN %s INT;", str(i))
  colName = "col" + str(i)
  cursor.execute(sql.SQL("ALTER TABLE buildingdb ADD COLUMN {} INT;").format(sql.Identifier(colName)))

conn.commit()
cursor.close()
conn.close()