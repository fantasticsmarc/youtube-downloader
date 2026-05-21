# Changelog

All notable changes to this project will be documented here.

## [2.1.0] - 2026-05-21

### Fixed
- Unresolved Git merge conflict markers in `main.py`, `requirements.txt`, and `youtube-downloader.spec` that caused syntax errors
- Restricted or age-gated videos now retry with browser cookies (Edge, Firefox, Chrome) when anonymous download fails
- Browser cookie read failures (e.g. Chrome open on Windows) skip to the next browser instead of stopping silently

### Added
- Pre-download availability check before the folder picker opens
- GUI status messages for videos that cannot be downloaded (blocked, private, region, or network restrictions)
- Separate GUI hints for browser cookie issues (fully quit browsers and retry)
- `DownloadFailed` exception to aggregate retry attempts and drive user-facing messages

### Changed
- Entire UI translated to English (labels, dialogs, status text, and error messages)
- Chrome moved to last in the cookie retry order to reduce Windows cookie database lock errors
- Window height increased to `720x520` and status label uses `wraplength=640` for multiline errors
- Folder picker only appears after the video passes the availability check

## [2.0.0] - 2026-05-19

### Fixed
- HTTP 400 Bad Request errors when downloading videos by replacing `pytube` with `yt-dlp`
- MP3 downloads now produce valid `.mp3` files via `imageio-ffmpeg` (bundled ffmpeg)
- Invalid Windows filename characters are sanitized before saving files
- UI freezing during downloads by running downloads on a background thread

### Changed
- Rewrote `main.py` to use `yt-dlp` instead of `pytube`
- Updated `requirements.txt` to include `customtkinter`, `yt-dlp`, and `imageio-ffmpeg`
- Updated `youtube-downloader.spec` for PyInstaller with required hidden imports and custom icon
- Build output moved from `build/` and `dist/` to `release/YouTube-Downloader/`
- Executable renamed to `YouTube-Downloader.exe`

### Removed
- `pytube` dependency (no longer compatible with YouTube)

## [1.0.0] - 2026-04-14

### Added
- Initial professional structure
- README, requirements, gitignore
- CONTRIBUTING and CHANGELOG files
