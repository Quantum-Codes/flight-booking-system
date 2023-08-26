# AIRLINES. NOT AIRPORT
#END DATABASE MUST HAVE EVERYTHING IN LOWER CASE

import mysql.connector, os, random
"""
Setup SQL queries:


CREATE TABLE flights (
id INT NOT NULL UNIQUE,
from_city TEXT,
to_city TEXT,
name varchar(40),
arrival DATETIME,
departure DATETIME
);


CREATE TABLE booked (
id INT UNSIGNED PRIMARY KEY,
userid INT NOT NULL,
flightid INT NOT NULL
);


CREATE TABLE userdata (
id INT PRIMARY KEY,
name varchar(50) UNIQUE NOT NULL,
age INT UNSIGNED,
password varchar(50)
);
"""

db = mysql.connector.connect(
  host = os.environ["db_host"],
  user = os.environ["db_user"],
  password = os.environ["db_pass"],
  database = "testdb",
  autocommit = True  # fix planetscale bug
)
sql = db.cursor()
"""
import time
print("started")
#sql.execute("UPDATE flights SET from_city = 'lol' WHERE from_city = 'lop';")
sql.execute("SELECT * FROM flights;")
#db.commit()
x=sql.fetchall()
time.sleep(21)
sql.execute("SELECT id FROM flights;")
#x=sql.fetchall()
print("No errors ")
exit()#"""

def get_flights(from_city = None, to_city = None, flight_id = None):
  #priority to arguments: flight_id > to_city > from_city
  if flight_id:
    sql.execute("SELECT * FROM flights WHERE id = %s;", (flight_id,))
    return sql.fetchone()

  if from_city and to_city: #x and y -- > if any one = None, then result = False
    sql.execute('SELECT * FROM flights WHERE to_city = %s AND from_city = %s;',(to_city, from_city))
    return sql.fetchall()
  elif to_city:
    #IF REMAINS EMPTY THEN PUT HERE THE if from_city and to_city BLOCK
    pass
  elif from_city:
    sql.execute("SELECT DISTINCT to_city FROM flights WHERE from_city = %s;", (from_city,))
    return sql.fetchall()
  else:
    sql.execute("SELECT DISTINCT from_city FROM flights;")
    return sql.fetchall()


def generate_id(column = None, table = None):
  temp_id = random.randint(0,1E8) # 1*10^10 - 10 digits
  while True: # duplicate checking
    sql.execute(f"SELECT {column} FROM {table};")
    existing_id = sql.fetchall()
    if temp_id in existing_id:
      temp_id = random.randint(0,1E10)
    else:
      break
  return temp_id


def userinput():
  print("Cities we fly from:")
  from_options = get_flights()
  for item in from_options:
    print('>> ',item[0].title())
  home = input('Enter your city: ').lower().strip()
  print("\n")
  print('Here are all the destinations connected to your location: ')
  to_options = get_flights(from_city = home)
  for item in to_options:
    print('>> ',item[0].title())
  dest = input('Enter your desired destination: ').lower().strip()
  print(f"All flights travelling to {dest} from {home}:")
  print(get_flights(to_city = dest, from_city = home))
  print()
  flightID = int(input('Please select the flight id of the plane you want to board in: ').strip())
  
  flight_data = get_flights(flight_id = flightID)
  return flight_data #tuple

def display_flight(flight):
  print(f'''
----------------------------------------------------------------------------------------------------------------------------------------------
  Flight ID : {flight[0]}
  Name of flight : {flight[3]}
  From {flight[1]} to {flight[2]}
  Time of departure : {flight[5]}
  Time of arrival : {flight[4]} 
---------------------------------------------------------------------------------------------------------------------------------------------''') 

