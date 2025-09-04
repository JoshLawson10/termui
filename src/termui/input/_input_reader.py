import sys

__all__ = ["InputReader"]

WINDOWS = sys.platform == "win32"

if WINDOWS:
    from termui.input._input_reader_windows import InputReader
else:
    from termui.input._input_reader_unix import InputReader
