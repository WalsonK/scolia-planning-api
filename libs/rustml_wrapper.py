import sys
import os
import ctypes

class Rustml:
    def __init__(self):
        self.lib = None
        self.load_lib()

    def load_lib(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))

        if sys.platform == "win32":
            lib_path = os.path.join(current_dir, "librustml.dll")
        elif sys.platform == "darwin":
            lib_path = os.path.join(current_dir, "librustml.dylib")
        elif sys.platform == "linux":
            lib_path = os.path.join(current_dir, "librustml.so")
        else:
            raise Exception("Unsupported OS")
        
        self.lib = ctypes.CDLL(lib_path)
        
        # Function signatures
        self.lib.add.argtypes = [ctypes.c_int, ctypes.c_int]
        self.lib.add.restype = ctypes.c_int

    def add(self, a, b):
        if self.lib is None:
            self.load_lib()
        return self.lib.add(a, b)