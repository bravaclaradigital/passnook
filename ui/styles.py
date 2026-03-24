"""
PassNook — Design tokens
All colours, fonts, and sizing constants in one place.
"""

# ── Palette ───────────────────────────────────────────────────────────────────

BG            = "#0f172a"   # Main window / deepest background
SURFACE       = "#111827"   # Sidebar / dialogs
CARD          = "#1e293b"   # Entry card default
CARD_HOVER    = "#1e3a5f"   # Card on hover
CARD_SEL      = "#1a3050"   # Card selected / pressed

ACCENT        = "#0284c7"   # Blue — primary CTA
ACCENT_HOVER  = "#0369a1"
ACCENT_LIGHT  = "#38bdf8"   # Labels, links, highlights

SUCCESS       = "#10b981"   # Green — copy confirmed, unlock
SUCCESS_HOVER = "#059669"

WARN          = "#f59e0b"   # Amber

DANGER        = "#ef4444"   # Red — delete
DANGER_HOVER  = "#dc2626"

TEXT          = "#e2e8f0"   # Primary text (near-white, neutral)
SUBTEXT       = "#94a3b8"   # Secondary / muted
PLACEHOLDER   = "#475569"   # Input placeholder

BORDER        = "#1e3054"   # Subtle border / divider
INPUT_BG      = "#0f172a"   # Text entry background

# Note-type accent
NOTE_ACCENT   = "#0891b2"   # Cyan — secure notes
NOTE_HOVER    = "#0e7490"

# ── Fonts ─────────────────────────────────────────────────────────────────────

FF = "Segoe UI"

FONT_XL   = (FF, 30, "bold")
FONT_LG   = (FF, 20, "bold")
FONT_MD   = (FF, 15, "bold")
FONT_SM   = (FF, 13, "normal")
FONT_XS   = (FF, 11, "normal")
FONT_MONO = ("Consolas", 13, "normal")

# ── Layout ────────────────────────────────────────────────────────────────────

SIDEBAR_W   = 220
CARD_RADIUS = 12
BTN_RADIUS  = 8
INPUT_RADIUS = 8

# Icon palette — used to colour entry initials
ICON_PALETTE = [
    "#0284c7", "#2563eb", "#059669", "#d97706",
    "#dc2626", "#0891b2", "#4338ca", "#0369a1",
    "#65a30d", "#b45309",
]


def site_color(name: str) -> str:
    return ICON_PALETTE[sum(ord(c) for c in name) % len(ICON_PALETTE)] if name else ICON_PALETTE[0]
