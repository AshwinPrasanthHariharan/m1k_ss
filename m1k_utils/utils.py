"""Simple calibration manager for ADALM1000-style calibration files.

This module provides a lightweight `CalibrationManager` that either loads an
existing calibration file (preserving block order) or initialises a default
ordered dictionary of calibration blocks. It can convert the in-memory
dictionary to the ADALM1000 calibration file text format and save it.
"""

from __future__ import annotations

from collections import OrderedDict
from pathlib import Path
from typing import Iterable, List, OrderedDict as _OD, Sequence, Tuple, Union
from pysmu import *

CalibrationPoint = Tuple[float, float]


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
def get(session: Session,serial:str)->SessionDevice:
    for dev in session.devices:
        if dev.serial == serial:
            return dev
    else:
        for dev in session.available_devices:
            if dev.serial == serial:
                session.add_device(dev)
                return get(session,serial)
    raise ValueError(f"No device with serial {serial} found in session")