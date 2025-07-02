import sys
import os
import ctypes
import numpy as np

class Rustml:
    def __init__(self):
        self.lib = None
        self.load_lib()

    def load_lib(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))

        if sys.platform == "win32":
            lib_path = os.path.join(current_dir, "librustml.dll")
        elif sys.platform == "darwin":
            lib_path = os.path.join(current_dir, "librustlib.dylib")
        elif sys.platform == "linux":
            lib_path = os.path.join(current_dir, "librustml.so")
        else:
            raise Exception("Unsupported OS")
        
        self.lib = ctypes.CDLL(lib_path)
        
        # Function signatures
        self.lib.add.argtypes = [ctypes.c_int, ctypes.c_int]
        self.lib.add.restype = ctypes.c_int

        self.lib.generate_greedy_planning.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                                      ctypes.POINTER(ctypes.c_float), ctypes.c_int,
                                                      ctypes.POINTER(ctypes.c_float), ctypes.c_int,
                                                      ctypes.POINTER(ctypes.c_float), ctypes.c_int,
                                                      ctypes.POINTER(ctypes.c_float), ctypes.c_int]
        self.lib.generate_greedy_planning.restype = ctypes.POINTER(ctypes.c_int)

        self.lib.free_greedy_planning.argtypes = [ctypes.POINTER(ctypes.c_int)]
        self.lib.free_greedy_planning.restype = None

    def add(self, a, b):
        if self.lib is None:
            self.load_lib()
        return self.lib.add(a, b)
    
    def generate_greedy_planning(self, total_slots: int, max_hours: int, slot_minutes: int, subjects: list[float], todo: list[float], unavailability: list[list[float]]):
        if self.lib is None:
            self.load_lib()
        
        # Convert lists to ctypes arrays
        subject_numpy = np.array(subjects, dtype=np.float32)
        subject_ptr = subject_numpy.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        todo_numpy = np.array(todo, dtype=np.float32)
        todo_ptr = todo_numpy.ctypes.data_as(ctypes.POINTER(ctypes.c_float))

        flat_unavailability = [item for sublist in unavailability for item in sublist]
        unavailability_numpy = np.array(flat_unavailability, dtype=np.float32)
        unavailability_ptr = unavailability_numpy.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        sub_unavailability = np.array([len(sublist) for sublist in unavailability], dtype=np.float32)
        sub_unavailability_ptr = sub_unavailability.ctypes.data_as(ctypes.POINTER(ctypes.c_float))


        result_ptr = self.lib.generate_greedy_planning(ctypes.c_int(total_slots), ctypes.c_int(max_hours), ctypes.c_int(slot_minutes), 
                                                   subject_ptr, ctypes.c_int(len(subjects)), 
                                                   todo_ptr, ctypes.c_int(len(todo)),
                                                   unavailability_ptr, ctypes.c_int(len(flat_unavailability)),
                                                   sub_unavailability_ptr, ctypes.c_int(len(sub_unavailability))
                                                   )
        
        # Convert result to a Python list
        arr_slice = ctypes.cast(result_ptr, ctypes.POINTER(ctypes.c_int * total_slots)).contents
        result = list(arr_slice)

        self.lib.free_greedy_planning(result_ptr)
        return result