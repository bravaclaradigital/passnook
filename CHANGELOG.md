# Changelog

All notable changes to PassNook will be documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [1.0.0] — 2026-03-22

Initial public release.

### Added

- Master password protected vault using PBKDF2-SHA256 (390,000 iterations) + Fernet AES-128-CBC
- Store website passwords and secure notes in a single encrypted vault file
- Built-in password generator with configurable length, uppercase, lowercase, numbers, and symbols
- Password strength indicator on generator and entry dialog
- One-click copy for username and password — clipboard clears automatically after 30 seconds
- Show/hide password toggle in entry dialog
- CSV import — auto-detects format from Chrome, Bitwarden, LastPass, 1Password, and KeePass exports
- Encrypted backup export and restore (`.passnook` format)
- Atomic vault writes — write to `.tmp`, verify, rename; prevents corruption on crash
- Auto-lock after 30 minutes of idle
- System tray — close hides to tray; right-click to show or quit
- Single-instance enforcement — launching a second copy brings the existing window to front
- PassNook padlock icon for exe and system tray
- About dialog with Brava IT Services branding
- Window auto-sizes to fit screen resolution

---

[1.0.0]: https://github.com/bravaclaradigital/passnook/releases/tag/v1.0.0
