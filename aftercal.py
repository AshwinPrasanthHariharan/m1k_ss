#Channel A Re-Rereadd
from m1k_utils import *
import time
import numpy as np
import matplotlib.pyplot as plt
smu=SMU()
mgr=CalibrationManager("m1k.cal")
def calibrate_write_read(channel, v_start=0, v_stop=5, steps=11, samples=100, settle_s=1):
    write_values = np.linspace(v_start, v_stop, steps).tolist()
    read_values = []

    for v in write_values:
        channel.dc(float(v))
        time.sleep(settle_s)
        read_values.append(float(channel.dcr(samples)))

    return write_values, read_values


def print_deviation(label, write_values, read_values):
    deviations = [read - write for write, read in zip(write_values, read_values)]
    abs_deviations = [abs(deviation) for deviation in deviations]

    print(f"{label} Deviation:")
    for write, read, deviation in zip(write_values, read_values, deviations):
        print(
            f"Written: {write:.4f} V, Read: {read:.4f} V, Deviation: {deviation:+.4f} V"
        )

    print(
        f"{label} Summary: mean abs deviation = {np.mean(abs_deviations):.6f} V, "
        f"max abs deviation = {np.max(abs_deviations):.6f} V"
    )
smu.session.add_all()
smu.start(0)
smu.devices[0].ch_a.mode=Mode.SVMI
ki,li=calibrate_write_read(smu.devices[0].ch_a)
print("After Calibration:")
print_deviation("After Calibration", ki, li)
print(smu.devices[0].ch_a.dcr())
smu.session._close()
smu.session=Session()
smu.session.add_all()
smu.start(0)
smu.devices[0].ch_a.mode=Mode.SVMI
time.sleep(0.5)
smu.session._close()

smu.session=Session()
smu.session.add_all()
smu.start(0)
smu.devices[0].ch_b.mode=Mode.SVMI
ki_b,li_b=calibrate_write_read(smu.devices[0].ch_b)
print("After Calibration Channel B:")
print_deviation("After Calibration Channel B", ki_b, li_b)
print(smu.devices[0].ch_b.dcr())
smu.session._close()
smu.session=Session()
smu.session.add_all()
smu.start(0)
smu.devices[0].ch_b.mode=Mode.SVMI
time.sleep(0.5)
smu.session._close()
