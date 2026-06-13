from fastapi import FastAPI, HTTPException
import uvicorn
from m1k_utils import *

app = FastAPI()

# Global initialization right at the start
print("Initializing ADALM1000...")
smu=SMU()
smu.start(0)

def gain_phase(inp, out):
    x = np.asarray(inp, dtype=float)
    y = np.asarray(out, dtype=float)

    # Remove DC
    x = x - np.mean(x)
    y = y - np.mean(y)

    N = len(x)

    # FFT
    X = np.fft.rfft(x)
    Y = np.fft.rfft(y)

    # Ignore DC bin
    k = np.argmax(np.abs(X[1:])) + 1

    # Transfer function
    H = Y[k] / X[k]

    mag_linear = np.abs(H)
    mag_db = 20 * np.log10(mag_linear)

    # 1. Get raw phase and frequency
    raw_phase_deg = np.angle(H, deg=True)
    freq_cycles_per_sample = k / N

    # 2. Hardware delay compensation (0.42 samples)
    hardware_delay_samples = 0.42 
    
    # Calculate how many degrees of phase lag this time delay causes at this specific frequency
    phase_error_deg = freq_cycles_per_sample * hardware_delay_samples * 360.0
    
    # 3. Add the error back to advance the phase and correct the hardware lag
    true_phase_deg = raw_phase_deg - phase_error_deg

    # Optional: Keep phase wrapped strictly between -180 and +180
    true_phase_deg = (true_phase_deg + 180) % 360 - 180

    return {
        "frequency_cycles_per_sample": freq_cycles_per_sample,
        "magnitude_linear": mag_linear,
        "magnitude_db": mag_db,
        "phase_deg": true_phase_deg,
        "raw_phase_deg": raw_phase_deg  # Good to keep around for debugging
    }

@app.get("/rva")
def read_voltage():
    """Endpoint for Streamlit to query."""
    if not smu or not smu.devices:
        raise HTTPException(status_code=503, detail="Hardware not connected")
    
    try:
        dev = smu.devices[0]
        time.sleep(0.05)
        channel_a_volts = dev.ch_a.dcr()
        return {
            "channel_a": channel_a_volts,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/sva/{voltage}")
def set_voltage(voltage: float):
    if not smu or not smu.devices:
        raise HTTPException(status_code=503, detail="Hardware not connected")
    
    try:
        dev = smu.devices[0]
        dev.ch_a.dc(voltage)
        time.sleep(0.05)
        return {"message": "Voltage set successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/rvb")
def read_voltage():
    """Endpoint for Streamlit to query."""
    if not smu or not smu.devices:
        raise HTTPException(status_code=503, detail="Hardware not connected")
    
    try:
        dev = smu.devices[0]
        time.sleep(0.05)
        channel_b_volts = dev.ch_b.dcr()
        return {
            "channel_b": channel_b_volts,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/svb/{voltage}")
def set_voltage(voltage: float):
    if not smu or not smu.devices:
        raise HTTPException(status_code=503, detail="Hardware not connected")
    
    try:
        dev = smu.devices[0]
        dev.ch_b.dc(voltage)
        time.sleep(0.05)
        return {"message": "Voltage set successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/pulse/{in_ch}/{out_ch}/{frequency}")
def trigger_pulse( frequency: float, in_ch: str, out_ch: str):
    return gain_phase(*(smu.devices[0].pulse_in_out(1/frequency*10_000, in_ch=in_ch, out_ch=out_ch)))

if __name__ == "__main__":
    uvicorn.run(
        "backend:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True
    )