# AIRLINES. NOT AIRPORT
#Currently working on: See available flights

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


def userinput():
  print("Cities we fly from:")
  from_options = get_flights()
  for item in from_options:
    print(item[0].title())
  home = input('Enter your city: ')
  print("\n")
  print('Here are all the flights departuring/will take off from your city: ')
  to_options = get_flights(from_city = home)
  for item in to_options:
    print(item[0].title())
  dest = input('Enter your desired destination: ')
  print(f"All flights travelling to {dest} from {home}:")
  print(get_flights(to_city = dest, from_city = home))
  print()
  flightID = int(input('Please select the flight id of the plane you want to board in: '))
  
  flight_data = get_flights(flight_id = flightID)
  return flight_data #tuple

def payment(flight):
  os.system("clear")
  print('Please confirm all details.')
  print()
  print(f'''
----------------------------------------------------------------------------------------------------------------------------------------------
  Flight ID : {flight[0]}
  Name of flight : {flight[3]}
  From {flight[1]} to {flight[2]}
  Time of departure : 1 am lololol
  Time of arrival : 1am in your dreams. YES CHANGE THIS 
---------------------------------------------------------------------------------------------------------------------------------------------''') #TO DO AFTERWARDS
  confirm = input('')
  print('''\n
  Select mode of payment
  1. Debit Card
  2. Kidney''')

  choice = int(input('Enter the index of your option.'))
  print('------------------------------------------------------------------------------------------------------------------------------------')
  if choice == 1:
    print('okay, please enter the following details to proceed:')
    num = int(input('Your card number (16 digits)'))
    pin = int(input('Your pin'))

  elif choice ==2:
    print('Okay, an operation has been scheduled at your nearest hospital. You are expected to arrive on 12:00pm in the pon vidyashram hospital')
    print('Lastly, you are requested to accept our terms of service to complete our process.')
    print()
  print('''The Flight booking system will not be responsible for any monetary losses/damage done to the users\' properties (or even lives). We  will also not be obliged to provide any sort of refund in any circumstance.''')
  agree = input('do you agree? y/n')
  while 'n' in agree.lower():
    print('please press y to continue')
    agree = input('do you agree y/n')

  print('Thank You, You may leave this site now.')

  
  

print("""FLIGHT BOOKING SYSTEM""")
print('-------------------------------------------------------------------------------------------------------------------------------')
print('''Please choose an appropriate option:
1.Check available flights
2.Book a flight
''')
a = int(input('enter index'))
if a ==2:
  flight = userinput()
  payment(flight)
elif a==1:
  