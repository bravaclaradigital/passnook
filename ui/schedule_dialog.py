"""
PassNook — Scheduled backup settings dialog
"""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from core import schedule as sched
from ui.styles import *
from ui.utils import center_over, set_icon


# ── Hour labels (index == 24-hour value) ──────────────────────────────────────

def _make_hours() -> list[str]:
    labels = []
    for h in range(24):
        if h == 0:
            labels.append("12:00 AM")
        elif h < 12:
            labels.append(f"{h}:00 AM")
        elif h == 12:
            labels.append("12:00 PM")
        else:
            labels.append(f"{h - 12}:00 PM")
    return labels


_HOURS        = _make_hours()
_DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday",
                 "Thursday", "Friday", "Saturday", "Sunday"]
_DAYS_OF_MONTH = [str(i) for i in range(1, 29)]   # "1" … "28"


# ── Dialog ────────────────────────────────────────────────────────────────────

class ScheduleDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Auto Backup")
        self.geometry("440x530")
        self.resizable(False, False)
        self.configure(fg_color=SURFACE)
        self.grab_set()
        self.focus()

        self._cfg = sched.load()
        self._build()
        set_icon(self)
        center_over(self, parent)

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build(self):
        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=28, pady=22)
        wrap.grid_columnconfigure(1, weight=1)

        r = 0

        # ── Enable checkbox ───────────────────────────────────────────────────
        self._enabled_var = tk.BooleanVar(value=self._cfg.get("enabled", False))
        ctk.CTkCheckBox(
            wrap, text="Enable scheduled backups",
            variable=self._enabled_var,
            font=(FF, 13, "bold"), text_color=TEXT,
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
            checkmark_color="white",
            command=self._on_toggle,
        ).grid(row=r, column=0, columnspan=2, sticky="w", pady=(0, 18))
        r += 1

        ctk.CTkFrame(wrap, height=1, fg_color=BORDER).grid(
            row=r, column=0, columnspan=2, sticky="ew", pady=(0, 18))
        r += 1

        # ── Frequency ─────────────────────────────────────────────────────────
        ctk.CTkLabel(wrap, text="Frequency", font=FONT_XS,
                     text_color=SUBTEXT).grid(
            row=r, column=0, columnspan=2, sticky="w", pady=(0, 6))
        r += 1

        self._freq_var = tk.StringVar(
            value=self._cfg.get("frequency", "daily").capitalize())
        self._freq_seg = ctk.CTkSegmentedButton(
            wrap, values=["Daily", "Weekly", "Monthly"],
            variable=self._freq_var,
            font=FONT_SM,
            fg_color=CARD,
            selected_color=ACCENT, selected_hover_color=ACCENT_HOVER,
            unselected_color=CARD, unselected_hover_color=CARD_HOVER,
            text_color=TEXT,
            command=self._on_freq_change,
        )
        self._freq_seg.grid(row=r, column=0, columnspan=2,
                            sticky="ew", pady=(0, 14))
        r += 1

        # ── Run at (hour) ─────────────────────────────────────────────────────
        ctk.CTkLabel(wrap, text="Run at", font=FONT_SM,
                     text_color=SUBTEXT).grid(row=r, column=0, sticky="w")
        self._hour_var = tk.StringVar(
            value=_HOURS[int(self._cfg.get("hour", 10))])
        self._hour_menu = ctk.CTkOptionMenu(
            wrap, variable=self._hour_var, values=_HOURS,
            fg_color=CARD, button_color=CARD_HOVER,
            button_hover_color=CARD_SEL,
            dropdown_fg_color=CARD, dropdown_hover_color=CARD_HOVER,
            text_color=TEXT, font=FONT_SM, width=160,
        )
        self._hour_menu.grid(row=r, column=1, sticky="e", pady=(0, 10))
        r += 1

        # ── Conditional row (weekly / monthly) ────────────────────────────────
        self._cond_row = r

        # Weekly widgets
        self._dow_lbl = ctk.CTkLabel(wrap, text="On", font=FONT_SM,
                                     text_color=SUBTEXT)
        self._dow_var = tk.StringVar(
            value=_DAYS_OF_WEEK[int(self._cfg.get("day_of_week", 0))])
        self._dow_menu = ctk.CTkOptionMenu(
            wrap, variable=self._dow_var, values=_DAYS_OF_WEEK,
            fg_color=CARD, button_color=CARD_HOVER,
            button_hover_color=CARD_SEL,
            dropdown_fg_color=CARD, dropdown_hover_color=CARD_HOVER,
            text_color=TEXT, font=FONT_SM, width=160,
        )

        # Monthly widgets
        self._dom_lbl = ctk.CTkLabel(wrap, text="On day", font=FONT_SM,
                                     text_color=SUBTEXT)
        self._dom_var = tk.StringVar(
            value=str(self._cfg.get("day_of_month", 1)))
        self._dom_menu = ctk.CTkOptionMenu(
            wrap, variable=self._dom_var, values=_DAYS_OF_MONTH,
            fg_color=CARD, button_color=CARD_HOVER,
            button_hover_color=CARD_SEL,
            dropdown_fg_color=CARD, dropdown_hover_color=CARD_HOVER,
            text_color=TEXT, font=FONT_SM, width=160,
        )

        # Grid them once so grid_remove() / grid() can restore positions
        self._dow_lbl.grid( row=r, column=0, sticky="w",  pady=(0, 10))
        self._dow_menu.grid(row=r, column=1, sticky="e",  pady=(0, 10))
        self._dom_lbl.grid( row=r, column=0, sticky="w",  pady=(0, 10))
        self._dom_menu.grid(row=r, column=1, sticky="e",  pady=(0, 10))
        # Hide immediately; shown by _update_cond_row
        self._dow_lbl.grid_remove()
        self._dow_menu.grid_remove()
        self._dom_lbl.grid_remove()
        self._dom_menu.grid_remove()
        r += 1

        ctk.CTkFrame(wrap, height=1, fg_color=BORDER).grid(
            row=r, column=0, columnspan=2, sticky="ew", pady=(4, 18))
        r += 1

        # ── Backup folder ─────────────────────────────────────────────────────
        ctk.CTkLabel(wrap, text="Save backups to", font=FONT_XS,
                     text_color=SUBTEXT).grid(
            row=r, column=0, columnspan=2, sticky="w", pady=(0, 6))
        r += 1

        folder_row = ctk.CTkFrame(wrap, fg_color="transparent")
        folder_row.grid(row=r, column=0, columnspan=2,
                        sticky="ew", pady=(0, 14))
        folder_row.grid_columnconfigure(0, weight=1)

        self._folder_var = tk.StringVar(value=self._cfg.get("folder", ""))
        self._folder_entry = ctk.CTkEntry(
            folder_row, textvariable=self._folder_var,
            fg_color=INPUT_BG, border_color=BORDER,
            text_color=TEXT, font=FONT_SM, height=34,
            corner_radius=INPUT_RADIUS,
        )
        self._folder_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self._browse_btn = ctk.CTkButton(
            folder_row, text="Browse…", width=80, height=34,
            fg_color=CARD_HOVER, hover_color=CARD_SEL,
            text_color=ACCENT_LIGHT, font=FONT_XS,
            corner_radius=BTN_RADIUS,
            command=self._browse,
        )
        self._browse_btn.grid(row=0, column=1)
        r += 1

        # ── Keep last N ───────────────────────────────────────────────────────
        keep_row = ctk.CTkFrame(wrap, fg_color="transparent")
        keep_row.grid(row=r, column=0, columnspan=2,
                      sticky="w", pady=(0, 22))

        ctk.CTkLabel(keep_row, text="Keep last",
                     font=FONT_SM, text_color=SUBTEXT).pack(side="left")
        self._keep_var = tk.StringVar(value=str(self._cfg.get("keep", 10)))
        self._keep_entry = ctk.CTkEntry(
            keep_row, textvariable=self._keep_var,
            fg_color=INPUT_BG, border_color=BORDER,
            text_color=TEXT, font=FONT_SM,
            width=52, height=30, corner_radius=INPUT_RADIUS,
        )
        self._keep_entry.pack(side="left", padx=8)
        ctk.CTkLabel(keep_row, text="backups",
                     font=FONT_SM, text_color=SUBTEXT).pack(side="left")
        r += 1

        # ── Buttons ───────────────────────────────────────────────────────────
        btn_row = ctk.CTkFrame(wrap, fg_color="transparent")
        btn_row.grid(row=r, column=0, columnspan=2, sticky="ew")

        ctk.CTkButton(
            btn_row, text="Cancel", width=110, height=36,
            fg_color=CARD, hover_color=CARD_HOVER,
            text_color=TEXT, corner_radius=BTN_RADIUS,
            command=self.destroy,
        ).pack(side="left")
        ctk.CTkButton(
            btn_row, text="Save", width=110, height=36,
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
            text_color="white", corner_radius=BTN_RADIUS,
            command=self._save,
        ).pack(side="right")

        # Apply initial state
        self._update_cond_row()
        self._apply_enabled_state()

    # ── Event handlers ────────────────────────────────────────────────────────

    def _on_toggle(self):
        self._apply_enabled_state()

    def _on_freq_change(self, _val=None):
        self._update_cond_row()

    def _update_cond_row(self):
        freq = self._freq_var.get()
        self._dow_lbl.grid_remove()
        self._dow_menu.grid_remove()
        self._dom_lbl.grid_remove()
        self._dom_menu.grid_remove()
        if freq == "Weekly":
            self._dow_lbl.grid()
            self._dow_menu.grid()
        elif freq == "Monthly":
            self._dom_lbl.grid()
            self._dom_menu.grid()

    def _apply_enabled_state(self):
        enabled = self._enabled_var.get()
        state   = "normal" if enabled else "disabled"
        for w in (self._freq_seg, self._hour_menu,
                  self._dow_menu, self._dom_menu,
                  self._folder_entry, self._browse_btn, self._keep_entry):
            try:
                w.configure(state=state)
            except Exception:
                pass

    def _browse(self):
        folder = filedialog.askdirectory(
            title="Select backup folder",
            initialdir=self._folder_var.get() or str(Path.home()),
            parent=self,
        )
        if folder:
            self._folder_var.set(folder)

    def _save(self):
        folder = self._folder_var.get().strip()
        if self._enabled_var.get() and not folder:
            messagebox.showwarning(
                "Missing folder",
                "Please choose a folder to save backups to.",
                parent=self,
            )
            return

        try:
            keep = int(self._keep_var.get())
            if keep < 1:
                raise ValueError
        except ValueError:
            messagebox.showwarning(
                "Invalid value",
                "\"Keep last\" must be a whole number of 1 or more.",
                parent=self,
            )
            return

        self._cfg.update({
            "enabled":      self._enabled_var.get(),
            "frequency":    self._freq_var.get().lower(),
            "hour":         _HOURS.index(self._hour_var.get()),
            "day_of_week":  _DAYS_OF_WEEK.index(self._dow_var.get()),
            "day_of_month": int(self._dom_var.get()),
            "folder":       folder,
            "keep":         keep,
        })
        sched.save(self._cfg)
        self.destroy()
