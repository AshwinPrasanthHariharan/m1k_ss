# M1K SMU Project - Contribution Summary (Ashwin Prasanth Hariharan)

This README is written for evaluation. Everything listed below is part of my project contribution for ADALM1000 (M1K) control, measurement, and calibration workflow.

## My Contributions by File

### Core implementation
- [m1k_utils/utils.py](m1k_utils/utils.py): Main SMU abstraction (`SMU`, `Device`, `Channel`) with session lifecycle control, robust write/read helpers, and retry logic.
- [m1k_utils/__init__.py](m1k_utils/__init__.py): Package export surface for utility imports.
- [m1k_utils/pyproject.toml](m1k_utils/pyproject.toml): Python package metadata for `m1k_utils`.

### Interactive experiment and calibration workflow
- [smu_control.ipynb](smu_control.ipynb): End-to-end interactive notebook covering device setup, channel mode setup, write/read validation, calibration sweep, model fitting, and plotting.

### Calibration assets
- [m1k.cal](m1k.cal): Calibration mapping file used for M1K calibration workflow.
- [template.cal](template.cal): Calibration command/help template used as reference.

### Environment and reproducibility setup
- [pixi.toml](pixi.toml): Environment definition with dependency specification.
- [pixi.lock](pixi.lock): Locked dependency graph for reproducible setup.
- [.vscode/settings.json](.vscode/settings.json): VS Code interpreter configuration for the project environment.

### Reference and validation scripts
- [examples/get_samples.py](examples/get_samples.py): Fixed-size multi-device sample capture reference.
- [examples/hotplug.py](examples/hotplug.py): Device attach/detach monitoring reference.
- [examples/leds.py](examples/leds.py): LED control behavior reference.
- [examples/multi-cyclic-run.py](examples/multi-cyclic-run.py): Cyclic write/run reference.
- [examples/plot-voltage.py](examples/plot-voltage.py): Signal generation and plotting reference.
- [examples/read-continuous.py](examples/read-continuous.py): Continuous read streaming reference.
- [examples/read-write-continuous.py](examples/read-write-continuous.py): Continuous read/write loop reference.
- [examples/read-write.py](examples/read-write.py): Noncontinuous read/write loop reference.
- [examples/read.py](examples/read.py): Noncontinuous read reference.

## Instructions for Evaluator (GitHub-Only Review)

This evaluation can be completed directly in GitHub by reading code and notebook outputs.
No local setup or execution is required for primary assessment.

### 1) Environment and reproducibility evidence (code review only)
1. Review [.vscode/settings.json](.vscode/settings.json) for interpreter configuration.
2. Review [pixi.toml](pixi.toml) for declared dependencies.
3. Review [pixi.lock](pixi.lock) for locked, reproducible dependency resolution.

### 2) Code structure validation
1. Open [m1k_utils/utils.py](m1k_utils/utils.py) and review the three main classes:
  - `Channel` for DC write/read operations
  - `Device` for per-device wrappers
  - `SMU` for session lifecycle and scan/start/stop flow
2. Confirm package export path in [m1k_utils/__init__.py](m1k_utils/__init__.py).

### 3) Functional workflow validation from notebook content/output
1. Open [smu_control.ipynb](smu_control.ipynb) in GitHub.
2. Verify the workflow order by reading cells and rendered outputs:
  - Session/device initialization
  - Channel mode selection
  - Write/read sanity check
  - Write-vs-read calibration sweep
  - Linear fit values and calibration plots
3. Use Markdown sections in the notebook as guidance for the intended flow.

### 4) Calibration artifact validation
1. Inspect [m1k.cal](m1k.cal) for channel calibration entries.
2. Inspect [template.cal](template.cal) for calibration CLI command reference.

### 5) Reference script validation
1. Review scripts under [examples](examples/) to confirm coverage of read, write, continuous streaming, cyclic operation, plotting, and hotplug handling.

## Evaluation Notes

- This workspace is organized so the notebook demonstrates practical behavior while the utility package provides reusable implementation.
- Generated directories such as [.pixi](.pixi/) and [m1k_utils/m1k_utils.egg-info](m1k_utils/m1k_utils.egg-info/) may appear depending on local environment setup.
- For GitHub-space evaluation, prioritize file-level logic in [m1k_utils/utils.py](m1k_utils/utils.py) and rendered results in [smu_control.ipynb](smu_control.ipynb).
