import time
from Adafruit_IO import Client
import pyfirmata

ADAFRUIT_IO_USERNAME = "toot123"
ADAFRUIT_IO_KEY = "aio_pwBZ2057cWM6VRrk1xfzvrU0nQWg"
aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

board = pyfirmata.Arduino('COM4')
it = pyfirmata.util.Iterator(board)
it.start()

analog_input = board.get_pin('a:0:i')
digital = aio.feeds('toggle')
slider = aio.feeds('lights')
run_count = 0

while True:
    #Counter
    print('Sending count:', run_count)
    run_count += 1
    aio.send_data('counter', run_count)


    #Line Chart
    chart_data = analog_input.read()
    print('Sending chart:', chart_data)
    aio.send_data('chart', chart_data)


    #Styrer 5 Lys
    #Tar imot data fra adafruit dashbordet
    data = aio.receive(digital.key)
    lights = aio.receive(slider.key)
    #.key gir en lang liste med ting, så .value leser bare "value" delen
    lightVal = lights.value
    #Plusser på 9 fordi bruker port 9-13 på arduinoen
    lightNum = int(lightVal) + 9
    print('Light:', lightVal)
    #Knapp blir trykket skrus på alle lys
    if data.value == "ON":
        lightNum = 14
    #Knapp av skrur av igjen lysa
    elif data.value == "OFF" and lightNum == 9:
        lightNum = 9
    #For å skru på lysa
    for n in range(8, lightNum):
        board.digital[n].write(True)
    #For å skru av lysa
    for n in range(13, lightNum - 1, -1):
        board.digital[n].write(False)

    #Delay for å ungå rate limit
    time.sleep(5)