def display_tickets(user):
  sql.execute("SELECT * FROM booked WHERE userid = %s;", (user,))
  tickets = sql.fetchall()
  print("Your booked flights:")
  if len(tickets) == 0:
    print("You have not booked any tickets.")
  for item in tickets:
    flight = get_flights(flight_id = item[2])
    print("TicketID", "FlightID", "Plane   ", "Departure \t\t", "Arrival", sep = "\t")
    print(item[0], flight[0], flight[3], flight[5], flight[4], sep = "\t")

def payment(flight, user):
  os.system("clear")
  print('Please confirm all details.')
  print()
  display_flight(flight)#TO DO AFTERWARDS
  confirm = input('Confirm?(y/n): ').strip().lower()
  if confirm not in ("yes", "y"): # rejected. so cancel booking process 
    return
  print('''\n
  Select mode of payment
  1. Debit Card''')

  choice = int(input('Enter the index of your option: '))
  print('------------------------------------------------------------------------------------------------------------------------------------')
  if choice == 1:
    print('Please enter the following details to proceed: ')
    num = int(input('Your card number (16 digits): '))
    pin = int(input('Your pin: '))
 

  ticket_id = generate_id("id", "booked")
  sql.execute("INSERT INTO booked (id, userid, flightid) VALUES (%s, %s, %s);", (ticket_id, user, flight[0]))
  db.commit()
  print("Payment Successful.")
  print("Ticket id:", ticket_id)


def cancel(user):
  flightid = input('Flight ID to cancel: ').strip()
  sql.execute('DELETE FROM booked WHERE id = %s AND userid = %s;',(flightid, user))
  db.commit()
  print('Your flight has been successfully cancelled.')


def signup():
  user_id = generate_id(column = "id", table = "userdata")
  name = input('Please Enter your full name: ').lower()
  sql.execute('SELECT name FROM userdata;')
  check = [item[0] for item in sql.fetchall()]
  if name in check:
    print('User already exists')
    return 
  age = input('Provide your age: ')
  if not age.isdigit() and int(age) < 0:
    return
  pass1 = "a"
  pass2 = "b"
  while pass1 != pass2:
    pass1 = input('Enter your new password').strip()
    pass2 = input('Confirm your password').strip()
  sql.execute('INSERT INTO userdata (id,name,age,password) VALUES (%s,%s,%s,%s);',(user_id, name, age, pass1))
  db.commit()
  return user_id

def login():
  username = input('Enter your username: ').lower()
  sql.execute('SELECT id, password FROM userdata WHERE name = %s',(username,))
  user = sql.fetchone()
  if user is None:
    print("No such user exists. Signup if you don't have an account.")
    return 
  input_pass = None
  password = user[1]
  while password!= input_pass:
    input_pass = input('Enter your password: ').strip()
    if password != input_pass:
      print('Incorrect Password. Please try again.')

  print('Logged in successfully')
  return user[0]
   
  
  

def authenticate(): # change func name
  while True:
    print("""You have not logged in. Either:
  1. Login
  2. Signup (for new users)
""")
    action = int(input("Enter option id: "))
    if action == 1:
      user_id = login()
    elif action == 2:
      user_id = signup()
    else:
      print("Invalid option.")
      continue
    return user_id
  

a = 0
user = None
while a != 5:
  print('-------------------------------------------------------------------------------------------------------------------------------')

  print("""\t\t\t\t\tFLIGHT BOOKING SYSTEM""")
  print('-------------------------------------------------------------------------------------------------------------------------------')
  if not user: # logged out.
    user = authenticate()
    continue
    
  print('''Please choose an appropriate option:
  1. View all flights
  2. Book a flight
  3. Check your flight status
  4. Cancel your flight
  5. Exit
  ''')
  a = int(input('Enter option index: '))

  if a == 1:
    sql.execute("SELECT * FROM flights;")
    allflights = sql.fetchall()
    for item in allflights:
      print(item)
  elif a == 2:
    flight = userinput()
    payment(flight, user)
  
  elif a == 3:
    display_tickets(user)

  elif a == 4:
    cancel(user)
  else:
    print("Exiting program.")
    break