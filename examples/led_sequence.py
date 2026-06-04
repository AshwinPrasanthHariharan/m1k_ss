from signal import signal, SIG_DFL, SIGINT
import sys
import time

from pysmu import Session

if __name__ == '__main__':
    signal(SIGINT, SIG_DFL)

    session = Session()

    if not session.devices:
        print("No devices found")
        sys.exit(1)

    while True:
        # Blue
        for dev in session.devices:
            dev.set_led(4)
        time.sleep(0.15)

        # Green
        for dev in session.devices:
            dev.set_led(2)
        time.sleep(0.15)

        # Red
        for dev in session.devices:
            dev.set_led(1)
        time.sleep(0.15)

        # Green
        for dev in session.devices:
            dev.set_led(2)
        time.sleep(0.15)