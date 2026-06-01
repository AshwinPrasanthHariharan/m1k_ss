# smu.py

import signal
import sys
import atexit
import time
from pysmu import Session, Mode
import gc
import numpy as np
# =========================
# Channel Wrapper
# =========================
class Channel:
    def __init__(self, ch_name, ctrl,dev_serial):
        self._ch_name = ch_name
        self.ctrl = ctrl
        self.dev_serial = dev_serial

    # ---------- OUTPUT ----------
    @property
    def dev(self):
        return self.ctrl.get(self.dev_serial)
    @property
    def _ch(self):
        return self.ctrl.get(self.dev_serial).channels[self._ch_name]
    def dc(self, v):
        """Set DC voltage"""
        if not self._ch.mode == Mode.SVMI:
            self._ch.mode = Mode.SVMI
        self.dev.flush(-1,True)
        self._ch.constant(v)
    # ---------- INPUT ----------
    def dcr(self,i=100):
        """Read DC voltage"""
        self.dev.flush(-1,True)
        samples = []
        for _ in range(3):
            time.sleep(0.02)
            samples = self._ch.read(i)
            if samples:
                break
        if not samples:
            return 0.0

        values = []
        for sample in samples:
            try:
                value = float(sample[0])
            except (TypeError, ValueError, IndexError):
                continue
            if np.isfinite(value):
                values.append(value)

        return float(np.mean(values)) if values else 0.0
    def __str__(self):
        return f"Channel(mode={self._ch.mode})"
# =========================
# Device Wrapper
# =========================
class Device:
    def __init__(self, dev, ctrl):
        self.ctrl = ctrl

        self.serial = dev.serial
        self.fw = dev.fwver
        self.hw = dev.hwver

        self.ch_a = Channel("A", ctrl,dev.serial)
        self.ch_b = Channel("B", ctrl,dev.serial)
    @property
    def _dev(self):
        return self.ctrl.get(self.serial)
    def led(self, val):
        self._dev.set_led(val)

    def __str__(self):
        return f"Device {self.serial} | FW:{self.fw} HW:{self.hw}"


# =========================
# SMU Manager
# =========================
class SMU:
    def __init__(self):
        
        self.session = None
        self.running = False

        # -------- STEP 1: kill stale sessions --------
        self._cleanup_sessions()

        # -------- STEP 2: try init --------
        try:
            self.session = Session()

        except Exception:
            print("[SMU] Device busy → retrying after cleanup...")

            # second cleanup (just in case)
            self._cleanup_sessions()

            # retry once
            try:
                self.session = Session()
            except Exception as e:
                raise RuntimeError(
                    "SMU init failed even after cleanup.\n"
                    "Try restarting kernel or unplugging device."
                ) from e

        # -------- STEP 3: scan devices --------
        self.scan()

        # cleanup hooks
        signal.signal(signal.SIGINT, self._handle_exit)
        signal.signal(signal.SIGTERM, self._handle_exit)
        atexit.register(self.stop)
    @property
    def devices(self):
        return [Device(dev, self) for dev in self.session.devices]
    # ---------- CORE ----------
    def scan(self):
        try:
            self.session.flush()
        except:
            pass

        self.session = Session()
    def start(self,i=0):
        if not self.running:
            self.session.start(i)
            self.running = True
            print("[SMU] Session started")

    def stop(self):
        if self.running:
            try:
                self.session.end()
            except:
                pass
            self.running = False
            print("[SMU] Session stopped")

    # ---------- REFRESH ----------
    def _cleanup_sessions(self):
        killed = 0

        for obj in gc.get_objects():
            try:
                if obj.__class__.__name__ == "pysmu.libsmu.Session":
                    obj._close()
                    killed += 1
            except:
                print("[SMU] Warning: Failed to close a session object during cleanup")

        if killed:
            print(f"[SMU] Cleaned {killed} stale session(s)")

        gc.collect()
        time.sleep(0.3)
    def refresh(self):
        """Hard reset session"""
        print("[SMU] Refreshing...")

        self.stop()

        try:
            del self.session
        except:
            pass

        time.sleep(0.5)

        self.session = Session()
        self.scan()

    def safe_start(self):
        """Start with auto-recovery"""
        try:
            self.start()
        except Exception as e:
            print("[SMU] Start failed → retrying with refresh")
            self.refresh()
            self.start()

    # ---------- HELPERS ----------
    def list(self):
        return [d.serial for d in self.devices]

    def get(self, serial):
        for d in self.session.devices:
            if d.serial == serial:
                return d
        raise ValueError("Device not found")

    # ---------- CONTEXT ----------
    def __enter__(self):
        self.safe_start()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.stop()

    # ---------- SIGNAL ----------
    def _handle_exit(self, signum):
        print(f"\n[SMU] Signal {signum} received")
        self.stop()
        sys.exit(0)

    # ---------- PRINT ----------
    def __str__(self):
        out = ["SMU:"]
        for i, d in enumerate(self.devices):
            out.append(f"  [{i}] {d}")
        return "\n".join(out)