# PyInstaller spec for YouTube Downloader
a=Analysis(['main.py'], hiddenimports=['pytube','customtkinter'])
exe=EXE(a.pure,a.scripts,name='youtube-downloader',console=False)
