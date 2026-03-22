"""
PassNook — Main vault frame
Two-column layout: sidebar (220 px fixed) + scrollable entry list.
"""

from __future__ import annotations
import sys
from pathlib import Path
from typing import Callable

import customtkinter as ctk
from PIL import Image

from core.vault import VaultManager
import core.clipboard as cb
from ui.styles import *
from ui.utils import center_over, set_icon


def _res(rel: str) -> Path:
    base = getattr(sys, "_MEIPASS", Path(__file__).parent.parent)
    return Path(base) / rel


# ── Helpers ───────────────────────────────────────────────────────────────────

def _initial_badge(parent, letter: str, color: str, size: int = 40):
    f = ctk.CTkFrame(parent, width=size, height=size,
                     fg_color=color, corner_radius=size // 2)
    f.grid_propagate(False)
    ctk.CTkLabel(f, text=letter.upper()[:1], font=(FF, size // 2, "bold"),
                 text_color="white").place(relx=0.5, rely=0.5, anchor="center")
    return f


# ── Entry card ────────────────────────────────────────────────────────────────

class EntryCard(ctk.CTkFrame):
    def __init__(self, parent, entry: dict, vault: VaultManager,
                 root, on_edit: Callable, on_delete: Callable, on_refresh: Callable):
        super().__init__(parent, fg_color=CARD, corner_radius=CARD_RADIUS,
                         border_width=1, border_color=BORDER)
        self._entry   = entry
        self._vault   = vault
        self._root    = root
        self._on_edit    = on_edit
        self._on_delete  = on_delete
        self._on_refresh = on_refresh
        self._build()

    def _build(self):
        e    = self._entry
        kind = e.get("type", "password")
        name = e.get("title", "—")

        self.grid_columnconfigure(1, weight=1)

        # ── Icon ──────────────────────────────────────────────────────────────
        color = NOTE_ACCENT if kind == "note" else site_color(name)
        badge = _initial_badge(self, name, color, 40)
        badge.grid(row=0, column=0, rowspan=3, padx=(14, 0), pady=14, sticky="n")

        # ── Title + subtitle ──────────────────────────────────────────────────
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=1, padx=12, pady=(14, 0), sticky="ew")
        hdr.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(hdr, text=name, font=(FF, 14, "bold"),
                     text_color=TEXT, anchor="w").grid(row=0, column=0, sticky="ew")

        sub = e.get("url", "") if kind == "password" else "Secure Note"
        if sub:
            ctk.CTkLabel(hdr, text=sub, font=FONT_XS,
                         text_color=SUBTEXT, anchor="w").grid(row=1, column=0, sticky="ew")

        # ── Password row / Note preview ───────────────────────────────────────
        detail = ctk.CTkFrame(self, fg_color="transparent")
        detail.grid(row=1, column=1, padx=12, pady=(6, 0), sticky="ew")
        detail.grid_columnconfigure(0, weight=1)

        if kind == "password":
            user = e.get("username", "")
            if user:
                ur = ctk.CTkFrame(detail, fg_color="transparent")
                ur.grid(row=0, column=0, sticky="ew", pady=1)
                ur.grid_columnconfigure(0, weight=1)
                ctk.CTkLabel(ur, text=f"👤  {user}", font=FONT_SM,
                             text_color=SUBTEXT, anchor="w").grid(row=0, column=0, sticky="ew")
                self._copy_btn(ur, "Copy Username", lambda: self._copy(user), 1)

            pr = ctk.CTkFrame(detail, fg_color="transparent")
            pr.grid(row=1, column=0, sticky="ew", pady=1)
            pr.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(pr, text="🔑  ••••••••••••", font=FONT_SM,
                         text_color=SUBTEXT, anchor="w").grid(row=0, column=0, sticky="ew")
            self._copy_btn(pr, "Copy Password",
                           lambda: self._copy(e.get("password", "")), 1)
        else:
            preview = (e.get("content", "")[:60] + "…") \
                if len(e.get("content", "")) > 60 else e.get("content", "")
            ctk.CTkLabel(detail, text=preview, font=FONT_SM,
                         text_color=SUBTEXT, anchor="w", wraplength=400,
                         justify="left").grid(row=0, column=0, sticky="ew")

        # ── Action row ────────────────────────────────────────────────────────
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=2, column=1, padx=12, pady=(6, 12), sticky="e")

        ctk.CTkButton(actions, text="Edit", width=68, height=28,
                      fg_color=CARD_HOVER, hover_color=CARD_SEL,
                      text_color=ACCENT_LIGHT, font=FONT_XS,
                      corner_radius=BTN_RADIUS,
                      command=lambda: self._on_edit(self._entry)).pack(side="left", padx=(0, 6))

        ctk.CTkButton(actions, text="Delete", width=68, height=28,
                      fg_color=CARD_HOVER, hover_color=DANGER,
                      text_color=DANGER, font=FONT_XS,
                      corner_radius=BTN_RADIUS,
                      command=lambda: self._confirm_delete()).pack(side="left")

    def _copy_btn(self, parent, label: str, action: Callable, col: int):
        btn = ctk.CTkButton(
            parent, text=label, width=130, height=26,
            fg_color=CARD_HOVER, hover_color=CARD_SEL,
            text_color=ACCENT_LIGHT, font=FONT_XS,
            corner_radius=BTN_RADIUS,
            command=lambda b=btn: self._do_copy(b, label, action),
        )
        # We need the btn reference inside the lambda — rebind:
        btn.configure(command=lambda: self._do_copy(btn, label, action))
        btn.grid(row=0, column=col, padx=(8, 0))

    def _do_copy(self, btn: ctk.CTkButton, original: str, action: Callable):
        action()
        btn.configure(text="Copied ✓", fg_color=SUCCESS, text_color="white")
        self.after(2000, lambda: btn.configure(
            text=original, fg_color=CARD_HOVER, text_color=ACCENT_LIGHT))

    def _copy(self, text: str):
        cb.copy(self._root, text)

    def _confirm_delete(self):
        dlg = ctk.CTkToplevel(self)
        dlg.title("Delete entry")
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.configure(fg_color=SURFACE)
        set_icon(dlg)

        center_over(dlg, self._root)
        ctk.CTkLabel(dlg, text="Delete this entry?", font=(FF, 15, "bold"),
                     text_color=TEXT).pack(pady=(28, 4))
        ctk.CTkLabel(dlg, text="This cannot be undone.", font=FONT_XS,
                     text_color=SUBTEXT).pack()

        btns = ctk.CTkFrame(dlg, fg_color="transparent")
        btns.pack(pady=20)
        ctk.CTkButton(btns, text="Cancel", width=100, height=36,
                      fg_color=CARD, hover_color=CARD_HOVER,
                      text_color=TEXT, corner_radius=BTN_RADIUS,
                      command=dlg.destroy).pack(side="left", padx=8)
        ctk.CTkButton(btns, text="Delete", width=100, height=36,
                      fg_color=DANGER, hover_color=DANGER_HOVER,
                      text_color="white", corner_radius=BTN_RADIUS,
                      command=lambda: self._do_delete(dlg)).pack(side="left", padx=8)

    def _do_delete(self, dlg):
        dlg.destroy()
        self._vault.delete(self._entry["id"])
        self._on_refresh()


