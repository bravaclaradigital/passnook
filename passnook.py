"""
PassNook — Secure Password Manager
Entry point
"""

import sys
import ctypes
from pathlib import Path

# ── Monkey-patch tkinter.Misc BEFORE any widget is created ───────────────────
# Python 3.13 changed how _root is set as an instance attribute on some widgets
# (via tkinter.Variable.__init__), which turns the _root() method into a plain
# PassNookApp instance.  When CallWrapper.__call__ catches an exception it calls
# self.widget._report_exception() → _report_exception calls self._root() →
# TypeError: 'PassNookApp' object is not callable.
# Patching Misc directly covers ALL widget classes, not just PassNookApp.
import tkinter as _tk

_orig_nametow = _tk.Misc.nametowidget
def _safe_nametowidget(self, name):
    try:
        return _orig_nametow(self, name)
    except (KeyError, TypeError):
        return name
_tk.Misc.nametowidget  = _safe_nametowidget
_tk.Misc._nametowidget = _safe_nametowidget  # alias used by _substitute

_orig_report_exc = _tk.Misc._report_exception
def _safe_report_exception(self):
    try:
        _orig_report_exc(self)
    except Exception:
        pass
_tk.Misc._report_exception = _safe_report_exception
# ─────────────────────────────────────────────────────────────────────────────

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

    # ── tkinter compatibility (Python 3.13 + PyInstaller windowed) ───────────

    def __setattr__(self, name, value):
        # Prevent anything from setting _root as an instance attribute, which
        # would shadow Misc._root() and cause TypeError when nametowidget calls
        # w._root() on the root window (Python 3.13 + customtkinter bug).
        if name == '_root':
            return
        super().__setattr__(name, value)

    def _root(self):
        """Root Tk window always IS the root — never traverse masters."""
        return self

    def _nametowidget(self, name):
        """_substitute calls this alias directly. Catch TypeError as safety net."""
        try:
            return super()._nametowidget(name)
        except (KeyError, TypeError):
            return name

    def _report_exception(self):
        """Swallow secondary crash if _root() still fails for any reason."""
        try:
            super()._report_exception()
        except Exception:
            pass

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
        self.resizable(True, True)
        self.minsize(820, 560)
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        win_w = min(1100, sw - 80)
        win_h = min(700, sh - 120)
        x = (sw - win_w) // 2
        y = (sh - win_h) // 2
        self.geometry(f"{win_w}x{win_h}+{x}+{y}")
        try:
            self._frame = MainFrame(self, self._vault, on_lock=self._lock)
            self._frame.grid(row=0, column=0, sticky="nsew")
        except Exception as exc:
            import traceback, tkinter.messagebox as mb
            mb.showerror("PassNook — startup error",
                         f"Failed to load main view:\n\n{traceback.format_exc()}")

    def _lock(self):
        self._vault.lock()
        self._show_lock()

    def _swap_frame(self, new):
        if self._frame:
            # Remove CTkScrollableFrame bind_all handlers before destroy to
            # prevent stale global bindings (Python 3.13 + customtkinter compat)
            for seq in ("<MouseWheel>", "<KeyPress-Shift_L>", "<KeyPress-Shift_R>",
                        "<KeyRelease-Shift_L>", "<KeyRelease-Shift_R>"):
                try:
                    self._frame.unbind_all(seq)
                except Exception:
                    pass
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


_MUTEX_HANDLE = None  # keep alive for process lifetime


def _ensure_single_instance():
    global _MUTEX_HANDLE
    _MUTEX_HANDLE = ctypes.windll.kernel32.CreateMutexW(None, False, "PassNook_SingleInstance_v1")
    if ctypes.windll.kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
        hwnd = ctypes.windll.user32.FindWindowW(None, "PassNook")
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 9)   # SW_RESTORE
            ctypes.windll.user32.SetForegroundWindow(hwnd)
        sys.exit(0)


def main():
    _ensure_single_instance()
    ensure_assets()
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = PassNookApp()
    app.mainloop()


if __name__ == "__main__":
    main()
