"""
PassNook — About dialog
"""

from __future__ import annotations
import sys
import webbrowser
from pathlib import Path

import customtkinter as ctk
from PIL import Image

from ui.styles import *
from ui.utils import center_over, set_icon

VERSION = "1.0.1"


def _res(rel: str) -> Path:
    base = getattr(sys, "_MEIPASS", Path(__file__).parent.parent)
    return Path(base) / rel


class AboutDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("About PassNook")
        self.geometry("360x560")
        self.resizable(False, False)
        self.configure(fg_color=SURFACE)
        self.grab_set()
        self.focus()

        self._build()
        set_icon(self)
        center_over(self, parent)

    def _build(self):
        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(padx=36, pady=28)

        # PassNook logo
        logo_path = _res("assets/logo.png")
        if logo_path.exists():
            img = ctk.CTkImage(Image.open(str(logo_path)), size=(68, 68))
            ctk.CTkLabel(wrap, image=img, text="").pack(pady=(0, 10))

        # App name + version
        ctk.CTkLabel(wrap, text="PassNook", font=(FF, 26, "bold"),
                     text_color=TEXT).pack()
        ctk.CTkLabel(wrap, text=f"Version {VERSION}", font=FONT_XS,
                     text_color=SUBTEXT).pack(pady=(2, 14))

        # Divider
        ctk.CTkFrame(wrap, height=1, fg_color=BORDER, width=260).pack(pady=(0, 14))

        # Description
        ctk.CTkLabel(
            wrap,
            text="A simple, secure password manager for Windows.",
            font=FONT_SM, text_color=SUBTEXT, justify="center",
        ).pack()
        ctk.CTkLabel(
            wrap,
            text="No cloud. No accounts. No tracking.\nYour vault never leaves your computer.",
            font=FONT_XS, text_color=PLACEHOLDER, justify="center",
        ).pack(pady=(6, 14))

        # GitHub link
        gh_lbl = ctk.CTkLabel(
            wrap, text="View on GitHub →",
            font=FONT_SM, text_color=ACCENT_LIGHT, cursor="hand2",
        )
        gh_lbl.pack(pady=(0, 14))
        gh_lbl.bind("<Button-1>", lambda _e: webbrowser.open(
            "https://github.com/bravaclaradigital/passnook"))

        # Divider
        ctk.CTkFrame(wrap, height=1, fg_color=BORDER, width=260).pack(pady=(0, 14))

        # Brava IT logo
        brava_path = _res("assets/brava-logo.png")
        if brava_path.exists():
            raw = Image.open(str(brava_path)).convert("RGBA")
            # Scale to fixed width, preserve aspect ratio
            w, h = raw.size
            target_w = 130
            target_h = int(h * target_w / w)
            brava_img = ctk.CTkImage(raw, size=(target_w, target_h))
            brava_lbl = ctk.CTkLabel(wrap, image=brava_img, text="", cursor="hand2")
            brava_lbl.pack(pady=(0, 4))
            brava_lbl.bind("<Button-1>", lambda _e: webbrowser.open("https://bravait.com"))

        site_lbl = ctk.CTkLabel(wrap, text="© 2026 Brava IT · bravait.com",
                                font=FONT_XS, text_color=PLACEHOLDER, cursor="hand2")
        site_lbl.pack(pady=(0, 14))
        site_lbl.bind("<Button-1>", lambda _e: webbrowser.open("https://bravait.com"))

        ctk.CTkButton(
            wrap, text="Close", width=120, height=36,
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
            text_color="white", corner_radius=BTN_RADIUS,
            command=self.destroy,
        ).pack()
