<img src="assets/logo.png" width="64" alt="PassNook" />

# PassNook

[![Release](https://img.shields.io/github/v/release/bravaclaradigital/passnook?style=flat-square&color=7c3aed)](https://github.com/bravaclaradigital/passnook/releases/latest)
[![Downloads](https://img.shields.io/github/downloads/bravaclaradigital/passnook/total?style=flat-square&color=7c3aed)](https://github.com/bravaclaradigital/passnook/releases/latest)
[![Platform](https://img.shields.io/badge/platform-Windows-informational?style=flat-square)](https://github.com/bravaclaradigital/passnook/releases/latest)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)
[![Made by Brava IT](https://img.shields.io/badge/made%20by-Brava%20IT%20Services-white?style=flat-square)](https://bravait.com)

**A free, local, encrypted password manager for Windows.**

Store website passwords and secure notes in an AES-encrypted vault on your machine. No cloud. No accounts. No telemetry.

[**Download PassNook.exe →**](https://github.com/bravaclaradigital/passnook/releases/latest/download/PassNook.exe) &nbsp;·&nbsp; [Website →](https://bravaclaradigital.github.io/passnook/)

---

## Features

- **AES-256 encryption** — vault protected by PBKDF2-SHA256 + Fernet AES-128-CBC
- **Stays local** — single encrypted file at `%APPDATA%\PassNook\vault.pn`, nothing leaves your machine
- **Passwords & secure notes** — save website logins or any sensitive text as a secure note
- **Built-in password generator** — configurable length, uppercase, lowercase, numbers, symbols
- **One-click copy** — copy username or password with one click; clipboard clears automatically after 30 seconds
- **CSV import** — import from Chrome, Bitwarden, LastPass, 1Password, KeePass exports
- **Encrypted backups** — export/restore `.passnook` backup files
- **Auto-lock** — locks after 30 minutes idle
- **System tray** — close hides to tray; right-click to show or quit

---

## Download

| Platform | Link |
|---|---|
| Windows 10/11 (64-bit) | [**PassNook.exe**](https://github.com/bravaclaradigital/passnook/releases/latest/download/PassNook.exe) |

No installer. No admin rights required. Download, run, done.

---

## CSV Import

PassNook auto-detects the column format from the CSV header row:

| Source | Detected columns |
|---|---|
| **Chrome / Edge** | `name, url, username, password` |
| **Bitwarden** | `name, login_uri, login_username, login_password, notes` |
| **LastPass** | `name, url, username, password, extra` |
| **1Password** | `title, url, username, password, notes` |
| **KeePass** | `account, web site, login name, password, comments` |

Any CSV with recognisable `name`/`title`, `username`, and `password` columns will be detected automatically.

---

## Security

| Layer | Detail |
|---|---|
| Key derivation | PBKDF2-SHA256, 390,000 iterations, random 32-byte salt |
| Encryption | Fernet — AES-128-CBC + HMAC-SHA256 |
| Vault writes | Atomic — write to `.tmp`, verify, then rename |
| Backup files | Encrypted with a separate Fernet key derived from master password |
| Master password | Never stored. Not recoverable if forgotten. |

---

## Running from Source

> **Windows only.** PassNook uses Windows-specific APIs (`ctypes.windll`) for idle detection and system tray integration.

```bash
git clone https://github.com/bravaclaradigital/passnook.git
cd passnook
pip install -r requirements.txt
python make_assets.py
python passnook.py
```

**Building the exe:**

```bash
python make_assets.py
python -m PyInstaller PassNook.spec --noconfirm
# Output: dist\PassNook.exe
```

Requires Python 3.11+ and PyInstaller. Must be built on Windows.

---

## Data Locations

| File | Path |
|---|---|
| Vault | `%APPDATA%\PassNook\vault.pn` |

---

## Contributing

Bug reports and pull requests welcome at [github.com/bravaclaradigital/passnook/issues](https://github.com/bravaclaradigital/passnook/issues).

---

## License

MIT — see [LICENSE](LICENSE).

---

*Built and maintained by [Brava IT Services](https://bravait.com) — IT consulting for infrastructure, security, and technology strategy.*
