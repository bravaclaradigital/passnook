"""
PassNook — Shared dialog utilities
"""

from __future__ import annotations
import sys
from pathlib import Path
import customtkinter as ctk


def _res(rel: str) -> Path:
    base = getattr(sys, "_MEIPASS", Path(__file__).parent.parent)
    return Path(base) / rel


def center_over(win: ctk.CTkToplevel, parent):
    """
    Center *win* over *parent*.
    Uses withdraw → full render → centre → deiconify so the window
    appears at the right position without any visible jump.
    """
    win.withdraw()
    win.update()          # force full render so winfo_width/height are real
    ww = win.winfo_width()
    wh = win.winfo_height()
    # Fallback to requested size if window hasn't expanded yet
    if ww < 10:
        ww = win.winfo_reqwidth()
    if wh < 10:
        wh = win.winfo_reqheight()

    px = parent.winfo_rootx()
    py = parent.winfo_rooty()
    pw = parent.winfo_width()
    ph = parent.winfo_height()

    x = px + max(0, (pw - ww) // 2)
    y = py + max(0, (ph - wh) // 2)
    win.geometry(f"+{x}+{y}")
    win.deiconify()


def set_icon(win: ctk.CTkToplevel):
    """Apply PassNook icon to a Toplevel window."""
    icon_path = _res("assets/icon.ico")
    if icon_path.exists():
        try:
            win.after(100, lambda: win.iconbitmap(str(icon_path)))
        except Exception:
            pass
