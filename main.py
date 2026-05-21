import os
import shutil
import sys
import threading
import tkinter
from tkinter import filedialog
import customtkinter
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

app = None

_INVALID_CHARS = '<>:"/\\|?*'

# Only retry with browser cookies for these (not generic "unavailable").
_COOKIE_RETRY_HINTS = (
    "restricted",
    "sign in",
    "confirm your age",
    "private video",
    "members only",
    "google workspace",
)


class DownloadFailed(Exception):
    def __init__(self, attempts: list[tuple[str | None, BaseException]]):
        self.attempts = attempts
        super().__init__(str(attempts[-1][1]) if attempts else "Unknown error")


def _resource_path(filename: str) -> str:
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, filename)


def safe_filename(name: str) -> str:
    cleaned = "".join("_" if c in _INVALID_CHARS else c for c in name).strip()
    return cleaned or "video"


def update_progress(percent: float) -> None:
    progressBar.set(percent)
    pPercentatge.configure(text=f"{int(percent * 100)}%")


def progress_hook(d: dict) -> None:
    if d["status"] != "downloading":
        return
    total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
    downloaded = d.get("downloaded_bytes", 0)
    if total > 0:
        app.after(0, lambda p=downloaded / total: update_progress(p))


def _set_status(text: str, color: str = "white") -> None:
    finishLabel.configure(text=text, text_color=color)


def _ffmpeg_location() -> str:
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError as e:
        raise RuntimeError(
            "ffmpeg is missing. Run: pip install -r requirements.txt"
        ) from e


def _browser_label(browser: tuple[str, ...] | None) -> str:
    if browser is None:
        return "no session"
    return browser[0].capitalize()


def _is_cookie_error(exc: BaseException) -> bool:
    msg = str(exc).lower()
    return "cookie" in msg and (
        "could not copy" in msg or "permission denied" in msg
    )


def _is_video_blocked(exc: BaseException) -> bool:
    msg = str(exc).lower()
    if any(
        hint in msg
        for hint in (
            "google workspace",
            "private video",
            "members only",
            "confirm your age",
        )
    ):
        return True
    if "restricted" in msg and "unavailable" in msg:
        return True
    if "sign in" in msg and ("youtube" in msg or "unavailable" in msg):
        return True
    return False


def _needs_cookie_retry(exc: BaseException) -> bool:
    msg = str(exc).lower()
    return any(hint in msg for hint in _COOKIE_RETRY_HINTS)


def _base_ydl_opts(extra: dict | None = None) -> dict:
    opts = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
    }
    if extra:
        opts.update(extra)
    return opts


def _browsers_for_cookies() -> list[tuple[str, ...]]:
    return [("edge",), ("firefox",), ("chrome",)]


def _with_youtube_auth(url: str, action) -> None:
    """Try without cookies first; only use browser cookies for restriction errors."""
    attempts: list[tuple[str | None, BaseException]] = []

    def run(browser: tuple[str, ...] | None):
        opts = _base_ydl_opts()
        if browser is not None:
            opts["cookiesfrombrowser"] = browser
        return action(opts)

    try:
        return run(None)
    except Exception as e:
        attempts.append((_browser_label(None), e))
        if not _needs_cookie_retry(e):
            raise

    for browser in _browsers_for_cookies():
        try:
            return run(browser)
        except Exception as err:
            attempts.append((_browser_label(browser), err))
            if _is_cookie_error(err):
                continue
            if not _needs_cookie_retry(err):
                raise DownloadFailed(attempts) from err

    raise DownloadFailed(attempts)


def _friendly_error(exc: BaseException) -> tuple[str, str]:
    if isinstance(exc, DownloadFailed):
        return _message_from_attempts(exc.attempts)

    if _is_cookie_error(exc):
        return (
            "Could not read your browser session. Fully quit Chrome, Edge, and Firefox "
            "(including the system tray icon) and try again.",
            "orange",
        )
    if _is_video_blocked(exc):
        return _blocked_video_message(), "red"
    return ("Download failed. Check the link and try again.", "red")


def _blocked_video_message() -> str:
    return (
        "This video cannot be downloaded.\n\n"
        "YouTube has blocked or restricted it (work/school network, age gate, "
        "region, private video, or removed). If it does not play in your browser "
        "while logged in, downloading is not possible."
    )


