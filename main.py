import mysql.connector, os
"""
CREATE TABLE flights (
id INT NOT NULL UNIQUE,
from_city TEXT,
to_city TEXT,
name varchar(40)
);
"""
#END DATABASE MUST HAVE EVERYTHING IN LOWER CASE

db = mysql.connector.connect(
  host = os.environ["db_host"],
  user = os.environ["db_user"],
  password = os.environ["db_pass"],
  database = "testdb"
)
sql = db.cursor()

def get_flights(from_city = None, to_city = None, flight_id = None):
  #priority to arguments: flight_id > to_city > from_city
  if flight_id is not None:
    pass
  elif to_city is not None:
    pass
  elif from_city is not None:
    pass

  else:
    sql.execute("SELECT DISTINCT from_city FROM flights;")


def userinput():
  from_options = sql.fetchall()
  print("Cities we fly from:")
  for item in from_options:
    print(item[0].title())
  home = input('Enter your city: ')
  print("\n")
  print('Here are all the flights departuring/will take off from your city: ')
  sql.execute("SELECT DISTINCT to_city FROM flights WHERE from_city = %s;", (home,))
  to_options = sql.fetchall()
  for item in to_options:
    print(item[0].title())
  dest = input('Enter your desired destination: ')
  print(f"All flights travelling to {dest} from {home}:")
  sql.execute('SELECT * FROM flights WHERE to_city = %s AND from_city = %s;',(dest, home))
  print(sql.fetchall())
  print()
  flightID = int(input('Please select the flight id of the plane you want to board in: '))
  sql.execute("SELECT * FROM flights WHERE id = %s;", (flightID,))
  flight_data = sql.fetchone()
  return flight_data #tuple

def payment():
  os.clear()
  print('Please confirm all details.')
  print()
  print('''
  ----------------------------------------------------------------------------------------------------------------------------------------------
  Flight ID : {flightID}
  From {home} to {dest}
  Time of departure : {hello}
  Time of arrival : {frrfrf}
  ---------------------------------------------------------------------------------------------------------------------------------------------
  ''') #TO DO AFTERWARDS
  confirm = input('')
  print('''
  
  Select mode of payment
  1. Debit Card
  2. Kidney''')

choice = input('Enter the index of your option.')
print('------------------------------------------------------------------------------------------------------------------------------------')
if choice == 1:
  print('okay, please enter the following details to proceed:')
  num = int(input('Your card number (16 digits)'))
  pin = int(input('Your pin'))
  print('Thank You, You may leave this site now.')

if choice ==2:
  print('Okay, an operation has been scheduled at your nearest hospital. You are expected to arrive on 12:00pm in the pon vidyashram hospital')
  print()
  print('Lastly, you are requested to accept our terms of service ')
  
  


userinput()