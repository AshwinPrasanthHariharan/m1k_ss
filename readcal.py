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
#Channel A Calibration
mgr.reset_block('a',"measure V")
mgr.save()
smu.session._close()
time.sleep(0.5)
subprocess.run(["smu", "-w", "m1k.cal"])
time.sleep(1)
smu.session=Session()
smu.session.add_all()
smu.start(0)
smu.devices[0].ch_a.mode=Mode.SVMI
k,l=calibrate_write_read(smu.devices[0].ch_a)
print("Before Calibration:")
print_deviation("Before Calibration", k, l)
print(smu.devices[0].ch_a.dcr())
mgr.recab("measure V","a",zip(k,l))
mgr.save()
smu.session._close()
subprocess.run(["smu", "-w", "m1k.cal"])
time.sleep(1)
#Channel A Re-Read
smu.session=Session()
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