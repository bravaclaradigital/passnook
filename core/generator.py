"""
PassNook — Password generator
"""

import secrets
import string
import re


_SYMBOLS = "!@#$%^&*()-_=+[]{}|;:,.<>?"


def generate(
    length: int = 16,
    uppercase: bool = True,
    lowercase: bool = True,
    numbers: bool = True,
    symbols: bool = True,
) -> str:
    charset = ""
    guaranteed = []

    if uppercase:
        charset += string.ascii_uppercase
        guaranteed.append(secrets.choice(string.ascii_uppercase))
    if lowercase:
        charset += string.ascii_lowercase
        guaranteed.append(secrets.choice(string.ascii_lowercase))
    if numbers:
        charset += string.digits
        guaranteed.append(secrets.choice(string.digits))
    if symbols:
        charset += _SYMBOLS
        guaranteed.append(secrets.choice(_SYMBOLS))

    if not charset:
        charset = string.ascii_lowercase
        guaranteed = [secrets.choice(string.ascii_lowercase)]

    remaining = max(0, length - len(guaranteed))
    pool = guaranteed + [secrets.choice(charset) for _ in range(remaining)]

    # Fisher-Yates shuffle via secrets
    for i in range(len(pool) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        pool[i], pool[j] = pool[j], pool[i]

    return "".join(pool)


def strength(password: str) -> tuple[int, str, str]:
    """Return (score 0-4, label, hex_color)."""
    if not password:
        return 0, "", "#2d2547"

    score = 0
    if len(password) >= 8:  score += 1
    if len(password) >= 12: score += 1
    if re.search(r"[A-Z]", password) and re.search(r"[a-z]", password): score += 1
    if re.search(r"\d", password):   score += 1
    if re.search(r"[^a-zA-Z0-9]", password): score += 1

    score = min(score, 4)
    labels = ["Very Weak", "Weak", "Fair", "Strong", "Very Strong"]
    colors = ["#ef4444", "#f97316", "#f59e0b", "#22c55e", "#10b981"]
    return score, labels[score], colors[score]
