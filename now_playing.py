import win32gui, win32process, win32api, win32con
import re
from pywintypes import error as PyWinError
import urllib.request
from bs4 import BeautifulSoup

spotify = True
yt_chrome = True


def get_song_info():
    def enumHandler(hwnd, result):
        threadpid, procpid = win32process.GetWindowThreadProcessId(hwnd)
        try:
            mypyproc = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, False, procpid)
            exe = win32process.GetModuleFileNameEx(mypyproc, 0)
            if yt_chrome and exe.endswith("chrome.exe"):
                title = win32gui.GetWindowText(hwnd)
                if ("- YouTube" in title):
                    match = re.search(r"(?:\([0-9]+\) )?(.+) - YouTube", title).group(1)
                    if "-" in match:
                        artist, song = match.split("-")
                        song = song.strip()
                        artist = artist.strip()
                    else:
                        song = match.strip()
                        artist = None
                    result["chrome"] = artist, song
            elif spotify and exe.endswith("Spotify.exe"):
                title = win32gui.GetWindowText(hwnd)
                if ("-" in title):
                    artist, song = title.split("-")
                    song = song.strip()
                    artist = artist.strip()
                    result["spotify"] = artist, song
        except PyWinError:
            pass

    result = {}
    win32gui.EnumWindows(enumHandler, result)
    return result


def get_url(name):
    textToSearch = name
    query = urllib.parse.quote(textToSearch)
    url = "https://www.youtube.com/results?search_query=" + query
    response = urllib.request.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    vid = soup.find(attrs={'class': 'yt-uix-tile-link'})
    return 'https://www.youtube.com' + vid['href']