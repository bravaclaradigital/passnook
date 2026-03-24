"""
PassNook — Password generator dialog
Can be opened standalone (from sidebar) or from an entry dialog (returns password).
"""

from __future__ import annotations
from typing import Callable

import customtkinter as ctk

from core.generator import generate, strength as pw_strength
import core.clipboard as cb
from ui.styles import *
from ui.utils import center_over, set_icon


class GeneratorDialog(ctk.CTkToplevel):
    def __init__(self, parent, on_use: Callable[[str], None] | None = None):
        super().__init__(parent)
        self._on_use   = on_use
        self._parent   = parent

        self.title("Password Generator")
        self.geometry("420x440")
        self.resizable(False, False)
        self.configure(fg_color=SURFACE)
        self.grab_set()
        self.focus()

        self._build()
        self._regenerate()
        set_icon(self)
        center_over(self, parent)

    def _build(self):
        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=28, pady=24)
        wrap.grid_columnconfigure(0, weight=1)

        row = 0

        # Title
        ctk.CTkLabel(wrap, text="Password Generator", font=(FF, 17, "bold"),
                     text_color=TEXT).grid(row=row, column=0, sticky="w")
        row += 1

        ctk.CTkLabel(wrap, text="Create a strong, random password",
                     font=FONT_XS, text_color=SUBTEXT).grid(
            row=row, column=0, sticky="w", pady=(2, 18))
        row += 1

        # ── Generated password display ────────────────────────────────────────
        pw_frame = ctk.CTkFrame(wrap, fg_color=INPUT_BG, corner_radius=CARD_RADIUS,
                                border_width=1, border_color=BORDER)
        pw_frame.grid(row=row, column=0, sticky="ew", pady=(0, 8))
        pw_frame.grid_columnconfigure(0, weight=1)
        row += 1

        self._pw_lbl = ctk.CTkLabel(
            pw_frame, text="", font=("Consolas", 17, "bold"),
            text_color=ACCENT_LIGHT, wraplength=320, justify="center")
        self._pw_lbl.grid(row=0, column=0, padx=16, pady=16, sticky="ew")

        # Strength bar
        self._str_bar = ctk.CTkProgressBar(
            wrap, height=5, corner_radius=2, fg_color=BORDER,
            progress_color=ACCENT)
        self._str_bar.set(0)
        self._str_bar.grid(row=row, column=0, sticky="ew")
        row += 1

        str_row = ctk.CTkFrame(wrap, fg_color="transparent")
        str_row.grid(row=row, column=0, sticky="ew", pady=(4, 16))
        str_row.grid_columnconfigure(0, weight=1)
        row += 1

        self._str_lbl = ctk.CTkLabel(str_row, text="", font=FONT_XS, text_color=SUBTEXT)
        self._str_lbl.grid(row=0, column=0, sticky="w")

        self._len_lbl = ctk.CTkLabel(str_row, text="", font=FONT_XS, text_color=SUBTEXT)
        self._len_lbl.grid(row=0, column=1, sticky="e")

        # ── Length slider ─────────────────────────────────────────────────────
        ctk.CTkLabel(wrap, text="Length", font=(FF, 12, "bold"),
                     text_color=SUBTEXT).grid(row=row, column=0, sticky="w")
        row += 1

        self._len_var = ctk.IntVar(value=16)
        ctk.CTkSlider(
            wrap, from_=8, to=64, variable=self._len_var,
            button_color=ACCENT, button_hover_color=ACCENT_HOVER,
            progress_color=ACCENT, fg_color=BORDER,
            command=lambda _: self._regenerate(),
        ).grid(row=row, column=0, sticky="ew", pady=(6, 16))
        row += 1

        # ── Checkboxes ────────────────────────────────────────────────────────
        checks = ctk.CTkFrame(wrap, fg_color="transparent")
        checks.grid(row=row, column=0, sticky="ew", pady=(0, 20))
        checks.grid_columnconfigure((0, 1), weight=1)
        row += 1

        self._upper  = self._checkbox(checks, "Uppercase  A–Z", 0, 0, True)
        self._lower  = self._checkbox(checks, "Lowercase  a–z", 0, 1, True)
        self._nums   = self._checkbox(checks, "Numbers  0–9",   1, 0, True)
        self._syms   = self._checkbox(checks, "Symbols  !@#…",  1, 1, True)

        # ── Action buttons ────────────────────────────────────────────────────
        btn_row = ctk.CTkFrame(wrap, fg_color="transparent")
        btn_row.grid(row=row, column=0, sticky="ew")
        btn_row.grid_columnconfigure(0, weight=1)
        row += 1

        ctk.CTkButton(btn_row, text="↻  Regenerate", width=130, height=40,
                      fg_color=CARD, hover_color=CARD_HOVER,
                      text_color=TEXT, corner_radius=BTN_RADIUS,
                      font=FONT_SM,
                      command=self._regenerate).grid(row=0, column=0, sticky="w")

        self._copy_btn = ctk.CTkButton(
            btn_row, text="Copy", width=90, height=40,
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
            text_color="white", corner_radius=BTN_RADIUS,
            font=(FF, 13, "bold"),
            command=self._copy,
        )
        self._copy_btn.grid(row=0, column=1, padx=(8, 0))

        if self._on_use:
            ctk.CTkButton(btn_row, text="Use this password", height=40,
                          fg_color=SUCCESS, hover_color=SUCCESS_HOVER,
                          text_color="white", corner_radius=BTN_RADIUS,
                          font=(FF, 13, "bold"),
                          command=self._use).grid(row=0, column=2, padx=(8, 0))

    def _checkbox(self, parent, label, r, c, default):
        var = ctk.BooleanVar(value=default)
        cb = ctk.CTkCheckBox(
            parent, text=label, variable=var, font=FONT_SM,
            text_color=TEXT, fg_color=ACCENT, hover_color=ACCENT_HOVER,
            border_color=BORDER,
            command=self._regenerate,
        )
        cb.grid(row=r, column=c, sticky="w", padx=4, pady=4)
        return var

    def _regenerate(self):
        length = int(self._len_var.get())
        pw = generate(
            length=length,
            uppercase=self._upper.get(),
            lowercase=self._lower.get(),
            numbers=self._nums.get(),
            symbols=self._syms.get(),
        )
        self._current = pw
        self._pw_lbl.configure(text=pw)
        score, label, color = pw_strength(pw)
        self._str_bar.set(score / 4)
        self._str_bar.configure(progress_color=color)
        self._str_lbl.configure(text=label, text_color=color)
        self._len_lbl.configure(text=f"{length} characters")

    def _copy(self):
        cb.copy(self.winfo_toplevel(), self._current)
        self._copy_btn.configure(text="Copied ✓", fg_color=SUCCESS)
        self.after(2000, lambda: self._copy_btn.configure(
            text="Copy", fg_color=ACCENT))

    def _use(self):
        if self._on_use:
            self._on_use(self._current)
        self.destroy()
