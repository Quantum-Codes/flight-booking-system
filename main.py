import mysql.connector, os, random, pickle


def setup():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Tiger"
    )
    sql = db.cursor()
    print("Connected!")
    sql.execute("CREATE DATABASE IF NOT EXISTS airline_db;")
    sql.execute("USE airline_db;")
    sql.execute("CREATE TABLE IF NOT EXISTS flights (id INT NOT NULL UNIQUE, from_city TEXT, to_city TEXT,\
name varchar(40), arrival TIME, departure TIME);")
    sql.execute(
        "CREATE TABLE IF NOT EXISTS booked (id INT UNSIGNED PRIMARY KEY, userid INT NOT NULL, flightid INT NOT NULL);")
    sql.execute("CREATE TABLE IF NOT EXISTS userdata (id INT PRIMARY KEY, name varchar(50) UNIQUE NOT NULL,\
age INT UNSIGNED, password varchar(50));")
    db.commit()
    print("Setup db structure.")

    sql.execute("SELECT * FROM flights;")
    if len(sql.fetchall()) > 0:  # records already exist. No need to update. also use ffetchall() instead of len() to prevent unread result error
        return

    # Database loader
    with open("database.dat", "rb") as file:
        # FOR TABLE flights
        data = pickle.load(file)
        for item in data:
            sql.execute(f"INSERT INTO flights VALUES (%s, %s, %s, %s, %s, %s);", item)
        db.commit()
        print(f"Uploaded flights table")

        # FOR TABLE booked
        data = pickle.load(file)
        for item in data:
            sql.execute(f"INSERT INTO booked VALUES (%s, %s, %s);", item)
        db.commit()
        print(f"Uploaded booked table")

        # FOR TABLE userdata
        data = pickle.load(file)
        for item in data:
            sql.execute(f"INSERT INTO userdata VALUES (%s, %s, %s, %s);", item)
        db.commit()
        print(f"Uploaded userdata table")

    db.close()


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

def get_flights(from_city=None, to_city=None, flight_id=None):
    # priority to arguments: flight_id > to_city > from_city
    if flight_id:
        sql.execute("SELECT * FROM flights WHERE id = %s;", (flight_id,))
        return sql.fetchone()

    if from_city and to_city:  # x and y -- > if any one = None, then result = False
        sql.execute('SELECT * FROM flights WHERE to_city = %s AND from_city = %s;', (to_city, from_city))
        return sql.fetchall()
    elif from_city:
        sql.execute("SELECT * FROM flights WHERE from_city = %s;", (from_city,))
        return sql.fetchall()
    else:
        sql.execute("SELECT DISTINCT from_city FROM flights;")
        return sql.fetchall()


def generate_id(column=None, table=None):
    temp_id = random.randint(1E7, 1E8)  # 1*10^7 - 8 digits
    while True:  # duplicate checking
        sql.execute(f"SELECT {column} FROM {table};")
        existing_id = sql.fetchall()
        if temp_id in existing_id:
            temp_id = random.randint(1E7, 1E8)
        else:
            break
    return temp_id


def userinput():
    print("Cities we connect:")
    from_options = get_flights()
    for item in from_options:
        print('>> ', item[0].title())
    home = input('Enter your current location: ').lower().strip()
    dest = input('Enter your desired destination: ').lower().strip()
    sql.execute('SELECT * FROM flights WHERE from_city=%s AND to_city=%s;', (home, dest))
    OneFlight = sql.fetchall()
    mode = 0
    if not OneFlight:  # Just Oneflight - returns False if it is a list of empty tuples
        mode = 1
        TwoFlight = []
        sql.execute('SELECT to_city, id, departure, arrival,from_city FROM flights WHERE from_city = %s;', (home,))
        layer1 = sql.fetchall()
        #Layer1 = all flight with start location as current city. Doesnt necessarily directly connect to destination. Example for direct: chennai - bangalore
        index = 0
        for i in layer1:
            sql.execute(
                'SELECT to_city, id, departure, arrival,from_city FROM flights WHERE from_city = %s AND departure>%s AND to_city = %s;',
                (i[0], i[3], dest)
            )
            layer2 = sql.fetchall()
            #Layer 2 = all flights starting from destination of Layer1 flights connecting the final destination. Example: bangalore - hyderabad
            for j in layer2:
                TwoFlight.append((index, home, i[0], dest, str(i[2]), str(j[3]), i[1], j[1]))
                # i[1], j[1] are id. not to be displayed. i[2], j[3] are datetime. str() to convert to readable time
                index += 1
        if TwoFlight:  # Just Twoflight - returns False if it is a list of empty tuples
            for item in TwoFlight:
                print(item[0:6]) 
        else:   # searching 3 flight connections if 2 is empty. example: chennai - new york
            mode = 2
            journey = list()
            sql.execute('SELECT to_city, id, departure, arrival FROM flights WHERE from_city = %s;', (home,))
            layer1 = sql.fetchall()  # list of tuples
            index = 0
            for i in layer1:
                sql.execute('SELECT to_city, id, departure, arrival FROM flights WHERE from_city = %s AND departure>%s;',
                            (i[0], i[3]))  # fromcity-B  B-C C-destination
                layer2 = sql.fetchall()
                for j in layer2:
                    sql.execute(
                        'SELECT id, arrival, departure, from_city,to_city FROM flights WHERE from_city = %s AND to_city = %s AND departure>%s;',
                        (j[0], dest, j[3]))
                    layer3 = sql.fetchall()
                    for k in layer3:
                        journey.append((index, home, i[0], j[0], dest, str(i[2]), str(k[1]), i[1], j[1], k[0]))
                        index += 1

            for item in journey:
                print(item[:7])
            if journey == []:
              print('No Flight is available.')
              return
    else:
        for num, item in enumerate(OneFlight):
            flight_display = list(item[1:])
            flight_display[3] = str(flight_display[3]) # convert datetime to readable time
            flight_display[4] = str(flight_display[4])
            flight_display[3], flight_display[4] = flight_display[4], flight_display[3] # order- departure, arrival
            print(num, flight_display)

    option = int(input('Enter your desired flight\'s index: '))
    if mode == 2:
        return get_flights(flight_id=journey[option][7]), get_flights(flight_id=journey[option][8]), get_flights(flight_id=journey[option][9])
    elif mode == 1:
        return get_flights(flight_id=TwoFlight[option][6]), get_flights(flight_id=TwoFlight[option][7])
    else:
        return [OneFlight[option]]  # function returns list of flights even if only 1 flight


