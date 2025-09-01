from pywebio.input import *
from pywebio.output import *
from pywebio import start_server
import uuid


user={'Clinton': 'abc1234'}
routes={
    "Newcastle-Leeds":30,
    "Newcastle-Manchester":35,
    "Newcastle-Birmingham":40,
    "Newcastle-London":50,
    "Newcastle-Edinburgh":30
}

bookings={}
available_seats={}


def login():
    clear()
    put_html("<H1>Login to access your FlixBus account</H1>")
    put_buttons(["Forgot password"], onclick=[password_reset])
    data=input_group("Login", [
        input("Name:", name='name', required=True),
        input("Password", name='password', type=PASSWORD, required=True)
    ])
    username=data['name']
    password=data['password']
    if username in user and user[username]:
        home(username)
    else:
        toast("Incorrect username or password", color='error')
        login()

def password_reset():
    clear()
    put_html("<H1>Password Reset</H1>")
    put_buttons(["Back"], onclick=[login])
    while True:
        username=input("Enter username:", required=True)
        if username not in user:
            toast("Invalid username")
        else:
            break
    while True:
        password_reset_data=input_group("Password reset",[
            input("Enter new password:", name="new_password", type=PASSWORD, required=True),
            input("Confirm password", name="confirm_password", type=PASSWORD, required=True)
        ])
        if password_reset_data["new_password"] != password_reset_data["confirm_password"]:
            toast("Passwords dont match")
        else:
            break
    user[username]=password_reset_data["new_password"]
    toast("Password has been updated successfully")

def home(user):
    clear()
    put_html(f"<H1>Welcome {user}</H1>")
    put_buttons(["My bookings", "Logout"], onclick=[lambda: my_bookings(user), login])
    if user not in bookings:
        bookings[user]=[]

    data=input_group("Trip details",[
        radio("Select trip type", name="trip_type", options=["Round-trip", "Single"], required=True),
        select("Select route:", name="route", options=list(routes.keys()), required=True),
        select("Number of passengers", name="passengers", options=[str(i) for i in range(1,16)], required=True),
        input("Departure date", name="departure", type=DATE, required=True),
        input("Return date", name="return", type=DATE, required=True)
    ])
    trip_type=data["trip_type"]
    route=data["route"]
    number_of_passengers=int(data["passengers"])
    departure_date=data["departure"]
    return_date=data["return"] if trip_type == "Round-trip" else None
    passenger_info=[]
    for i in range(number_of_passengers):
        passenger_data=input_group(f"Passenger{i+1}", [
            input("Full Name:", name="passenger_name", required=True),
            select("Age:", name="age", options=[str(i) for i in range(1,100)], required=True),
            input("Number", name="passenger_number",type=NUMBER, required=True)
        ])
        passenger_info.append(passenger_data)

    current_booking={
        "trip_type":trip_type,
        "route":route,
        "passengers":number_of_passengers,
        "departure_date":departure_date,
        "return_date":return_date,
        "price":routes[route]*number_of_passengers*(2 if trip_type=="Round-trip" else 1)
    }
    booking_summary(user, current_booking)



def booking_summary(user, current_booking):
    clear()
    put_html("<H1>Booking summary</H1>")
    put_text(f"Trip type:{current_booking['trip_type']}")
    put_text(f"Route:{current_booking['route']}")
    put_text(f"Passengers:{current_booking['passengers']}")
    put_text(f"Departure:{current_booking['departure_date']}")
    if current_booking['trip_type']=="Round-trip":
        put_text(f"Return:{current_booking['return_date']}")
    put_text(f"Price:{current_booking['price']}")
    put_buttons(["Confirm", "Cancel"], onclick=[lambda: confirmation_booking(user, current_booking), lambda:home(user)])

def confirmation_booking(user, current_booking):
    clear()
    key=(current_booking["route"], current_booking["departure_date"])
    if key not in available_seats:
        available_seats[key]=10
    if available_seats[key]<current_booking["passengers"]:
        toast("No available seats", color='error')
        home(user)
        return

    available_seats[key]-=current_booking["passengers"]
    booking_id="BKG-" + str(uuid.uuid4())[:8].upper()
    current_booking["booking_id"]=booking_id
    bookings[user].append(current_booking)
    clear()
    put_html("<H1>Booking confirmation</H1>")
    put_text(f"Booking ID:{booking_id}")
    put_text(f"You have:{len(bookings[user])} booking(s).")
    put_buttons(["Back", "My bookings"], onclick=[lambda:home(user), lambda: my_bookings(user)])


def my_bookings(user):
    clear()
    put_html("<H1>My bookings</H1>")
    if not bookings[user]:
        put_text("No bookings yet...")
    else:
        for b in bookings[user]:
            put_html(f"<b>ID:</b> {b['booking_id']} | {b['route']} | {b['departure_date']} | Price: {b['price']} | Passengers: {b['passengers']}")
            put_buttons(["Cancel"], onclick=[lambda b_id=b["booking_id"]: cancel_booking(user, b_id)])
    put_buttons(["Back"], onclick=[lambda: home(user)])

def cancel_booking(user, booking_id):
    clear()
    bookings[user]=[b for b in bookings[user] if b ["booking_id"] != booking_id]
    toast("Booking canceled", color='success')
    my_bookings(user)



if __name__ == '__main__':
    start_server(login, port=500, debug=True)
