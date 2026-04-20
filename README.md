# 📊 Frequency Response Analysis, System Identification & VI Characterization using ADALM M1K

## 🚀 Overview

This project develops a **Python-based experimental framework** for analyzing and identifying electrical systems using the **ADALM1000 (M1K)**.

The system goes beyond basic measurement and focuses on **extracting system behavior from signals**, using core **frequency-domain techniques** from Signals and Systems.

It enables:

* **Frequency response analysis (magnitude & phase)**
* **Voltage-Current (VI) characterization**
* **DC gain analysis**
* **FFT-based spectral analysis**
* **Transfer function estimation**
* **System identification and validation**

The objective is to build a **structured, automated, and reproducible platform** that bridges theoretical concepts with real experimental data .

---

## 🎯 Key Idea

> Instead of only measuring signals, the system **derives the underlying system behavior** using frequency-domain analysis and validates it experimentally.

---

## 🎯 Objectives

* Determine **frequency response** of systems:

  * RC, RL, and RLC circuits

* Analyze **VI characteristics** of:

  * Linear components (resistors)
  * Non-linear components (diodes)

* Perform **FFT-based spectral analysis** of signals

* Estimate **transfer function**:
  $$
  H(f) = \frac{Y(f)}{X(f)}
  $$

* Identify system properties:

  * Cutoff frequency
  * Resonance behavior
  * Gain characteristics

* Validate results using:

  * Theoretical models
  * Broadband excitation (square wave harmonic analysis)

* Study real-world limitations:

  * Noise
  * Sampling constraints
  * Hardware non-idealities

---

## ⚙️ System Architecture

```id="3fh9dl"
ADALM1000 (M1K)
        │
        ▼
Data Acquisition (PySMU)
        │
        ▼
DSP Analysis Layer
│
├─ FFT (spectral analysis)
├─ Transfer Function Estimation
├─ System Identification
│
▼
Visualization Layer (Streamlit)
│
├─ Time-domain plots
├─ Frequency-domain plots
├─ VI curves
```

---

## 🧩 Modular Design

The system is divided into three main modules:

### 1. Data Acquisition

* Interface with ADALM1000 using **PySMU**
* Generate signals:

  * Sinusoidal inputs (for sweep analysis)
  * Ramp/DC signals (for VI characterization)
  * Square waves (for broadband validation)
* Capture:

  * Input voltage
  * Output voltage
  * Current

---

### 2. DSP Analysis

Core signal processing and system analysis:

* **FFT Analysis**

  * Extract spectral components of signals
  * Analyze frequency content

* **Transfer Function Estimation**

  * Compute:
    $$
    H(f) = \frac{Y(f)}{X(f)}
    $$
  * Directly characterize system behavior from measured data

* **System Identification**

  * Estimate:

    * Cutoff frequency
    * Resonance peaks
    * Gain characteristics
  * Validate against theoretical models

* **Broadband Validation**

  * Apply square wave input
  * Analyze harmonic attenuation
  * Verify system response via spectral decomposition

---

### 3. Visualization Layer

* Interactive UI built using **Streamlit**

* Features:

  * Parameter selection (frequency range, sweep resolution)
  * Experiment control
  * Real-time visualization:

    * Time-domain signals
    * FFT magnitude plots
    * Bode magnitude & phase plots
    * VI characteristic curves

* Enables intuitive experimentation without modifying code

---

## 🧪 Methodology

### 1. System Setup

* Use **PySMU** to interface with M1K
* Manage environment using **Pixi**
* Use:

  * NumPy (processing)
  * Matplotlib (plotting)
  * Streamlit (UI)

---

### 2. Circuit Implementation

* Construct:

  * RC, RL, RLC circuits
* Include:

  * Linear components
  * Non-linear components

---

### 3. Automated Measurement

* Perform:

  * Frequency sweeps
  * VI sweeps
* Record input/output signals at each step

---

### 4. Data Processing

* Compute:

  * Gain and phase
  * FFT spectra
  * Transfer function

* Apply:

  * Averaging
  * Noise reduction

---

### 5. Validation

* Compare experimental results with:

  * Analytical models
  * Expected cutoff/resonance behavior

* Validate using:

  * Square wave harmonic analysis

---

### 6. Error Analysis

* Evaluate:

  * Hardware noise (M1K limitations)
  * Sampling rate constraints
  * Breadboard parasitics

---

## 📁 Project Structure (Expected)

```id="g3f3z8"
project/
│
├── src/
│   ├── acquisition/
│   ├── dsp/
│   ├── system_id/
│
├── ui/
│   └── streamlit_app.py
│
├── data/
│   └── experiments/
│
├── configs/
│   └── pixi.toml
│
└── README.md
```

---

## 🧰 Technologies Used

* **Hardware:** ADALM1000 (M1K)
* **Backend:** Python, PySMU
* **Processing:** NumPy
* **Visualization:** Matplotlib
* **UI:** Streamlit
* **Environment:** Pixi

---

## 📌 Summary

This project builds a **complete experimental system** for:

* Signal acquisition
* Frequency-domain analysis
* System identification
* Experimental validation

It emphasizes applying **core Signals and Systems concepts** such as:

* Frequency-domain representation
* Transfer functions
* System modeling

while validating them using **real-world experimental data**.

---

