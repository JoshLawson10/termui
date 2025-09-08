import sys

if sys.platform == "win32":
    from termui.drivers._windows_driver import WindowsDriver as Driver
else:
    from termui.drivers._unix_driver import UnixDriver as Driver
