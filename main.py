import time
from Adafruit_IO import *
import pyfirmata
import mysql.connector
from datetime import datetime
import threading
from flask import Flask, render_template

# Kobler til adafruit og databasen
def connect():
    global analog_input, digital, aio, mycursor, board, mydb
    # kobler til Adafruit dashbordet
    ADAFRUIT_IO_USERNAME = "toot123"
    ADAFRUIT_IO_KEY = "adafruitkey"
    aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

    # Kobler til Arduino
    board = pyfirmata.Arduino('COM4')
    it = pyfirmata.util.Iterator(board)
    it.start()

    analog_input = board.get_pin('a:0:i')
    digital = aio.feeds('toggle')

    # Kobler til MySQL databasen
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="elev",
        database="adafruitlog"
    )
    mycursor = mydb.cursor()

    loop()

def adafruit():
    global data
    # Line Chart
    chart_data = str(analog_input.read())
    aio.send_data('chart', chart_data)
    print('Sending chart data:', chart_data)

    # Tar imot data fra adafruit dashbordet
    toggle = aio.receive(digital.key)
    # Knapp blir trykket skrus på alle lys
    if toggle.value == "ON":
        board.digital[8].write(True)
    # Knapp av skrur av igjen lysa
    elif toggle.value == "OFF":
        board.digital[8].write(False)

    # Logger data til SQL database
    now = datetime.now()
    current_time = str(now.strftime("%d/%m/%Y %H:%M:%S"))
    sql = "INSERT INTO potentiometer (time, value) VALUES (%s, %s)"
    mycursor.execute(sql, (current_time, chart_data))
    mydb.commit()
    print("Data saved to database")

    # Henter data til nettsida
    mycursor.execute("SELECT * FROM potentiometer")
    data = mycursor.fetchall()

# Runs in a thread
def start_webserver(name):
    app = Flask(__name__)

    @app.route('/')
    def home():
        return render_template("index.html", data=data)

    app.run()
# Fires up webserver
thread = threading.Thread(
    target=start_webserver,
    args=(1,), daemon=True)
thread.start()

def loop():
    while True:
        adafruit()
        time.sleep(5)

if __name__ == "__main__":
    connect()

