import mysql.connector, os, pickle

db = mysql.connector.connect(
  host = os.environ["db_host"],
  user = os.environ["db_user"],
  password = os.environ["db_pass"],
  database = "testdb",
  autocommit = True  # fix planetscale bug
)
sql = db.cursor()

with open("database.dat", "wb") as file:
  for i in ("flights", "booked", "userdata"):
    sql.execute(f"SELECT * FROM {i};")
    data = sql.fetchall()
    pickle.dump(data, file)
  file.flush()
  print("data saved")

db.close()