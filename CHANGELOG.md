# Changelog

All notable changes to this project will be documented here.

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