def _message_from_attempts(
    attempts: list[tuple[str | None, BaseException]],
) -> tuple[str, str]:
    blocked = [e for _, e in attempts if _is_video_blocked(e)]
    cookie_errors = [e for _, e in attempts if _is_cookie_error(e)]
    first_error = attempts[0][1] if attempts else None

    if blocked and first_error and _is_video_blocked(first_error):
        extra = ""
        if cookie_errors:
            extra = (
                "\n\nNote: browser session could not be used either. "
                "Fully quit Chrome/Edge/Firefox before trying again."
            )
        return (_blocked_video_message() + extra, "red")

    if cookie_errors:
        return (
            "Could not access browser cookies. Fully quit Chrome, Edge, and Firefox "
            "and try again.",
            "orange",
        )

    if blocked:
        return (_blocked_video_message(), "red")

    last = attempts[-1][1]
    msg = str(last).lower()
    if "sign in" in msg or "confirm your age" in msg:
        return (
            "YouTube requires sign-in or age verification. Open the video in your "
            "browser while logged in, quit the browser, and try again.",
            "orange",
        )

    return ("Download failed. Check the link and try again.", "red")


def _get_video_info(url: str) -> dict:
    def action(opts: dict) -> dict:
        with YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=False)

    return _with_youtube_auth(url, action)


def _run_download(url: str, ydl_opts: dict, directory: str, filename: str) -> None:
    outtmpl = os.path.join(directory, f"{filename}.%(ext)s")

    def action(opts: dict) -> None:
        download_opts = {
            **opts,
            "outtmpl": outtmpl,
            "progress_hooks": [progress_hook],
            "noplaylist": True,
            **ydl_opts,
        }
        with YoutubeDL(download_opts) as ydl:
            ydl.download([url])

    _with_youtube_auth(url, action)


def _enable_buttons() -> None:
    downloadmp4.configure(state="normal")
    downloadmp3.configure(state="normal")


def _disable_buttons() -> None:
    downloadmp4.configure(state="disabled")
    downloadmp3.configure(state="disabled")


def _show_error(exc: BaseException) -> None:
    print(exc)
    text, color = _friendly_error(exc)
    _set_status(text, color)


def _start_download(mode: str) -> None:
    url = link.get().strip()
    if not url:
        _set_status("Enter a YouTube link.", "red")
        return

    directory = filedialog.askdirectory(title="Choose a folder to save the file")
    if not directory:
        return

    name = name_entry.get().strip()
    _set_status("Downloading...", "white")
    update_progress(0)
    _disable_buttons()

    def worker() -> None:
        try:
            info = _get_video_info(url)
            video_title = info.get("title", "video")
            filename = safe_filename(name or video_title)

            app.after(
                0,
                lambda t=video_title: title.configure(text=t, text_color="white"),
            )

            if mode == "video":
                opts = {"format": "best[ext=mp4]/best"}
            else:
                opts = {
                    "format": "bestaudio/best",
                    "ffmpeg_location": _ffmpeg_location(),
                    "postprocessors": [
                        {
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "mp3",
                            "preferredquality": "192",
                        }
                    ],
                }

            _run_download(url, opts, directory, filename)

            app.after(
                0,
                lambda: _set_status("Download complete!", "white"),
            )
        except Exception as e:
            app.after(0, lambda err=e: _show_error(err))
        finally:
            app.after(0, _enable_buttons)

    threading.Thread(target=worker, daemon=True).start()


def startDownloadVideo() -> None:
    _start_download("video")


def startDownloadAudio() -> None:
    _start_download("audio")


customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

app = customtkinter.CTk()
app.geometry("720x520")
app.title("YouTube Downloader")

_icon_path = _resource_path("youtube-downloader.ico")
if os.path.isfile(_icon_path):
    app.iconbitmap(_icon_path)

title = customtkinter.CTkLabel(app, text="Paste a YouTube link")
title.pack(padx=10, pady=10)

url_var = tkinter.StringVar()
link = customtkinter.CTkEntry(app, width=350, height=40, textvariable=url_var)
link.pack()

title_2 = customtkinter.CTkLabel(app, text="Choose a filename for the file")
title_2.pack(padx=10, pady=10)

name_var = tkinter.StringVar()
name_entry = customtkinter.CTkEntry(app, width=350, height=40, textvariable=name_var)
name_entry.pack()

finishLabel = customtkinter.CTkLabel(
    app,
    text="",
    wraplength=640,
    justify="left",
)
finishLabel.pack(padx=20, pady=10)

pPercentatge = customtkinter.CTkLabel(app, text="0%")
pPercentatge.pack()

progressBar = customtkinter.CTkProgressBar(app, width=400)
progressBar.set(0)
progressBar.pack(padx=10, pady=10)

downloadmp4 = customtkinter.CTkButton(app, text="Download MP4", command=startDownloadVideo)
downloadmp4.pack(padx=10, pady=10)

downloadmp3 = customtkinter.CTkButton(app, text="Download MP3", command=startDownloadAudio)
downloadmp3.pack(padx=10, pady=10)

app.mainloop()
