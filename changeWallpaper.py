import ctypes, sys

ctypes.windll.user32.SystemParametersInfoA(20, 0, sys.argv[1], 0)