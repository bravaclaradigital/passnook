# PassNook — User Guide

> **PassNook v1.0.0** · Free, local, encrypted password manager for Windows

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [The Master Password](#the-master-password)
3. [Adding Entries](#adding-entries)
4. [Secure Notes](#secure-notes)
5. [Searching and Filtering](#searching-and-filtering)
6. [Copying Credentials](#copying-credentials)
7. [Password Generator](#password-generator)
8. [Importing from CSV](#importing-from-csv)
9. [Backup and Restore](#backup-and-restore)
10. [Auto-Lock](#auto-lock)
11. [System Tray](#system-tray)
12. [Security Details](#security-details)
13. [Data Locations](#data-locations)
14. [Running from Source](#running-from-source)

---

## Getting Started

1. Download `PassNook.exe` from the [Releases page](https://github.com/bravaclaradigital/passnook/releases).
2. Run it — no installation required. Windows may show a SmartScreen warning the first time; click **More info → Run anyway**.
3. On first launch, create a vault password. Choose something strong — it encrypts everything and is **never stored**.
4. Start adding passwords and secure notes.

---

## The Master Password

Your master password is the single key that encrypts and decrypts your entire vault.

- **Never stored anywhere** — not in the vault file, not in the registry, nowhere.
- Derives an encryption key using PBKDF2-SHA256 with 390,000 iterations and a random salt.
- If you forget it, your data cannot be recovered. There is no reset.
- The vault automatically locks after **30 minutes of idle**.

---

## Adding Entries

Click **+ Add Entry** to open the entry dialog. Select the type at the top:

### Password entry

| Field | Required | Description |
|---|---|---|
| **Site name** | Yes | Label for this entry (e.g. "Google") |
| **URL** | No | The website address |
| **Username / Email** | Yes | Your login username or email |
| **Password** | Yes | Your password — stored encrypted |
| **Notes** | No | Any additional notes — also encrypted |

Click **Save Entry** to encrypt and write to your vault.

Use the **Generate** button next to the password field to open the password generator and fill the field automatically.

---

## Secure Notes

Switch the type toggle to **Secure Note** in the entry dialog to store any sensitive text — Wi-Fi passwords, PINs, recovery codes, or anything else that isn't a website login.

| Field | Required | Description |
|---|---|---|
| **Note title** | Yes | A label for this note |
| **Content** | Yes | The sensitive text — stored encrypted |

---

## Searching and Filtering

- Use the **search bar** at the top to filter entries by title, username, or URL in real time.
- Use the sidebar tabs — **All Entries**, **Passwords**, **Secure Notes** — to filter by type.

---

## Copying Credentials

Each entry in the list shows **Copy** buttons for the username and password.

- Click **Copy** next to the username or password to copy it to the clipboard.
- The clipboard is **automatically cleared after 30 seconds**.
- The button briefly shows "Copied ✓" as confirmation.

---

## Password Generator

Open the generator from the **sidebar** or from the **Generate** button inside the entry dialog.

| Control | Description |
|---|---|
| **Length slider** | Set password length from 8 to 64 characters |
| **Uppercase A–Z** | Include uppercase letters |
| **Lowercase a–z** | Include lowercase letters |
| **Numbers 0–9** | Include digits |
| **Symbols !@#…** | Include special characters |
| **↻ Regenerate** | Generate a new password with the same settings |
| **Copy** | Copy the current password to clipboard |
| **Use this password** | Fill the password field in the entry dialog (only available when opened from an entry) |

A strength indicator shows the quality of the generated password.

---

## Importing from CSV

Click **Import CSV** in the sidebar to import passwords from another password manager.

PassNook auto-detects the format from the CSV header row:

| Source | Detected columns |
|---|---|
| **Chrome / Edge** | `name, url, username, password` |
| **Bitwarden** | `name, login_uri, login_username, login_password, notes` |
| **LastPass** | `name, url, username, password, extra` |
| **1Password** | `title, url, username, password, notes` |
| **KeePass** | `account, web site, login name, password, comments` |

Any CSV with recognisable `name`/`title`, `username`, and `password` columns will be detected automatically.

After import, a summary shows how many entries were added and how many were skipped (duplicates or missing required fields).

---

## Backup and Restore

### Backup

Click **Backup** in the sidebar to export an encrypted `.passnook` backup file. The backup is encrypted using a separate Fernet key derived from your master password — it cannot be opened without it.

### Restore

Click **Restore** in the sidebar to import a `.passnook` backup file. This merges entries from the backup into your current vault. Existing entries are not overwritten.

---

## Auto-Lock

PassNook automatically locks the vault after **30 minutes of system idle** (no keyboard or mouse input). When locked, you must re-enter your master password to access your vault.

You can also lock immediately at any time using the **Lock** button at the bottom of the sidebar.

---

## System Tray

PassNook runs in the system tray from the moment it launches.

- **Closing the window** hides it to the tray — PassNook keeps running in the background.
- **Right-click the tray icon** to show the window or quit.
- **Launching a second copy** of PassNook brings the existing window to the front.

---

## Security Details

| Layer | Detail |
|---|---|
| Key derivation | PBKDF2-SHA256, 390,000 iterations, random 32-byte salt |
| Encryption | Fernet — AES-128-CBC + HMAC-SHA256 |
| Vault writes | Atomic — write to `.tmp`, verify, then rename |
| Backup files | Encrypted with a separate Fernet key derived from master password |
| Clipboard | Auto-cleared after 30 seconds |
| Master password | Never stored. Not recoverable if forgotten. |

---

## Data Locations

| File | Path |
|---|---|
| Vault | `%APPDATA%\PassNook\vault.pn` |

---

## Running from Source

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

*Built and maintained by [Brava IT Services](https://bravait.com)*
