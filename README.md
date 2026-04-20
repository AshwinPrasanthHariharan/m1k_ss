# 📊 Spreadsheet-Driven Data Acquisition & Signal Analysis (ADALM M1K)

## 🚀 Overview

This project is a **spreadsheet-driven data acquisition and signal analysis system** built using the **ADALM1000 (M1K)** and **PySMU**.

It provides a structured way to:

* Acquire **voltage and current signals**
* Perform **signal analysis (FFT, frequency response)**
* Visualize results through a **spreadsheet-like interface**

The system is designed with a **clean separation between UI and computation**, where:

* **Excel (VBA)** acts as the control interface
* **Python backend** handles hardware and signal processing

---

## 🧠 Core Idea

> **Spreadsheet = Control Panel**
> **Python = Signal Engine**

* Cells → Input parameters (sample rate, waveform, sweep range)
* Buttons → Actions (Acquire, FFT, Sweep)
* Tables → Data (raw signals, FFT, sweep results)
* Charts → Visualization

**No signal computation happens in the UI.**

---

## ⚙️ System Architecture

```
Excel (UI + VBA)
│
├─ Reads inputs from cells
├─ Sends commands (HTTP / file-based)
├─ Displays results in tables & charts
│
└───────────────► Python Backend
                 │
                 ├─ Device control (PySMU)
                 ├─ Data acquisition
                 ├─ FFT & sweep analysis
                 ├─ Signal management (signal_id)
                 │
                 └─ Returns structured data
```

Optional:

```
Univer Sheets (Web UI)
        │
        └── Uses same backend (UI-independent design)
```

---

## 🔑 Key Features

### 1. Device Handling

* ADALM1000 integration via PySMU
* Connection status monitoring
* LED sanity check

---

### 2. Data Acquisition

* Finite sample capture
* Voltage & current measurement
* Parameter-driven acquisition

---

### 3. Signal Analysis

* Time-domain visualization
* FFT magnitude computation
* Frequency response via sine sweep
* VI (Voltage-Current) characterization

---

### 4. Signal Abstraction (Important)

Each dataset is treated as a **Signal object**:

* Unique `signal_id`
* Metadata (parameters used)
* Data arrays (time, voltage, current, frequency)

This enables:

* Traceability
* Reproducibility
* Multiple experiments without overwriting data

---

### 5. Spreadsheet-Based Workflow

* Cells = knobs
* Buttons = actions
* Tables = results
* Charts = derived views

---

## 🔄 Workflow

1. Enter parameters in Excel
2. Click action (Acquire / FFT / Sweep)
3. VBA sends request to Python backend
4. Backend processes data / hardware
5. New signal created with `signal_id`
6. Data returned and populated into tables
7. Charts update automatically

---

## 📁 Project Structure

```
project/
│
├── backend/
│   ├── server.py
│   ├── signals/
│   ├── registry.py
│   └── device.py
│
├── excel_ui/
│   ├── ui.xlsx
│   └── vba_modules/
│
├── web_ui/ (optional)
│   ├── index.html
│   ├── main.js
│   └── styles.css
│
└── README.md
```

---

## 🧪 Technologies Used

* **Hardware:** ADALM1000 (M1K)
* **Backend:** Python, PySMU, NumPy, SciPy
* **UI (Primary):** Microsoft Excel + VBA
* **UI (Optional):** Univer Sheets (Web)
* **Communication:** HTTP API / structured data exchange

---

## 🎯 Goals

* Build a **structured experimental platform** for signals and systems
* Enable **intuitive, spreadsheet-driven experiments**
* Ensure **clean separation of UI and computation**
* Provide **extensible architecture** for multiple interfaces

---

## 📌 Notes

* This is not just a UI project — it is a **signal processing system with a spreadsheet interface**
* The backend is designed to be **UI-independent**
* The system can be extended to support:

  * More signal types
  * Real-time streaming
  * Additional frontends

---

## 🤝 Contributions

This project is being developed as a collaborative effort with roles such as:

* Backend (Python & signal processing)
* Excel UI (VBA & layout)
* Web UI (Univer / JavaScript)

---

## 📜 License

Open for academic and educational use.

---

## 💡 Summary

This project turns a spreadsheet into a **lab instrument interface**, backed by a structured signal-processing engine — combining usability with solid engineering design.

---
