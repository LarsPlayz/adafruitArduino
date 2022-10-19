import time
from Adafruit_IO import *
import pyfirmata
import mysql.connector
from datetime import datetime


#kobler til Adafruit dashbordet
ADAFRUIT_IO_USERNAME = "toot123"
ADAFRUIT_IO_KEY = "adafruitkey"
aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

#Kobler til MySQL databasen
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="elev",
  database="adafruitlog"
)
mycursor = mydb.cursor()

#Kobler til Arduino
board = pyfirmata.Arduino('COM4')
it = pyfirmata.util.Iterator(board)
it.start()

analog_input = board.get_pin('a:0:i')
digital = aio.feeds('toggle')

while True:
    #Line Chart
    chart_data = str(analog_input.read())
    aio.send_data('chart', chart_data)
    print('Sending chart data:', chart_data)

    #Logger data til SQL database
    now = datetime.now()
    current_time = str(now.strftime("%d/%m/%Y %H:%M:%S"))
    sql = "INSERT INTO potentiometer (time, value) VALUES (%s, %s)"
    mycursor.execute(sql, (current_time, chart_data))
    mydb.commit()
    print("Data saved to database")

    #Tar imot data fra adafruit dashbordet
    toggle = aio.receive(digital.key)
    #Knapp blir trykket skrus på alle lys
    if toggle.value == "ON":
        board.digital[8].write(True)
    #Knapp av skrur av igjen lysa
    elif toggle.value == "OFF":
        board.digital[8].write(False)

    #Delay for å ungå rate limit
    time.sleep(5)
