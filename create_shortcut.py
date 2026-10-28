"""
Creates a Desktop shortcut for AgriSentinel one-click launch.
Run once: python create_shortcut.py
"""
import os
import sys

try:
    import winshell
    from win32com.client import Dispatch
except ImportError:
    print("Installing pywin32 + winshell for shortcut creation...")
    os.system(f'"{sys.executable}" -m pip install pywin32 winshell')
    import winshell
    from win32com.client import Dispatch

desktop = winshell.desktop()
bat_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "start_agrisentinel.bat")
shortcut_path = os.path.join(desktop, "AgriSentinel.lnk")

shell = Dispatch("WScript.Shell")
shortcut = shell.CreateShortCut(shortcut_path)
shortcut.Targetpath = bat_path
shortcut.WorkingDirectory = os.path.dirname(bat_path)
shortcut.Description = "Launch AgriSentinel Enterprise Dashboard & Backend"
shortcut.IconLocation = "shell32.dll,21"
shortcut.save()

print(f"\nDesktop shortcut created: {shortcut_path}")
print("Double-click 'AgriSentinel' on your Desktop to launch everything!")