# ── Main frame ────────────────────────────────────────────────────────────────

class MainFrame(ctk.CTkFrame):
    def __init__(self, master, vault: VaultManager, on_lock: Callable):
        super().__init__(master, fg_color=BG, corner_radius=0)
        self._vault    = vault
        self._on_lock  = on_lock
        self._filter   = ""
        self._tab      = "all"          # "all" | "password" | "note"

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self._build_sidebar()
        self._build_content()
        self._refresh()

    # ── Sidebar ───────────────────────────────────────────────────────────────

    def _build_sidebar(self):
        sb = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=0, width=SIDEBAR_W)
        sb.grid(row=0, column=0, sticky="nsew")
        sb.grid_propagate(False)
        sb.grid_rowconfigure(5, weight=1)
        sb.grid_columnconfigure(0, weight=1)

        # Logo + wordmark
        logo_path = _res("assets/logo.png")
        top = ctk.CTkFrame(sb, fg_color="transparent")
        top.grid(row=0, column=0, padx=18, pady=(22, 0), sticky="ew")
        top.grid_columnconfigure(1, weight=1)

        if logo_path.exists():
            img = ctk.CTkImage(Image.open(str(logo_path)), size=(32, 32))
            ctk.CTkLabel(top, image=img, text="").grid(row=0, column=0, padx=(0, 8))
        ctk.CTkLabel(top, text="PassNook", font=(FF, 16, "bold"),
                     text_color=TEXT).grid(row=0, column=1, sticky="w")

        # Divider
        ctk.CTkFrame(sb, height=1, fg_color=BORDER).grid(
            row=1, column=0, sticky="ew", padx=14, pady=(18, 12))

        # Nav buttons
        nav = ctk.CTkFrame(sb, fg_color="transparent")
        nav.grid(row=2, column=0, sticky="ew", padx=10)
        nav.grid_columnconfigure(0, weight=1)

        self._nav_btns = {}
        tabs = [("all", "🗂  All Entries"), ("password", "🔑  Passwords"),
                ("note", "📋  Secure Notes")]
        for i, (key, label) in enumerate(tabs):
            btn = ctk.CTkButton(
                nav, text=label, anchor="w", height=36,
                font=FONT_SM, corner_radius=BTN_RADIUS,
                fg_color=ACCENT if key == self._tab else "transparent",
                hover_color=CARD_HOVER if key != self._tab else ACCENT_HOVER,
                text_color=TEXT,
                command=lambda k=key: self._switch_tab(k),
            )
            btn.grid(row=i, column=0, sticky="ew", pady=2)
            self._nav_btns[key] = btn

        # Spacer
        ctk.CTkFrame(sb, fg_color="transparent").grid(row=3, column=0)

        # Entry count
        self._count_lbl = ctk.CTkLabel(sb, text="", font=FONT_XS, text_color=SUBTEXT)
        self._count_lbl.grid(row=4, column=0, padx=18, pady=(16, 0), sticky="w")

        # Divider
        ctk.CTkFrame(sb, height=1, fg_color=BORDER).grid(
            row=5, column=0, sticky="ews", padx=14, pady=(0, 12))

        # Bottom buttons
        bottom = ctk.CTkFrame(sb, fg_color="transparent")
        bottom.grid(row=6, column=0, sticky="ew", padx=10, pady=(0, 18))
        bottom.grid_columnconfigure(0, weight=1)

        self._sb_btn(bottom, "🔑  Generator", 0, self._open_generator)
        self._sb_btn(bottom, "📤  Backup",    1, self._export_backup)
        self._sb_btn(bottom, "📥  Restore",   2, self._restore_backup)
        self._sb_btn(bottom, "📋  Import CSV",3, self._import_csv)
        self._sb_btn(bottom, "ℹ️  About",     4, self._open_about)
        self._sb_btn(bottom, "🔒  Lock",      5, self._on_lock,
                     fg=DANGER, hover=DANGER_HOVER)

    def _sb_btn(self, parent, label, row, cmd, fg="transparent", hover=CARD_HOVER):
        ctk.CTkButton(
            parent, text=label, anchor="w", height=34,
            font=FONT_SM, corner_radius=BTN_RADIUS,
            fg_color=fg, hover_color=hover, text_color=TEXT,
            command=cmd,
        ).grid(row=row, column=0, sticky="ew", pady=2)

    # ── Content area ──────────────────────────────────────────────────────────

    def _build_content(self):
        content = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        content.grid(row=0, column=1, sticky="nsew", padx=(1, 0))
        content.grid_rowconfigure(1, weight=1)
        content.grid_columnconfigure(0, weight=1)

        # ── Top bar ───────────────────────────────────────────────────────────
        topbar = ctk.CTkFrame(content, fg_color=BG, corner_radius=0)
        topbar.grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 10))
        topbar.grid_columnconfigure(0, weight=1)

        self._search_var = ctk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._refresh())

        ctk.CTkEntry(
            topbar, textvariable=self._search_var,
            placeholder_text="🔍  Search entries…",
            fg_color=INPUT_BG, border_color=BORDER,
            text_color=TEXT, placeholder_text_color=PLACEHOLDER,
            height=40, corner_radius=INPUT_RADIUS, font=FONT_SM,
        ).grid(row=0, column=0, sticky="ew")

        ctk.CTkButton(
            topbar, text="+ Add Entry", width=110, height=40,
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
            text_color="white", font=(FF, 13, "bold"),
            corner_radius=BTN_RADIUS,
            command=self._add_entry,
        ).grid(row=0, column=1, padx=(10, 0))

        # ── Scrollable list ───────────────────────────────────────────────────
        self._scroll = ctk.CTkScrollableFrame(
            content, fg_color=BG, scrollbar_button_color=CARD,
            scrollbar_button_hover_color=CARD_HOVER,
        )
        self._scroll.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 16))
        self._scroll.grid_columnconfigure(0, weight=1)

    # ── Entry list ────────────────────────────────────────────────────────────

    def _refresh(self):
        for w in self._scroll.winfo_children():
            w.destroy()

        query   = self._search_var.get().lower().strip()
        entries = self._vault.entries(
            kind=None if self._tab == "all" else self._tab
        )

        if query:
            entries = [
                e for e in entries
                if query in e.get("title", "").lower()
                or query in e.get("username", "").lower()
                or query in e.get("url", "").lower()
                or query in e.get("content", "").lower()
            ]

        entries.sort(key=lambda e: e.get("title", "").lower())

        if not entries:
            self._show_empty(query)
        else:
            for i, entry in enumerate(entries):
                card = EntryCard(
                    self._scroll, entry, self._vault,
                    self.winfo_toplevel(),
                    on_edit=self._edit_entry,
                    on_delete=lambda _: self._refresh(),
                    on_refresh=self._refresh,
                )
                card.grid(row=i, column=0, sticky="ew", pady=(0, 8))

        # Update count label
        noun = "entry" if len(entries) == 1 else "entries"
        self._count_lbl.configure(text=f"{len(entries)} {noun}")

    def _show_empty(self, query: str):
        msg_frame = ctk.CTkFrame(self._scroll, fg_color="transparent")
        msg_frame.grid(row=0, column=0, sticky="nsew", pady=60)

        if query:
            icon, title, sub = "🔍", "No results", f'Nothing matched "{query}"'
        elif self._tab == "note":
            icon, title, sub = "📋", "No secure notes yet", "Click '+ Add Entry' to create one"
        elif self._tab == "password":
            icon, title, sub = "🔑", "No passwords yet", "Click '+ Add Entry' to save one"
        else:
            icon, title, sub = "🗂", "Your vault is empty", "Click '+ Add Entry' to get started"

        ctk.CTkLabel(msg_frame, text=icon, font=(FF, 40)).pack()
        ctk.CTkLabel(msg_frame, text=title, font=(FF, 18, "bold"),
                     text_color=TEXT).pack(pady=(8, 2))
        ctk.CTkLabel(msg_frame, text=sub, font=FONT_SM,
                     text_color=SUBTEXT).pack()

    # ── Tab switching ─────────────────────────────────────────────────────────

    def _switch_tab(self, key: str):
        self._tab = key
        for k, btn in self._nav_btns.items():
            btn.configure(
                fg_color=ACCENT if k == key else "transparent",
                hover_color=ACCENT_HOVER if k == key else CARD_HOVER,
            )
        self._refresh()

    # ── CRUD helpers ──────────────────────────────────────────────────────────

    def _add_entry(self):
        from ui.entry_dialog import EntryDialog
        EntryDialog(self.winfo_toplevel(), self._vault,
                    default_type=self._tab if self._tab != "all" else "password",
                    on_save=self._refresh)

    def _edit_entry(self, entry: dict):
        from ui.entry_dialog import EntryDialog
        EntryDialog(self.winfo_toplevel(), self._vault,
                    entry=entry, on_save=self._refresh)

    # ── Generator ─────────────────────────────────────────────────────────────

    def _open_about(self):
        from ui.about_dialog import AboutDialog
        AboutDialog(self.winfo_toplevel())

    def _open_generator(self):
        from ui.generator_dialog import GeneratorDialog
        GeneratorDialog(self.winfo_toplevel())

    # ── Backup / Restore ──────────────────────────────────────────────────────

    def _export_backup(self):
        from tkinter import filedialog, messagebox
        path = filedialog.asksaveasfilename(
            title="Export backup",
            defaultextension=".passnook",
            filetypes=[("PassNook backup", "*.passnook"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            self._vault.export_backup(path)
            messagebox.showinfo("Backup saved", f"Backup saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Backup failed", str(e))

    def _import_csv(self):
        from tkinter import filedialog, messagebox
        import csv

        path = filedialog.askopenfilename(
            title="Import passwords from CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not path:
            return

        try:
            with open(path, newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                headers = [h.lower().strip() for h in (reader.fieldnames or [])]
        except Exception as e:
            messagebox.showerror("Import failed", f"Could not read file:\n{e}")
            return

        if not rows:
            messagebox.showinfo("Nothing to import", "The CSV file is empty.")
            return

        # ── Column detection — handles Chrome, Bitwarden, LastPass, 1Password, KeePass ──
        def _col(row, *candidates):
            for c in candidates:
                for k in row:
                    if k.lower().strip() == c:
                        return row[k].strip()
            return ""

        imported = 0
        skipped  = 0
        for row in rows:
            title = _col(row, "name", "title", "account", "label", "site")
            url   = _col(row, "url", "login_uri", "website", "web site", "uri")
            user  = _col(row, "username", "login name", "login_username", "user", "email", "login")
            pw    = _col(row, "password", "login_password", "pass")
            notes = _col(row, "notes", "note", "extra", "comment", "comments")

            if not title and url:
                # Fall back to domain as title
                title = url.split("/")[2] if "//" in url else url
            if not title:
                skipped += 1
                continue

            self._vault.add({
                "type":     "password",
                "title":    title,
                "url":      url,
                "username": user,
                "password": pw,
                "notes":    notes,
                "content":  "",
            })
            imported += 1

        self._refresh()
        msg = f"Imported {imported} password{'s' if imported != 1 else ''}."
        if skipped:
            msg += f"\n{skipped} row{'s' if skipped != 1 else ''} skipped (no name/title found)."
        messagebox.showinfo("Import complete", msg)

    def _restore_backup(self):
        from tkinter import filedialog, messagebox, simpledialog
        path = filedialog.askopenfilename(
            title="Select backup file",
            filetypes=[("PassNook backup", "*.passnook"), ("All files", "*.*")],
        )
        if not path:
            return
        pw = simpledialog.askstring(
            "Master password", "Enter the master password for this backup:",
            show="*", parent=self.winfo_toplevel(),
        )
        if not pw:
            return
        try:
            self._vault.restore_backup(path, pw)
            self._refresh()
            messagebox.showinfo("Restored", "Backup restored successfully.")
        except Exception as e:
            messagebox.showerror("Restore failed", str(e))


