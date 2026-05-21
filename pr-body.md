## Summary
- Resolve merge conflict markers in `main.py`, `requirements.txt`, and `youtube-downloader.spec`
- English UI with clear status messages for blocked videos and browser cookie issues
- Smarter yt-dlp flow: download without cookies first; retry with Edge/Firefox/Chrome only for restriction errors
- Fix Python 3.13 error display in background threads (`lambda err=e`)
- Add window icon from `youtube-downloader.ico` (including PyInstaller `datas`)

## Test plan
- [ ] `pip install -r requirements.txt` then `python main.py`
- [ ] Download a public video (MP4 and MP3)
- [ ] Try an invalid URL and confirm a red error appears (not stuck on Downloading)
- [ ] Try a restricted video and confirm the blocked message appears
- [ ] Rebuild with PyInstaller and verify window + exe icon
