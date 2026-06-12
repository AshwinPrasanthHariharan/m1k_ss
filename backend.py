from fastapi import FastAPI, HTTPException
import uvicorn
from m1k_utils import *

app = FastAPI()

# Global initialization right at the start
print("Initializing ADALM1000...")
smu=SMU()
smu.start(0)

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
if __name__ == "__main__":
    uvicorn.run(
        "backend:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True
    )