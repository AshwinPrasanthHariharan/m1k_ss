# smu.py

from collections import OrderedDict
from typing import List, Tuple, Union, Iterable, OrderedDict as _OD, NamedTuple
import time
from pathlib import Path
from pysmu import Session, Mode ,Signal 
sig=Signal()
import numpy as np
import subprocess
class CalibrationPoint(NamedTuple):
    """A simple calibration point: (input, output)"""
    left: float
    right: float

def measure_gain_phase_at_freqs(s,dev, p,amp):
    sine_wave = sig.sine(samples=10*p, midpoint=amp[0], peak=amp[1], period=p, phase=0)
    dev.channels["A"].write(sine_wave,-1)
    time.sleep(1)  # Allow some time for the signal to stabilize
    s.start(10*p+100)
    time.sleep(1)  # Allow some time for the measurement to complete
    data = dev.read(100)
    data = dev.read(10*p)
    list1, list3 = [], []
    for item in data:
        if isinstance(item, tuple):
            (a, b), (c, d) = item
            list1.append(a)
            list3.append(c)
    print(f"Measured {len(list1)} samples for period {p}")
    result = (list1, list3)
    return result
def _serials_match(expected: str, current: str) -> bool:
    expected = str(expected).strip().strip('\x00')
    current = str(current).strip().strip('\x00')

    if expected == current:
        return True

    if not expected or not current:
        return False

    if abs(len(expected) - len(current)) > 1:
        return False

    if len(expected) == len(current):
        differences = sum(left != right for left, right in zip(expected, current))
        return differences <= 1

    if len(expected) > len(current):
        expected, current = current, expected

    left_index = 0
    right_index = 0
    differences = 0

    while left_index < len(expected) and right_index < len(current):
        if expected[left_index] == current[right_index]:
            left_index += 1
            right_index += 1
            continue

        differences += 1
        if differences > 1:
            return False
        right_index += 1

    return True


def reconnect(serial_number):
    sysfs_usb = Path('/sys/bus/usb/devices/')
    
    for device_path in sysfs_usb.iterdir():
        serial_file = device_path / 'serial'
        
        if serial_file.exists():
            try:
                # Strip standard whitespace AND null bytes
                current_serial = serial_file.read_text().strip().strip('\x00')
                
                if _serials_match(serial_number, current_serial):
                    authorized_file = device_path / 'authorized'
                    print(f"Match found at {device_path.name}.")
                    
                    try:
                        print("Simulating unplug...")
                        authorized_file.write_text('0\n')
                        time.sleep(0.2) 
                        
                        print("Simulating replug...")
                        authorized_file.write_text('1\n')
                        
                        print("Reconnect successful.")
                        return True
                    except PermissionError:
                        print(f"Error: You need udev rules to grant write access to {authorized_file}")
                        return False
                        
            except PermissionError:
                # If we can't even READ the serial file, let the user know instead of silently failing
                print(f"Warning: Permission denied reading serial for {device_path.name}")
            except Exception as e:
                print(f"Warning: Unexpected error reading {device_path.name}: {e}")
                
    print(f"Error: Could not find a USB device with serial '{serial_number}'.")
    return False

def reconnect_all(product_title="ADALM1000"):
    """Reconnect all USB devices matching the specified product title."""
    sysfs_usb = Path('/sys/bus/usb/devices/')
    reconnected_count = 0
    failed_count = 0
    
    print(f"Scanning for devices matching product '{product_title}'...")
    
    for device_path in sysfs_usb.iterdir():
        product_file = device_path / 'product'
        authorized_file = device_path / 'authorized'
        
        if product_file.exists() and authorized_file.exists():
            try:
                product_name = product_file.read_text().strip().strip('\x00')
                
                if product_title in product_name:
                    serial_file = device_path / 'serial'
                    serial = "unknown"
                    
                    if serial_file.exists():
                        try:
                            serial = serial_file.read_text().strip().strip('\x00')
                        except Exception:
                            pass
                    
                    print(f"\nFound: {product_name} (Serial: {serial}) at {device_path.name}")
                    
                    try:
                        print("  Simulating unplug...")
                        authorized_file.write_text('0\n')
                        time.sleep(0.2)
                        
                        print("  Simulating replug...")
                        authorized_file.write_text('1\n')
                        time.sleep(0.1)
                        
                        print("  Reconnect successful.")
                        reconnected_count += 1
                    except PermissionError:
                        print(f"  Error: Permission denied. You need udev rules to grant write access.")
                        failed_count += 1
                    except Exception as e:
                        print(f"  Error reconnecting: {e}")
                        failed_count += 1
                        
            except PermissionError:
                pass  # Skip devices we can't read
            except Exception as e:
                pass  # Skip devices with errors
    
    print(f"\n--- Reconnect All Summary ---")
    print(f"Successfully reconnected: {reconnected_count}")
    print(f"Failed: {failed_count}")
    
    if reconnected_count == 0:
        print(f"No devices matching '{product_title}' found.")
        return False
    
    return reconnected_count > 0

