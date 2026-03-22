"""
PassNook — Secure Password Manager
Entry point
"""

import sys
import ctypes
from pathlib import Path

import customtkinter as ctk

from make_assets import ensure_assets
from core.vault import VaultManager
from ui.lock_frame import LockFrame
from ui.main_frame import MainFrame
from ui.tray import TrayIcon
from ui.styles import BG, SURFACE, BORDER

# Auto-lock: 30 minutes of system idle locks the vault
AUTO_LOCK_SECONDS = 30 * 60


def _idle_seconds() -> float:
    """Return Windows system idle time in seconds."""
    class _LASTINPUTINFO(ctypes.Structure):
        _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]
    lii = _LASTINPUTINFO()
    lii.cbSize = ctypes.sizeof(lii)
    ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii))
    return (ctypes.windll.kernel32.GetTickCount() - lii.dwTime) / 1000.0


class PassNookApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self._vault  = VaultManager()
        self._frame  = None
        self._tray: TrayIcon | None = None

        # Window chrome
        self.title("PassNook")
        self.configure(fg_color=BG)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Icon
        icon_path = Path(__file__).parent / "assets" / "icon.ico"
        if icon_path.exists():
            try:
                self.iconbitmap(str(icon_path))
            except Exception:
                pass

        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Start tray icon immediately so it's always visible
        self._tray = TrayIcon(
            on_show=lambda: self.after(0, self._restore),
            on_quit=lambda: self.after(0, self._quit),
        )
        self._tray.start()

        self._show_lock()
        self._poll_idle()

    # ── Frame switching ───────────────────────────────────────────────────────

    def _show_lock(self):
        self._swap_frame(None)
        self.geometry("460x560")
        self.resizable(False, False)
        self._center(460, 560)
        self._frame = LockFrame(self, self._vault, on_unlock=self._show_main)
        self._frame.grid(row=0, column=0, sticky="nsew")

    def _show_main(self):
        self._swap_frame(None)
        self.geometry("980x660")
        self.resizable(True, True)
        self.minsize(820, 560)
        self._center(980, 660)
        self._frame = MainFrame(self, self._vault, on_lock=self._lock)
        self._frame.grid(row=0, column=0, sticky="nsew")

    def _lock(self):
        self._vault.lock()
        self._show_lock()

    def _swap_frame(self, new):
        if self._frame:
            self._frame.destroy()
            self._frame = None

    # ── Idle auto-lock ────────────────────────────────────────────────────────

    def _poll_idle(self):
        if self._vault.is_unlocked:
            try:
                if _idle_seconds() >= AUTO_LOCK_SECONDS:
                    self._lock()
                    return
            except Exception:
                pass
        self.after(60_000, self._poll_idle)   # check every 60 s

    # ── Tray ──────────────────────────────────────────────────────────────────

    def _on_close(self):
        self.withdraw()

    def _restore(self):
        self.deiconify()
        self.lift()
        self.focus_force()

    def _quit(self):
        if self._tray:
            self._tray.stop()
        self.destroy()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _center(self, w: int, h: int):
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")


def main():
    ensure_assets()
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = PassNookApp()
    app.mainloop()


if __name__ == "__main__":
    main()
