"""
PassNook — System tray icon
Hides the window to tray on close; double-click / menu to restore.
"""

from __future__ import annotations
import sys
import threading
from pathlib import Path
from typing import Callable

import pystray
from PIL import Image


def _res(rel: str) -> Path:
    base = getattr(sys, "_MEIPASS", Path(__file__).parent.parent)
    return Path(base) / rel


class TrayIcon:
    def __init__(self, on_show: Callable, on_quit: Callable):
        self._on_show = on_show
        self._on_quit = on_quit
        self._icon: pystray.Icon | None = None

    def start(self):
        logo_path = _res("assets/logo.png")
        img = Image.open(str(logo_path)) if logo_path.exists() \
            else Image.new("RGB", (64, 64), color=(124, 58, 237))

        menu = pystray.Menu(
            pystray.MenuItem("Show PassNook", self._show, default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self._quit),
        )
        self._icon = pystray.Icon("PassNook", img, "PassNook", menu)
        thread = threading.Thread(target=self._icon.run, daemon=True)
        thread.start()

    def stop(self):
        if self._icon:
            try:
                self._icon.stop()
            except Exception:
                pass

    def _show(self, *_):
        self._on_show()

    def _quit(self, *_):
        self.stop()
        self._on_quit()
