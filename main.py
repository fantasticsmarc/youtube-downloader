import os
import shutil
import threading
import tkinter
from tkinter import filedialog
import customtkinter
from yt_dlp import YoutubeDL

app = None

_INVALID_CHARS = '<>:"/\\|?*'


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


def _ffmpeg_location() -> str:
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError as e:
        raise RuntimeError(
            "Falta ffmpeg. Ejecuta: pip install -r requirements.txt"
        ) from e


def _get_video_info(url: str) -> dict:
    with YoutubeDL({"quiet": True, "no_warnings": True, "noplaylist": True}) as ydl:
        return ydl.extract_info(url, download=False)


def _run_download(url: str, ydl_opts: dict, directory: str, filename: str) -> None:
    outtmpl = os.path.join(directory, f"{filename}.%(ext)s")
    opts = {
        "outtmpl": outtmpl,
        "progress_hooks": [progress_hook],
        "noplaylist": True,
        **ydl_opts,
    }
    with YoutubeDL(opts) as ydl:
        ydl.download([url])


def _start_download(mode: str) -> None:
    url = link.get().strip()
    if not url:
        finishLabel.configure(text="Introduce un enlace de YouTube.", text_color="red")
        return

    directory = filedialog.askdirectory(title="Escoge una ubicación para el archivo")
    if not directory:
        return

    name = name_entry.get().strip()
    finishLabel.configure(text="Descargando...", text_color="white")
    update_progress(0)
    downloadmp4.configure(state="disabled")
    downloadmp3.configure(state="disabled")

    def worker() -> None:
        try:
            info = _get_video_info(url)
            video_title = info.get("title", "video")
            filename = safe_filename(name or video_title)

            app.after(0, lambda: title.configure(text=video_title, text_color="white"))

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
                lambda: finishLabel.configure(
                    text="¡Descarga completada!", text_color="white"
                ),
            )
        except Exception as e:
            print(e)
            app.after(
                0,
                lambda: finishLabel.configure(
                    text="Error al descargar. Comprueba el enlace e inténtalo de nuevo.",
                    text_color="red",
                ),
            )
        finally:
            app.after(0, lambda: downloadmp4.configure(state="normal"))
            app.after(0, lambda: downloadmp3.configure(state="normal"))

    threading.Thread(target=worker, daemon=True).start()


def startDownloadVideo() -> None:
    _start_download("video")


def startDownloadAudio() -> None:
    _start_download("audio")


customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

app = customtkinter.CTk()
app.geometry("720x480")
app.title("YouTube Downloader con Python")

title = customtkinter.CTkLabel(app, text="Adjunta un enlace de YouTube")
title.pack(padx=10, pady=10)

url_var = tkinter.StringVar()
link = customtkinter.CTkEntry(app, width=350, height=40, textvariable=url_var)
link.pack()

title_2 = customtkinter.CTkLabel(app, text="Escoge un nombre para el archivo")
title_2.pack(padx=10, pady=10)

name_var = tkinter.StringVar()
name_entry = customtkinter.CTkEntry(app, width=350, height=40, textvariable=name_var)
name_entry.pack()

finishLabel = customtkinter.CTkLabel(app, text="")
finishLabel.pack()

pPercentatge = customtkinter.CTkLabel(app, text="0%")
pPercentatge.pack()

progressBar = customtkinter.CTkProgressBar(app, width=400)
progressBar.set(0)
progressBar.pack(padx=10, pady=10)

downloadmp4 = customtkinter.CTkButton(app, text="Descargar Mp4", command=startDownloadVideo)
downloadmp4.pack(padx=10, pady=10)

downloadmp3 = customtkinter.CTkButton(app, text="Descargar Mp3", command=startDownloadAudio)
downloadmp3.pack(padx=10, pady=10)

app.mainloop()
