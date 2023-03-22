import os

filenames = os.listdir(os.path.dirname(os.path.abspath(__file__)))
filenames.remove("__init__.py")
filenames.remove("__pycache__")
__all__ = []
for file in filenames:
    if file[0] != '#':
        __all__.append(file.replace(".py", ""))