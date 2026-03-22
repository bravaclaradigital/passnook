"""
PassNook — Lock / First-run frame
Shown as the full window when the app is locked.
"""

from __future__ import annotations
import sys
from pathlib import Path
from typing import Callable

import customtkinter as ctk
from PIL import Image

from core.vault import VaultManager, WrongPassword
from core.generator import strength as pw_strength
from ui.styles import *


def _res(rel: str) -> Path:
    base = getattr(sys, "_MEIPASS", Path(__file__).parent.parent)
    return Path(base) / rel


class LockFrame(ctk.CTkFrame):
    def __init__(self, master, vault: VaultManager, on_unlock: Callable):
        super().__init__(master, fg_color=BG, corner_radius=0)
        self._vault      = vault
        self._on_unlock  = on_unlock
        self._first_run  = not vault.vault_exists

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build()

    # ── Build ─────────────────────────────────────────────────────────────────

    def _build(self):
        # Central card
        card = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=20,
                             border_width=1, border_color=BORDER)
        card.grid(row=0, column=0, padx=40, pady=40, sticky="")
        card.grid_columnconfigure(0, weight=1)

        row = 0

        # ── Logo ──────────────────────────────────────────────────────────────
        logo_path = _res("assets/logo.png")
        if logo_path.exists():
            img = ctk.CTkImage(Image.open(str(logo_path)), size=(72, 72))
            ctk.CTkLabel(card, image=img, text="").grid(
                row=row, column=0, pady=(36, 0))
        else:
            # Fallback coloured circle
            ctk.CTkLabel(card, text="PN", font=FONT_LG,
                         text_color="white",
                         fg_color=ACCENT, corner_radius=36,
                         width=72, height=72).grid(row=row, column=0, pady=(36, 0))
        row += 1

        # ── Title ─────────────────────────────────────────────────────────────
        ctk.CTkLabel(card, text="PassNook", font=FONT_XL,
                     text_color=TEXT).grid(row=row, column=0, pady=(10, 0))
        row += 1

        sub = "Set up your vault" if self._first_run else "Your secure password vault"
        ctk.CTkLabel(card, text=sub, font=FONT_XS,
                     text_color=SUBTEXT).grid(row=row, column=0, pady=(2, 24))
        row += 1

        # ── Divider ───────────────────────────────────────────────────────────
        ctk.CTkFrame(card, height=1, fg_color=BORDER).grid(
            row=row, column=0, sticky="ew", padx=32, pady=(0, 24))
        row += 1

        # ── Heading ───────────────────────────────────────────────────────────
        heading = "Create a master password" if self._first_run else "Enter your master password"
        ctk.CTkLabel(card, text=heading, font=(FF, 13, "bold"),
                     text_color=TEXT).grid(row=row, column=0, padx=40, sticky="w")
        row += 1

        # ── Password entry ────────────────────────────────────────────────────
        self._pw_var = ctk.StringVar()
        pw_frame = ctk.CTkFrame(card, fg_color="transparent")
        pw_frame.grid(row=row, column=0, padx=40, pady=(8, 0), sticky="ew")
        pw_frame.grid_columnconfigure(0, weight=1)

        self._pw_entry = ctk.CTkEntry(
            pw_frame, textvariable=self._pw_var, show="●",
            placeholder_text="Master password",
            fg_color=INPUT_BG, border_color=BORDER,
            text_color=TEXT, placeholder_text_color=PLACEHOLDER,
            height=42, corner_radius=INPUT_RADIUS, font=FONT_SM,
        )
        self._pw_entry.grid(row=0, column=0, sticky="ew")

        self._show_btn = ctk.CTkButton(
            pw_frame, text="👁", width=42, height=42,
            fg_color=CARD, hover_color=CARD_HOVER,
            text_color=SUBTEXT, corner_radius=INPUT_RADIUS,
            command=self._toggle_show,
        )
        self._show_btn.grid(row=0, column=1, padx=(6, 0))
        row += 1

        # ── Strength bar (first-run only) ─────────────────────────────────────
        if self._first_run:
            self._strength_bar  = ctk.CTkProgressBar(
                card, height=4, corner_radius=2,
                fg_color=BORDER, progress_color=ACCENT)
            self._strength_bar.set(0)
            self._strength_bar.grid(row=row, column=0, padx=40, pady=(6, 0), sticky="ew")
            row += 1

            self._strength_lbl = ctk.CTkLabel(
                card, text="", font=FONT_XS, text_color=SUBTEXT)
            self._strength_lbl.grid(row=row, column=0, padx=40, sticky="w")
            row += 1

            self._pw_var.trace_add("write", self._on_pw_change)

            # Confirm entry
            ctk.CTkLabel(card, text="Confirm password", font=(FF, 13, "bold"),
                         text_color=TEXT).grid(row=row, column=0, padx=40,
                                               pady=(14, 0), sticky="w")
            row += 1

            self._confirm_var = ctk.StringVar()
            cf_frame = ctk.CTkFrame(card, fg_color="transparent")
            cf_frame.grid(row=row, column=0, padx=40, pady=(8, 0), sticky="ew")
            cf_frame.grid_columnconfigure(0, weight=1)

            self._cf_entry = ctk.CTkEntry(
                cf_frame, textvariable=self._confirm_var, show="●",
                placeholder_text="Confirm master password",
                fg_color=INPUT_BG, border_color=BORDER,
                text_color=TEXT, placeholder_text_color=PLACEHOLDER,
                height=42, corner_radius=INPUT_RADIUS, font=FONT_SM,
            )
            self._cf_entry.grid(row=0, column=0, sticky="ew")

            self._cf_show_btn = ctk.CTkButton(
                cf_frame, text="👁", width=42, height=42,
                fg_color=CARD, hover_color=CARD_HOVER,
                text_color=SUBTEXT, corner_radius=INPUT_RADIUS,
                command=self._toggle_show_cf,
            )
            self._cf_show_btn.grid(row=0, column=1, padx=(6, 0))
            row += 1

        # ── Error label ───────────────────────────────────────────────────────
        self._err_lbl = ctk.CTkLabel(card, text="", font=FONT_XS,
                                      text_color=DANGER)
        self._err_lbl.grid(row=row, column=0, padx=40, pady=(8, 0))
        row += 1

        # ── Action button ─────────────────────────────────────────────────────
        btn_text = "Create Vault" if self._first_run else "Unlock"
        btn_color = ACCENT if self._first_run else SUCCESS
        btn_hover = ACCENT_HOVER if self._first_run else SUCCESS_HOVER

        self._action_btn = ctk.CTkButton(
            card, text=btn_text, height=44,
            fg_color=btn_color, hover_color=btn_hover,
            text_color="white", font=(FF, 14, "bold"),
            corner_radius=BTN_RADIUS,
            command=self._on_action,
        )
        self._action_btn.grid(row=row, column=0, padx=40, pady=(12, 40), sticky="ew")
        row += 1

        # Bind Enter key
        self._pw_entry.bind("<Return>", lambda _: self._on_action())
        if self._first_run and hasattr(self, "_cf_entry"):
            self._cf_entry.bind("<Return>", lambda _: self._on_action())

        self._pw_entry.focus_set()

    # ── Handlers ──────────────────────────────────────────────────────────────

    def _toggle_show(self):
        cur = self._pw_entry.cget("show")
        self._pw_entry.configure(show="" if cur else "●")
        self._show_btn.configure(text="🙈" if cur else "👁")

    def _toggle_show_cf(self):
        cur = self._cf_entry.cget("show")
        self._cf_entry.configure(show="" if cur else "●")
        self._cf_show_btn.configure(text="🙈" if cur else "👁")

    def _on_pw_change(self, *_):
        pw = self._pw_var.get()
        score, label, color = pw_strength(pw)
        self._strength_bar.set(score / 4)
        self._strength_bar.configure(progress_color=color)
        self._strength_lbl.configure(text=label, text_color=color)

    def _on_action(self):
        pw = self._pw_var.get().strip()
        if not pw:
            self._show_error("Please enter a password.")
            return

        if self._first_run:
            if len(pw) < 6:
                self._show_error("Password must be at least 6 characters.")
                return
            cf = self._confirm_var.get().strip()
            if pw != cf:
                self._show_error("Passwords don't match.")
                return
            try:
                self._vault.create(pw)
                self._on_unlock()
            except Exception as e:
                self._show_error(f"Error: {e}")
        else:
            try:
                self._vault.open(pw)
                self._on_unlock()
            except WrongPassword:
                self._show_error("Incorrect password. Please try again.")
            except Exception as e:
                self._show_error(f"Error: {e}")

    def _show_error(self, msg: str):
        self._err_lbl.configure(text=msg)
        self._pw_entry.configure(border_color=DANGER)
        self.after(3000, lambda: (
            self._err_lbl.configure(text=""),
            self._pw_entry.configure(border_color=BORDER),
        ))