class CalibrationManager:
    """Manage calibration blocks stored in a simple ordered dict view.

    Usage:
      mgr = CalibrationManager("m1k.cal")
      mgr.recab("measure v", "a", [(0.0, 0.0), (2.5, 2.5)])
      mgr.save()
"""

    DEFAULT_KEYS = [
        "Channel A, measure V",
        "Channel A, measure I",
        "Channel A, source V",
        "Channel A, source I",
        "Channel B, measure V",
        "Channel B, measure I",
        "Channel B, source V",
        "Channel B, source I",
    ]

    # sensible default templates used when initializing or resetting blocks
    DEFAULT_TEMPLATES = {
        "v": [(0.0, 0.0), (2.5, 2.5)],
        "i": [(0.0, 0.0), (0.1, 0.1), (-0.1, -0.1)],
    }

    def __init__(self, path: Union[str, Path]):
        self.path = Path(path)
        self.header: List[str] = ["# ADALM1000 calibration file"]
        self.blocks: OrderedDict[str, List[CalibrationPoint]] = OrderedDict()

        if not self.path.exists() or self.path.stat().st_size == 0:
            # empty or missing file — create default ordered blocks using templates
            for k in self.DEFAULT_KEYS:
                kind = "v" if "v" in k.lower() else ("i" if "i" in k.lower() else "v")
                self.blocks[k] = [tuple(x) for x in self.DEFAULT_TEMPLATES.get(kind, [])]
        else:
            text = self.path.read_text(encoding="utf-8")
            parsed = self._parse_text(text)
            if parsed:
                self.blocks = parsed
            else:
                self.blocks = OrderedDict((k, []) for k in self.DEFAULT_KEYS)

    def _parse_text(self, text: str) -> OrderedDict[str, List[CalibrationPoint]]:
        blocks: OrderedDict[str, List[CalibrationPoint]] = OrderedDict()
        current_title: str | None = None
        current_points: List[CalibrationPoint] = []

        def flush_block() -> None:
            nonlocal current_title, current_points
            if current_title is not None:
                blocks[current_title] = list(current_points)
            current_title = None
            current_points = []

        for raw in text.splitlines():
            line = raw.strip()
            if not line:
                continue
            if line == "# ADALM1000 calibration file" and current_title is None and not blocks:
                # file banner, not a calibration block title
                continue
            if line.startswith("#"):
                # start a new block (flush previous if present)
                flush_block()
                current_title = line[1:].strip()
                current_points = []
                continue
            if line == "</>":
                continue
            if line == "<\\>":
                flush_block()
                continue
            # expect a point like <0.0000, 0.0000>
            if line.startswith("<") and line.endswith(">"):
                inner = line[1:-1].strip()
                if "," in inner:
                    left, right = [p.strip() for p in inner.split(",", 1)]
                    try:
                        current_points.append((float(left), float(right)))
                    except ValueError:
                        # skip malformed numeric lines
                        continue
                continue
            # ignore unknown lines

        # flush at EOF
        flush_block()

        return blocks

    def as_ordered_dict(self) -> _OD[str, List[CalibrationPoint]]:
        return OrderedDict((title, list(pts)) for title, pts in self.blocks.items())

    def to_text(self) -> str:
        parts: List[str] = []
        if self.header:
            parts.extend(self.header)
            parts.append("")

        for title, points in self.blocks.items():
            parts.append(f"# {title}")
            parts.append("</>")
            for p in points:
                parts.append("<{:.4f}, {:.4f}>".format(float(p[0]), float(p[1])))
            parts.append("<\\>")
            parts.append("")

        return "\n".join(parts).rstrip() + "\n"

    def save(self, path: Union[str, Path] | None = None) -> None:
        target = Path(path) if path is not None else self.path
        target.write_text(self.to_text(), encoding="utf-8")

    def recab(self, measure: str, channel: str, levels: Iterable[Iterable[float]]) -> None:
        """Replace a block's points.

        `measure` should include the distinguishing text such as "measure V",
        "measure I", "source V" or "source I" (case-insensitive). `channel`
        should be 'a' or 'b'. `levels` is an iterable of (vin, vout) pairs.
        """

        key_channel = "Channel A" if str(channel).strip().lower() == "a" else "Channel B"
        selector = str(measure).strip().lower()

        # find candidate blocks that match both channel and selector
        candidates = [title for title in self.blocks.keys() if key_channel.lower() in title.lower() and selector in title.lower()]

        if not candidates:
            raise KeyError(f"no calibration block matches channel={channel!r} measure={measure!r}")
        if len(candidates) > 1:
            raise ValueError(f"ambiguous selector; multiple blocks match channel={channel!r} measure={measure!r}")

        title = candidates[0]
        self.blocks[title] = [(float(v[0]), float(v[1])) for v in levels]

    def get(self, measure: str, channel: str) -> List[CalibrationPoint]:
        key_channel = "Channel A" if str(channel).strip().lower() == "a" else "Channel B"
        selector = str(measure).strip().lower()
        for title, pts in self.blocks.items():
            if key_channel.lower() in title.lower() and selector in title.lower():
                return list(pts)
        raise KeyError(f"no calibration block matches channel={channel!r} measure={measure!r}")

    def reset_block(self, arg1: str, arg2: str | None = None, points: Iterable[Iterable[float]] | None = None) -> None:
        """Reset a single calibration block.

        Accepts either `(measure, channel)` or `(channel, measure)` order. If
        `points` is None the block is populated with a sensible default
        template: voltage blocks get `[(0,0),(2.5,2.5)]`, current blocks get
        `[(0,0),(0.1,0.1),(-0.1,-0.1)]`.
        """

        if arg2 is None:
            raise TypeError("reset_block requires two positional arguments: channel and measure (either order)")

        a = str(arg1).strip().lower()
        b = str(arg2).strip().lower()

        # determine which argument is the channel ('a' or 'b')
        if a in ("a", "b") and not (b in ("a", "b")):
            channel = a
            selector = b
        elif b in ("a", "b") and not (a in ("a", "b")):
            channel = b
            selector = a
        else:
            # ambiguous or invalid ordering
            raise ValueError("cannot determine channel/measure from arguments; provide one channel ('a' or 'b') and one selector like 'measure v'")

        key_channel = "Channel A" if channel == "a" else "Channel B"
        sel = selector.lower()

        candidates = [title for title in self.blocks.keys() if key_channel.lower() in title.lower() and sel in title.lower()]
        if not candidates:
            raise KeyError(f"no calibration block matches channel={channel!r} selector={selector!r}")
        if len(candidates) > 1:
            raise ValueError(f"ambiguous selector; multiple blocks match channel={channel!r} selector={selector!r}")

        title = candidates[0]
        if points is None:
            # choose template based on selector (voltage/current)
            if "v" in sel or "voltage" in sel:
                new_pts = [tuple(x) for x in self.DEFAULT_TEMPLATES["v"]]
            elif "i" in sel or "current" in sel:
                new_pts = [tuple(x) for x in self.DEFAULT_TEMPLATES["i"]]
            else:
                new_pts = []
        else:
            new_pts = [(float(p[0]), float(p[1])) for p in points]

        self.blocks[title] = new_pts

    def reset_all(self) -> None:
        """Reset all blocks to their default templates."""
        for title in self.blocks.keys():
            if "measure v" in title.lower() or "source v" in title.lower():
                self.blocks[title] = [tuple(x) for x in self.DEFAULT_TEMPLATES["v"]]
            elif "measure i" in title.lower() or "source i" in title.lower():
                self.blocks[title] = [tuple(x) for x in self.DEFAULT_TEMPLATES["i"]]
            else:
                # preserve unknown block titles but clear values if they don't match a known template
                self.blocks[title] = []
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
        self._ch.constant(v)
    # ---------- INPUT ----------
    def dcr(self,i=100,mes="V"):
        """Read DC voltage"""
        self.dev.flush(-1,True)
        time.sleep(0.05)
        l,k=zip(*self._ch.read(i))
        return  np.average(l) if mes=="V" else np.average(k)
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
        

    def pulse_in_out(self,ps,amp=(0,5),t=None,in_ch="A",out_ch="B"):
        try:
            self.ctrl.session.cancel()
        except Exception as e:
            print(f"Warning: Could not cancel session before pulse_in_out: {e}")
        try:
            self._dev.channels[out_ch].mode = Mode.HI_Z
            self._dev.channels[in_ch].mode = Mode.SVMI
        except Exception as e:
            print(f"Error occurred while setting channel modes: {e}")
        self._dev.flush(-1,True)
        time.sleep(0.05)
        res=measure_gain_phase_at_freqs(self.ctrl.session,self._dev, ps,amp)
        return res

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
        self._cleanup_session()
    def _cleanup_session(self):
        try:
            self.session = Session()
        except:
            if self.session:
                self.session._close()
            self.reconnect_all()
            self.session = Session()
            self.session.add_all()

    @property
    def devices(self):
        return [Device(dev, self) for dev in self.session.devices]
    # ---------- CORE ----------
    def scan(self):
        self.session.scan()
    def start(self,i=0):
        self.session.start(i)
        self.running = True
        print("[SMU] Session started")
    def reconnect(self,serial):
        reconnect(serial)
    def reconnect_all(self):
        reconnect_all("ADALM1000")
    # ---------- HELPERS ----------
    def list(self):
        return [d.serial for d in self.devices]

    def get(self, serial):
        for d in self.session.devices:
            if d.serial == serial:
                return d
        raise ValueError("Device not found")

    # ---------- PRINT ----------
    def __str__(self):
        out = ["SMU:"]
        for i, d in enumerate(self.devices):
            out.append(f"  [{i}] {d}")
        return "\n".join(out)