def display_flight(flight):
    for item in flight:
        print(f'''
  ----------------------------------------------------------------------------------------------------------------------------------------------
    Flight ID : {item[0]}
    Name of flight : {item[3]}
    From {item[1]} to {item[2]}
    Time of departure : {item[5]}
    Time of arrival : {item[4]} 
  ---------------------------------------------------------------------------------------------------------------------------------------------''')


def display_tickets(user):
    sql.execute("SELECT * FROM booked WHERE userid = %s;", (user,))
    tickets = sql.fetchall()
    print("Your booked flights:")
    if len(tickets) == 0:
        print("You have not booked any tickets.")
        return

    print("TicketID ", "FlightID ", "Plane    ", "Departure", "Arrival", sep="   ")
    for item in tickets:
        flight = get_flights(flight_id=item[2])
        print(item[0],' '*(12-len(str(item[0]))), flight[0],' '*(12-len(str(flight[0]))), flight[3],' '*(12-len(str(flight[3]))), str(flight[5]),' '*(12-len(str(flight[5]))), str(flight[4]),' '*(12-len(str(flight[4]))), sep="")


def payment(flight, user):
    if not flight:
      return
    print('Please confirm all details.')
    print()
    display_flight(flight)
    confirm = input('Confirm?(y/n): ').strip().lower()
    if confirm not in ("yes", "y"):  # rejected. so cancel booking process
        return
    print('''\n
  Select mode of payment
  1. Debit Card
  2. Credit Card''')

    choice = int(input('Enter the index of your option: '))
    print(
        '------------------------------------------------------------------------------------------------------------------------------------')
    # does same stuff for both options
    print('Please enter the following details to proceed: ')
    num = int(input('Your card number (16 digits): '))
    pin = int(input('Your pin: '))

    ticket_ids = []
    for item in flight:
        ticket_id = generate_id("id", "booked")
        sql.execute("INSERT INTO booked (id, userid, flightid) VALUES (%s, %s, %s);", (ticket_id, user, item[0]))
        ticket_ids.append(ticket_id)
    db.commit()
    print("Payment Successful.")
    print("Ticket id:", ticket_ids)


def cancel(user):
    ticketid = input('Ticket ID to cancel: ').strip()
    sql.execute('SELECT * FROM booked WHERE id = %s;', (ticketid,))
    if not sql.fetchone():
        print("Ticket doesn't exist.")
        return
    sql.execute('DELETE FROM booked WHERE id = %s AND userid = %s;', (ticketid, user))
    db.commit()
    print('Your flight has been successfully cancelled.')


def signup():
    user_id = generate_id(column="id", table="userdata")
    name = input('Please Enter your full name: ').lower()
    sql.execute('SELECT name FROM userdata;')
    check = [item[0] for item in sql.fetchall()]
    if name in check:
        print('User already exists')
        return
    age = input('Provide your age: ')
    if not age.isdigit() or int(age) < 0:
        return
    pass1 = "a"
    pass2 = "b"
    while pass1 != pass2:
        pass1 = input('Enter your new password: ').strip()
        pass2 = input('Confirm your password: ').strip()
    sql.execute('INSERT INTO userdata (id,name,age,password) VALUES (%s,%s,%s,%s);', (user_id, name, age, pass1))
    db.commit()
    print()
    print('Signed up successfully')
    return user_id


def login():
    username = input('Enter your username: ').lower()
    sql.execute('SELECT id, password FROM userdata WHERE name = %s', (username,))
    user = sql.fetchone()
    if user is None:
        print("No such user exists. Signup if you don't have an account.")
        return
    input_pass = None
    password = user[1]
    while password != input_pass:
        input_pass = input('Enter your password: ').strip()
        if password != input_pass:
            print('Incorrect Password. Please try again.')

    print('Logged in successfully')
    return user[0]


def authenticate():
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


#setup() #sets up and load database


db = mysql.connector.connect(
  host = "localhost",
  user = "root",
  password = "Tiger",
  database = "airline_db",
  autocommit = True
)
sql = db.cursor()




a = 0
user = None
while a != 5:
    print(
        '-------------------------------------------------------------------------------------------------------------------------------')

    print("""\t\t\t\t\tFLIGHT BOOKING SYSTEM""")
    print(
        '-------------------------------------------------------------------------------------------------------------------------------')
    if not user:  # logged out.
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
        print("FlightID   ", "Plane        ", "Flying from", "   Flying to  ", "   Departure" + "  Arrival")
        for item in allflights:
            flight = get_flights(flight_id=item[0])
            print(item[0], "    ", item[3], "    ", item[1], ' ' * (15 - len(item[1])), item[2], ' ' * (15 - len(item[2])), str(item[5]), ' ' * (11 - len(str(item[5]))), str(item[4]), sep="")
    elif a == 2:
        flight = userinput()
        payment(flight, user)

    elif a == 3:
        display_tickets(user)

    elif a == 4:
        cancel(user)
    else:
        print("Exiting program.")
        db.close()
        break
