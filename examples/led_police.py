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
        # Blue flash
        for dev in session.devices:
            dev.set_led(4)
        time.sleep(0.1)

        for dev in session.devices:
            dev.set_led(0)
        time.sleep(0.05)

        for dev in session.devices:
            dev.set_led(4)
        time.sleep(0.1)

        for dev in session.devices:
            dev.set_led(0)
        time.sleep(0.2)

        # Red flash
        for dev in session.devices:
            dev.set_led(1)
        time.sleep(0.1)

        for dev in session.devices:
            dev.set_led(0)
        time.sleep(0.05)

        for dev in session.devices:
            dev.set_led(1)
        time.sleep(0.1)

        for dev in session.devices:
            dev.set_led(0)
        time.sleep(0.2)