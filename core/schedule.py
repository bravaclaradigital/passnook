"""
PassNook — Scheduled backup manager
Handles config persistence and backup-due logic.

Config file: %APPDATA%/PassNook/schedule.json
"""

from __future__ import annotations

import json
import shutil
import calendar
from datetime import datetime, timedelta
from pathlib import Path

from core.vault import APPDATA, VAULT_PATH

SCHEDULE_PATH = APPDATA / "schedule.json"

DEFAULTS: dict = {
    "enabled":      False,
    "frequency":    "daily",    # "daily" | "weekly" | "monthly"
    "hour":         10,         # 0–23
    "day_of_week":  0,          # 0=Mon … 6=Sun  (weekly only)
    "day_of_month": 1,          # 1–28           (monthly only)
    "folder":       str(Path.home() / "Documents" / "PassNook Backups"),
    "keep":         10,         # number of backups to keep
    "last_backup":  None,       # ISO datetime string of last run
}


# ── Persistence ───────────────────────────────────────────────────────────────

def load() -> dict:
    if SCHEDULE_PATH.exists():
        try:
            data = json.loads(SCHEDULE_PATH.read_text("utf-8"))
            return {**DEFAULTS, **data}
        except Exception:
            pass
    return dict(DEFAULTS)


def save(cfg: dict) -> None:
    SCHEDULE_PATH.write_text(json.dumps(cfg, indent=2), "utf-8")


# ── Scheduling logic ──────────────────────────────────────────────────────────

def _next_due(cfg: dict) -> datetime | None:
    """Return the next datetime a backup should run, or None if disabled."""
    if not cfg.get("enabled"):
        return None

    last = cfg.get("last_backup")
    hour = int(cfg.get("hour", 10))

    if last is None:
        return datetime.min   # never backed up → due immediately

    last_dt = datetime.fromisoformat(last)
    freq    = cfg.get("frequency", "daily")

    if freq == "daily":
        candidate = last_dt.replace(hour=hour, minute=0, second=0, microsecond=0)
        if candidate <= last_dt:
            candidate += timedelta(days=1)
        return candidate

    if freq == "weekly":
        dow        = int(cfg.get("day_of_week", 0))
        days_ahead = (dow - last_dt.weekday()) % 7 or 7
        base       = last_dt + timedelta(days=days_ahead)
        return base.replace(hour=hour, minute=0, second=0, microsecond=0)

    # monthly
    dom   = int(cfg.get("day_of_month", 1))
    year  = last_dt.year
    month = last_dt.month + 1
    if month > 12:
        month, year = 1, year + 1
    dom = min(dom, calendar.monthrange(year, month)[1])
    return datetime(year, month, dom, hour, 0, 0)


def is_due(cfg: dict) -> bool:
    due = _next_due(cfg)
    if due is None:
        return False
    return datetime.now() >= due


# ── Execution ─────────────────────────────────────────────────────────────────

def run_backup(cfg: dict) -> str:
    """
    Copy the vault to the configured folder with a timestamped filename.
    Prunes old backups so only cfg['keep'] most recent are kept.
    Returns the path of the new backup file.
    """
    if not VAULT_PATH.exists():
        raise FileNotFoundError("Vault file not found — nothing to back up.")

    folder = Path(cfg["folder"])
    folder.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    dest  = folder / f"passnook-backup-{stamp}.passnook"
    shutil.copy2(str(VAULT_PATH), str(dest))

    # Prune: keep only the N most recent
    keep    = max(1, int(cfg.get("keep", 10)))
    backups = sorted(folder.glob("passnook-backup-*.passnook"))
    for old in backups[:-keep]:
        try:
            old.unlink()
        except Exception:
            pass

    return str(dest)
