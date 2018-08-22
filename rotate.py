import gpiozero
from time import sleep
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("steps", type=int)
parser.add_argument("-f", "--forward", action="store_true")
args = parser.parse_args()

pulse = gpiozero.DigitalOutputDevice(15)
direction = gpiozero.DigitalOutputDevice(14)
if args.forward:
    direction.on()
for i in range(args.steps):
    pulse.on()
    sleep(.001)
    pulse.off()

direction.close()
pulse.close()

