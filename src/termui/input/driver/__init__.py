import sys

if sys.platform == "win32":
    from termui.input.driver._windows_input_driver import WindowsInputDriver as Driver
else:
    from termui.input.driver._unix_input_driver import UnixInputDriver as Driver
