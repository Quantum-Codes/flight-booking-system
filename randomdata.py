import mysql.connector, os, random, datetime, string

db = mysql.connector.connect(
  host = os.environ["db_host"],
  user = os.environ["db_user"],
  password = os.environ["db_pass"],
  database = "testdb",
  autocommit = True  # fix planetscale bug
)
sql = db.cursor()

sql.execute("SELECT id FROM flights;")
ids = sql.fetchall()
for item in ids:
  plane = random.choice((f"Airbus {random.choice(string.ascii_uppercase)}", f"Boeing {random.randint(0,9)}")) + str(random.randint(0,99)).zfill(2)
  sql.execute("UPDATE flights SET name = %s WHERE id = %s;",(plane,item[0]))
  
"""
def generate_id(column = "id", table = "flights"):
  temp_id = random.randint(1E7,1E8) # 1*10^10 - 10 digits
  while True: # duplicate checking
    sql.execute(f"SELECT {column} FROM {table};")
    existing_id = sql.fetchall()
    if temp_id in existing_id:
      temp_id = random.randint(1E7,1E8)
    else:
      break
  return temp_id 

stop = lambda x, y: exit() if x > y else None

while True:
  plane = random.choice((f"Airbus {random.choice(string.ascii_uppercase)}", f"Boeing {random.randint(0,9)}")) + str(random.randint(0,99)).zfill(2)
  from_city = input("From city: ").lower().strip()
  to_city = input("To city: ").lower().strip()
  timewait = float(input("Enter timedelta(hrs) in arrival, departure: "))
  a = float(input("delay: ").strip())
  time = datetime.datetime.strptime(f"{str(random.randint(a,a+3)).zfill(2)}:00:00", "%H:%M:%S") #0 to 3
  x = 0
  for item in range(int(24 // timewait)):
    str_depart_time = time.strftime("%H:%M:%S")
    time += datetime.timedelta(hours = timewait) # on flight time
    str_arrive_time = time.strftime("%H:%M:%S")
    stop(x, time.hour)
    x = time.hour
    sql.execute("INSERT INTO flights VALUES (%s, %s, %s, %s, %s, %s);", (generate_id(), from_city, to_city, plane, str_arrive_time, str_depart_time))

    time += datetime.timedelta(hours = random.choice([(timewait/2),(timewait/2)+0.5])) # flight refuelling time
    from_city, to_city = to_city, from_city # update plane location
"""