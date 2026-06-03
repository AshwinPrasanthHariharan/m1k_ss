from m1k_utils import *
import time
import numpy as np
import subprocess
import matplotlib.pyplot as plt
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
smu=SMU()
print(smu.devices[0])
mgr=CalibrationManager("m1k.cal")
mgr.reset_all()
mgr.save()
time.sleep(0.5)
#Channel B Calibration
mgr.reset_block('b',"measure V")
mgr.save()
smu.session._close()
time.sleep(0.3)
subprocess.run(["smu", "-w", "m1k.cal"])
time.sleep(1)
print("unplug and replug the device now:(press enter when done)")
input() 
smu.session=Session()
smu.session.add_all()
smu.start(0)
print(smu.devices[0])
smu.devices[0].ch_b.mode=Mode.SVMI
write_values_b, read_values_b = calibrate_write_read(smu.devices[0].ch_b)
print_deviation("Channel B", write_values_b, read_values_b)
mgr.recab("measure V",'b',zip(write_values_b, read_values_b))
mgr.save()
smu.session._close()
time.sleep(0.3)
subprocess.run(["smu", "-w", "m1k.cal"])
time.sleep(1)
print("unplug and replug the device now:(press enter when done)")
input()
smu.session=Session()
smu.session.add_all()
smu.start(0)
print(smu.devices[0])
smu.devices[0].ch_b.mode=Mode.SVMI
write_values_b, read_values_b = calibrate_write_read(smu.devices[0].ch_b)
print_deviation("Channel B After Recalibration", write_values_b, read_values_b)
