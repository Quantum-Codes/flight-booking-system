import mysql.connector, os, random, datetime

db = mysql.connector.connect(
  host = os.environ["db_host"],
  user = os.environ["db_user"],
  password = os.environ["db_pass"],
  database = "testdb",
  autocommit = True  # fix planetscale bug
)
sql = db.cursor()

def generate_id(column = "id", table = "flights"):
  temp_id = random.randint(0,1E8) # 1*10^10 - 10 digits
  while True: # duplicate checking
    sql.execute(f"SELECT {column} FROM {table};")
    existing_id = sql.fetchall()
    if temp_id in existing_id:
      temp_id = random.randint(0,1E10)
    else:
      break
  return temp_id 

stop = lambda x, y: exit() if x > y else None

while True:
  from_city = input("From city: ").lower().strip()
  to_city = input("To city: ").lower().strip()
  timewait = float(input("Enter timedelta(hrs) in arrival, departure: "))
  time = datetime.datetime.strptime(f"{str(random.randint(0,3)).zfill(2)}:00:00", "%H:%M:%S")
  x = 0
  for item in range(int(24 // timewait)):
    str_depart_time = time.strftime("%H:%M:%S")
    time += datetime.timedelta(hours = timewait) # on flight time
    str_arrive_time = time.strftime("%H:%M:%S")
    stop(x, time.hour)
    x = time.hour
    sql.execute("INSERT INTO flights VALUES (%s, %s, %s, 'placehold', %s, %s);", (generate_id(), from_city, to_city, str_arrive_time, str_depart_time))

    time += datetime.timedelta(hours = random.choice([0.5,1])) # flight refuelling time
    from_city, to_city = to_city, from_city # update plane location