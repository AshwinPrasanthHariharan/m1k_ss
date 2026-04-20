# M1K SMU Project - Contribution Summary (Shendhan)

## My Contributions by Area

<img width="1536" height="1024" alt="ui_plan" src="https://github.com/user-attachments/assets/5ec2502e-35a1-4f15-87eb-3358a00127e6" />


### System Architecture & Design

* Designed the **overall system architecture** separating:

  * Excel (UI + orchestration)
  * Python backend (hardware + signal processing)
* Defined a **UI-agnostic backend model** allowing both Excel and web UI (Univer) to use the same system
* Established **clear separation of concerns**:

  * UI → input + orchestration
  * Backend → computation + hardware control

---

### Signal Abstraction & Workflow Design

* Designed a **Signal abstraction model** with:

  * Unique `signal_id` for every dataset
  * Structured signal lifecycle (acquire → process → store)
* Defined signal types:

  * Time-domain signal
  * FFT signal (derived)
  * Sweep signal (frequency response)
* Proposed a **Signal Registry system**:

  * Maps `signal_id → signal object`
  * Enables reproducibility and traceability

---

### UI Design & Workflow Planning

* Designed a **spreadsheet-driven UI layout**:

  * Cells = parameters (sample rate, waveform, sweep settings)
  * Buttons = actions (Acquire, FFT, Sweep)
  * Tables = data (Raw, FFT, Sweep)
  * Charts = visualization (time-domain and frequency-domain)
* Created initial **UI mockup and layout structure**
* Explored UI approaches:

  * Excel-based UI (finalized primary)
  * Web-based UI using Univer Sheets (optional extension)
* Documented UI decisions under `docs/ui_design.png`

---

### Excel UI & VBA Orchestration Planning

* Defined Excel structure:

  * Input sections (acquisition, waveform, sweep)
  * Action panel
  * Data tables
  * Status panel
* Designed VBA responsibilities:

  * Read parameters from cells
  * Send commands to backend
  * Populate tables with returned data
  * Update charts and status
* Ensured **no computation occurs inside Excel**

---

### Backend API & Communication Design

* Defined a **signal-centric API structure**:

  * `/signal/acquire`
  * `/signal/fft`
  * `/signal/sweep`
  * `/signal/{id}`
  * `/device/blink`
* Designed communication workflow:

  * Excel (VBA) → HTTP request → Python backend → response → Excel tables
* Ensured backend is **fully reusable across multiple UIs**

---

### Experimental Workflow Design

* Structured the complete workflow:

  * Finite sample acquisition (voltage & current)
  * FFT magnitude analysis
  * Frequency response via sine sweep
  * VI (Voltage-Current) characterization
* Defined **deterministic, block-based experiments** (no hidden state)

---

### Documentation & Proposal

* Prepared:

  * **Project proposal** (Problem, Objectives, Methodology)
  * **System workflow documentation**
  * **README structure for repository**
* Defined project as:

  > A lab-style measurement system implemented through a spreadsheet interface with a structured backend

---

## Instructions for Evaluator (GitHub-Only Review)

This evaluation can be completed directly through GitHub without running the system.

---

### 1) Architecture & Design Review

* Review README and documentation files
* Confirm:

  * Separation between UI and backend
  * Signal-based system design using `signal_id`
  * Multi-frontend capability (Excel + optional web UI)

---

### 2) UI Design Validation

* Open `docs/ui_design.png`
* Verify:

  * Spreadsheet-driven layout
  * Clear separation of control, data, and visualization
  * Alignment with signals and systems workflow

---

### 3) Workflow & Logic Review

* Review documentation for:

  * Acquisition → FFT → Sweep pipeline
  * Signal lifecycle definition
  * Backend-driven computation model

---

### 4) Project Structure Validation

* Check repository structure:

  * `backend/` → core logic and signal handling
  * `excel_ui/` → spreadsheet interface and VBA
  * `web_ui/` → optional Univer-based UI
  * `docs/` → UI design and planning

---

## Evaluation Notes

* This contribution focuses on **system-level design, architecture, and workflow integration**
* Emphasis is placed on:

  * Clean separation of components
  * Reproducibility using signal IDs
  * Extensibility via multiple UIs
* The project is structured to evolve from:

  * Spreadsheet-based interface → full instrumentation system

---

## Summary

This work contributes the **foundation and design of a structured signal acquisition system**, ensuring:

* Clear workflows
* Scalable architecture
* Reusable backend
* Intuitive spreadsheet-based interaction

The system bridges the gap between:

> **Educational tools (spreadsheets)** and **real measurement systems (instrumentation software)**

---
