"""
PassNook — Design tokens
All colours, fonts, and sizing constants in one place.
"""

# ── Palette ───────────────────────────────────────────────────────────────────

BG            = "#12101a"   # Main window / deepest background
SURFACE       = "#1c1929"   # Sidebar
CARD          = "#251f38"   # Entry card default
CARD_HOVER    = "#2e2847"   # Card on hover
CARD_SEL      = "#332c50"   # Card selected / pressed

ACCENT        = "#7c3aed"   # Violet — primary CTA
ACCENT_HOVER  = "#6d28d9"
ACCENT_LIGHT  = "#a78bfa"   # Labels, icons, highlights

SUCCESS       = "#10b981"   # Green — copy confirmed, unlock
SUCCESS_HOVER = "#059669"

WARN          = "#f59e0b"   # Amber

DANGER        = "#ef4444"   # Red — delete
DANGER_HOVER  = "#dc2626"

TEXT          = "#f0ebff"   # Primary text (near-white, slight purple cast)
SUBTEXT       = "#8b7fad"   # Secondary / muted
PLACEHOLDER   = "#4a4270"   # Input placeholder

BORDER        = "#2d2547"   # Subtle border / divider
INPUT_BG      = "#1e1830"   # Text entry background

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
    "#7c3aed", "#2563eb", "#059669", "#d97706",
    "#dc2626", "#0891b2", "#4338ca", "#c026d3",
    "#65a30d", "#b45309",
]


def site_color(name: str) -> str:
    return ICON_PALETTE[sum(ord(c) for c in name) % len(ICON_PALETTE)] if name else ICON_PALETTE[0]
