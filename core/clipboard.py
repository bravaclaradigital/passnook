"""
PassNook — Clipboard helper
Copies text and auto-clears after a timeout (default 30 s).
"""

import threading

_timer: threading.Timer | None = None


def copy(root, text: str, clear_after: int = 30) -> None:
    """Copy *text* to clipboard; schedule a clear after *clear_after* seconds."""
    global _timer

    if _timer is not None:
        _timer.cancel()
        _timer = None

    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()

    def _clear():
        try:
            current = root.clipboard_get()
            if current == text:
                root.clipboard_clear()
                root.update()
        except Exception:
            pass

    _timer = threading.Timer(clear_after, _clear)
    _timer.daemon = True
    _timer.start()
