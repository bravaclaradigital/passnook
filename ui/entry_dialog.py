"""
PassNook — Add / Edit entry dialog
Handles both password entries and secure notes.
"""

from __future__ import annotations
from typing import Callable

import customtkinter as ctk

from core.vault import VaultManager
from core.generator import strength as pw_strength
from ui.styles import *
from ui.utils import center_over, set_icon


class EntryDialog(ctk.CTkToplevel):
    def __init__(self, parent, vault: VaultManager,
                 entry: dict | None = None,
                 default_type: str = "password",
                 on_save: Callable | None = None):
        super().__init__(parent)
        self._vault      = vault
        self._entry      = entry
        self._on_save    = on_save
        self._is_edit    = entry is not None
        self._kind       = entry.get("type", default_type) if entry else default_type

        title = ("Edit" if self._is_edit else "Add") + " Entry"
        self.title(title)
        self.geometry("460x660")
        self.resizable(False, False)
        self.configure(fg_color=SURFACE)
        self.grab_set()
        self.focus()

        self._build()
        set_icon(self)
        center_over(self, parent)

    # ── Build ─────────────────────────────────────────────────────────────────

    def _build(self):
        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=24, pady=16)
        wrap.grid_columnconfigure(0, weight=1)

        row = 0

        # ── Type toggle (only when adding) ────────────────────────────────────
        if not self._is_edit:
            seg = ctk.CTkSegmentedButton(
                wrap, values=["Password", "Secure Note"],
                selected_color=ACCENT, selected_hover_color=ACCENT_HOVER,
                unselected_color=CARD, unselected_hover_color=CARD_HOVER,
                text_color=TEXT, font=(FF, 13, "bold"),
                command=self._on_type_change,
            )
            seg.set("Password" if self._kind == "password" else "Secure Note")
            seg.grid(row=row, column=0, sticky="ew", pady=(0, 18))
            row += 1

        # ── Title field ───────────────────────────────────────────────────────
        label = "Site name" if self._kind == "password" else "Note title"
        self._lbl_title = self._label(wrap, row, label + " *")
        row += 1
        self._title_var = ctk.StringVar(
            value=self._entry.get("title", "") if self._entry else "")
        self._title_entry = self._entry_widget(wrap, row, self._title_var,
                                               f"e.g. {'Google' if self._kind == 'password' else 'Wi-Fi passwords'}")
        row += 1

        # ── Password-specific fields ──────────────────────────────────────────
        self._pw_widgets: list[ctk.CTkBaseClass] = []

        self._lbl_url = self._label(wrap, row, "URL  (optional)")
        self._pw_widgets.append(self._lbl_url)
        row += 1
        self._url_var = ctk.StringVar(
            value=self._entry.get("url", "") if self._entry else "")
        self._url_entry = self._entry_widget(wrap, row, self._url_var, "https://")
        self._pw_widgets.append(self._url_entry)
        row += 1

        self._lbl_user = self._label(wrap, row, "Username / Email *")
        self._pw_widgets.append(self._lbl_user)
        row += 1
        self._user_var = ctk.StringVar(
            value=self._entry.get("username", "") if self._entry else "")
        self._user_entry = self._entry_widget(wrap, row, self._user_var, "username@example.com")
        self._pw_widgets.append(self._user_entry)
        row += 1

        self._lbl_pw = self._label(wrap, row, "Password *")
        self._pw_widgets.append(self._lbl_pw)
        row += 1

        pw_row = ctk.CTkFrame(wrap, fg_color="transparent")
        pw_row.grid(row=row, column=0, sticky="ew", pady=(4, 0))
        pw_row.grid_columnconfigure(0, weight=1)
        self._pw_widgets.append(pw_row)
        row += 1

        self._pw_var = ctk.StringVar(
            value=self._entry.get("password", "") if self._entry else "")
        self._pw_entry = ctk.CTkEntry(
            pw_row, textvariable=self._pw_var, show="●",
            placeholder_text="Password",
            fg_color=INPUT_BG, border_color=BORDER,
            text_color=TEXT, placeholder_text_color=PLACEHOLDER,
            height=40, corner_radius=INPUT_RADIUS, font=FONT_SM,
        )
        self._pw_entry.grid(row=0, column=0, sticky="ew")

        self._pw_show = ctk.CTkButton(
            pw_row, text="👁", width=40, height=40,
            fg_color=CARD, hover_color=CARD_HOVER, text_color=SUBTEXT,
            corner_radius=INPUT_RADIUS, command=self._toggle_pw,
        )
        self._pw_show.grid(row=0, column=1, padx=(6, 0))

        gen_btn = ctk.CTkButton(
            pw_row, text="Generate", width=84, height=40,
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
            text_color="white", font=FONT_XS,
            corner_radius=INPUT_RADIUS, command=self._open_generator,
        )
        gen_btn.grid(row=0, column=2, padx=(6, 0))
        self._pw_widgets.append(gen_btn)

        # Strength bar
        self._str_bar = ctk.CTkProgressBar(
            wrap, height=4, corner_radius=2, fg_color=BORDER,
            progress_color=ACCENT)
        self._str_bar.set(0)
        self._str_bar.grid(row=row, column=0, sticky="ew", pady=(6, 0))
        self._pw_widgets.append(self._str_bar)
        row += 1

        str_row = ctk.CTkFrame(wrap, fg_color="transparent")
        str_row.grid(row=row, column=0, sticky="ew")
        str_row.grid_columnconfigure(0, weight=1)
        self._pw_widgets.append(str_row)
        row += 1

        self._str_lbl = ctk.CTkLabel(str_row, text="", font=FONT_XS, text_color=SUBTEXT)
        self._str_lbl.grid(row=0, column=0, sticky="w")

        # History button — only shown when editing an existing entry
        if self._is_edit and self._entry.get("password_history"):
            hist_btn = ctk.CTkButton(
                str_row, text="🕐 History", width=80, height=22,
                fg_color="transparent", hover_color=CARD,
                text_color=SUBTEXT, font=FONT_XS,
                corner_radius=4, command=self._show_history,
            )
            hist_btn.grid(row=0, column=1, sticky="e")
            self._pw_widgets.append(hist_btn)

        self._pw_var.trace_add("write", self._on_pw_change)

        # ── Notes / Content field ─────────────────────────────────────────────
        notes_label = "Content *" if self._kind == "note" else "Notes  (optional)"
        self._lbl_notes = self._label(wrap, row, notes_label)
        row += 1

        init_notes = (self._entry.get("content") or self._entry.get("notes", "")) \
            if self._entry else ""
        self._notes_box = ctk.CTkTextbox(
            wrap, height=60, fg_color=INPUT_BG, border_color=BORDER,
            border_width=2, text_color=TEXT, font=FONT_SM,
            corner_radius=INPUT_RADIUS, wrap="word",
        )
        self._notes_box.insert("1.0", init_notes)
        self._notes_box.grid(row=row, column=0, sticky="ew", pady=(4, 0))
        row += 1

        # ── Error label ───────────────────────────────────────────────────────
        self._err_lbl = ctk.CTkLabel(wrap, text="", font=FONT_XS, text_color=DANGER)
        self._err_lbl.grid(row=row, column=0, pady=(8, 0))
        row += 1

        # ── Buttons ───────────────────────────────────────────────────────────
        btns = ctk.CTkFrame(wrap, fg_color="transparent")
        btns.grid(row=row, column=0, sticky="ew", pady=(12, 0))
        btns.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(btns, text="Cancel", width=100, height=40,
                      fg_color=CARD, hover_color=CARD_HOVER,
                      text_color=TEXT, corner_radius=BTN_RADIUS,
                      command=self.destroy).grid(row=0, column=0, sticky="w")

        ctk.CTkButton(btns, text="Save Entry", width=120, height=40,
                      fg_color=ACCENT, hover_color=ACCENT_HOVER,
                      text_color="white", font=(FF, 13, "bold"),
                      corner_radius=BTN_RADIUS,
                      command=self._save).grid(row=0, column=1, sticky="e")

        # Apply initial visibility
        self._apply_type()
        self._title_entry.focus_set()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _label(self, parent, row, text):
        lbl = ctk.CTkLabel(parent, text=text, font=(FF, 12, "bold"),
                           text_color=SUBTEXT)
        lbl.grid(row=row, column=0, sticky="w", pady=(12, 0))
        return lbl

    def _entry_widget(self, parent, row, var, placeholder):
        e = ctk.CTkEntry(parent, textvariable=var,
                         placeholder_text=placeholder,
                         fg_color=INPUT_BG, border_color=BORDER,
                         text_color=TEXT, placeholder_text_color=PLACEHOLDER,
                         height=40, corner_radius=INPUT_RADIUS, font=FONT_SM)
        e.grid(row=row, column=0, sticky="ew", pady=(4, 0))
        return e

    def _apply_type(self):
        show_pw = self._kind == "password"
        for w in self._pw_widgets:
            if show_pw:
                w.grid()
            else:
                w.grid_remove()
        self._lbl_title.configure(
            text=("Site name *" if show_pw else "Note title *"))
        self._title_entry.configure(
            placeholder_text=("e.g. Google" if show_pw else "e.g. Wi-Fi passwords"))
        self._lbl_notes.configure(
            text=("Notes  (optional)" if show_pw else "Content *"))

    def _on_type_change(self, val: str):
        self._kind = "password" if val == "Password" else "note"
        self._apply_type()

    def _toggle_pw(self):
        cur = self._pw_entry.cget("show")
        self._pw_entry.configure(show="" if cur else "●")
        self._pw_show.configure(text="🙈" if cur else "👁")

    def _on_pw_change(self, *_):
        pw = self._pw_var.get()
        score, label, color = pw_strength(pw)
        self._str_bar.set(score / 4)
        self._str_bar.configure(progress_color=color)
        self._str_lbl.configure(text=label, text_color=color)

    def _show_history(self):
        import time as _time
        history = self._entry.get("password_history", [])
        if not history:
            return

        dlg = ctk.CTkToplevel(self)
        dlg.title("Password History")
        dlg.geometry("380x300")
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.focus()
        dlg.configure(fg_color=SURFACE)
        set_icon(dlg)

        ctk.CTkLabel(dlg, text="Password History", font=(FF, 15, "bold"),
                     text_color=TEXT).pack(pady=(20, 4), padx=20, anchor="w")
        ctk.CTkLabel(dlg, text="Click a password to restore it.",
                     font=FONT_XS, text_color=SUBTEXT).pack(padx=20, anchor="w")

        scroll = ctk.CTkScrollableFrame(dlg, fg_color=CARD, corner_radius=8)
        scroll.pack(fill="both", expand=True, padx=16, pady=12)
        scroll.grid_columnconfigure(0, weight=1)

        for i, h in enumerate(history):
            ts = _time.strftime("%Y-%m-%d %H:%M", _time.localtime(h["changed"]))
            pw = h["password"]
            row_frame = ctk.CTkFrame(scroll, fg_color="transparent")
            row_frame.grid(row=i, column=0, sticky="ew", pady=3)
            row_frame.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(row_frame, text=ts, font=FONT_XS,
                         text_color=SUBTEXT).grid(row=0, column=0, sticky="w")
            ctk.CTkButton(
                row_frame, text=pw, font=("Consolas", 12),
                fg_color=INPUT_BG, hover_color=BORDER,
                text_color=ACCENT_LIGHT, anchor="w",
                command=lambda p=pw: (self._pw_var.set(p), self._pw_entry.configure(show=""), dlg.destroy()),
            ).grid(row=1, column=0, sticky="ew", pady=(2, 0))

        ctk.CTkButton(dlg, text="Close", height=34,
                      fg_color=CARD, hover_color=CARD_HOVER, text_color=TEXT,
                      command=dlg.destroy).pack(pady=(0, 12))

    def _open_generator(self):
        from ui.generator_dialog import GeneratorDialog
        dlg = GeneratorDialog(self, on_use=self._use_generated)
        dlg.wait_window()

    def _use_generated(self, password: str):
        self._pw_var.set(password)
        self._pw_entry.configure(show="")
        self._pw_show.configure(text="🙈")

    # ── Save ──────────────────────────────────────────────────────────────────

    def _save(self):
        title = self._title_var.get().strip()
        if not title:
            self._show_err("Title is required.")
            return

        notes_content = self._notes_box.get("1.0", "end-1c").strip()

        if self._kind == "password":
            username = self._user_var.get().strip()
            password = self._pw_var.get()
            if not username:
                self._show_err("Username / Email is required.")
                return
            if not password:
                self._show_err("Password is required.")
                return
            data = {
                "type":     "password",
                "title":    title,
                "url":      self._url_var.get().strip(),
                "username": username,
                "password": password,
                "notes":    notes_content,
                "content":  "",
            }
        else:
            if not notes_content:
                self._show_err("Note content is required.")
                return
            data = {
                "type":     "note",
                "title":    title,
                "url":      "",
                "username": "",
                "password": "",
                "notes":    "",
                "content":  notes_content,
            }

        if self._is_edit:
            self._vault.update(self._entry["id"], data)
        else:
            self._vault.add(data)

        on_save = self._on_save
        self.destroy()
        if on_save:
            on_save()

    def _show_err(self, msg: str):
        self._err_lbl.configure(text=msg)
        self.after(3000, lambda: self._err_lbl.configure(text=""))
