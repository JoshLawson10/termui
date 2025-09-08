import sys

if sys.platform == "win32":
    from ._windows_driver import WindowsDriver as Driver
else:
    from ._unix_driver import UnixDriver as Driver
