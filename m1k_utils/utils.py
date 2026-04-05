from pysmu import Session, Mode, Channel
import time
class dev:
    def __init__(self,dev):
        self.dev = dev
        self.serial = dev.serial
        self.fwver = dev.fwver
        self.hwver = dev.hwver
        self.default_rate = dev.default_rate
        self.sample_rate = dev.sample_rate
        self.calibration = dev.calibration
        self.ch_a = (dev.channels['A'])       
        self.ch_b =(dev.channels['B'])

    def set_led(self,val):
        self.dev.set_led(val)
    def __str__(self):
        return f"Serial: {self.serial}, Firmware: {self.fwver}, Hardware: {self.hwver}"
class session(Session):
    def __init__(self):
        super().__init__()
    @property
    def devices(self):
        return [dev(d) for d in super().devices]
def print_device_info(dev):
    print("=== ADALM1000 Device Info ===")
    print(f"  Serial:      {dev.serial}")
    print(f"  Firmware:    {dev.fwver}")
    print(f"  Hardware:    {dev.hwver}")
    print(f"  Default rate:{dev.default_rate} Hz")
    print(f"  Sample rate: {dev.sample_rate} Hz")
    print(f"  Calibration: {dev.calibration}", end="\n\n")


def cycle_leds(dev, n_cycles=12, delay=0.5):
    patterns = [1, 2, 4, 3, 5, 6, 7, 0]

    for i in range(n_cycles):
        val = patterns[i % len(patterns)]
        dev.set_led(val)
        print(f"Cycle {i+1:2d}: LED mask = {val:03b}")
        time.sleep(delay)

    dev.set_led(0)