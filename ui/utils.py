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
    Center *win* over *parent* (walks up to the actual toplevel).
    Uses update_idletasks (NOT update) to avoid deadlocking with grab_set().
    """
    win.update_idletasks()
    ww = win.winfo_width()
    wh = win.winfo_height()
    if ww < 10:
        ww = win.winfo_reqwidth()
    if wh < 10:
        wh = win.winfo_reqheight()

    # Walk up to actual toplevel so we always get the real window position/size
    p = parent
    while p.master is not None and not isinstance(p, (ctk.CTk, ctk.CTkToplevel)):
        p = p.master

    px = p.winfo_rootx()
    py = p.winfo_rooty()
    pw = p.winfo_width()
    ph = p.winfo_height()

    x = px + max(0, (pw - ww) // 2)
    y = py + max(0, (ph - wh) // 2)

    # Clamp so the dialog never goes off screen
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    x = max(0, min(x, sw - ww))
    y = max(0, min(y, sh - wh))
    win.geometry(f"+{x}+{y}")


def set_icon(win: ctk.CTkToplevel):
    """Apply PassNook icon to a Toplevel window."""
    icon_path = _res("assets/icon.ico")
    if icon_path.exists():
        p = str(icon_path)
        def _apply():
            if win.winfo_exists():
                try:
                    win.iconbitmap(p)
                except Exception:
                    pass
        # Apply after CTK finishes its own internal icon setup
        win.after(0, _apply)
        win.after(200, _apply)
