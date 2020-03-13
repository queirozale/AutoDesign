from cx_Freeze import setup, Executable
import os.path

PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')

base = 'Win32GUI'

executables = [Executable("AD_GUI.py", base=base, targetName='BeamOpt.exe', icon='engicon.ico')]

packages = ['pyqt5', 'ezdxf', 'matplotlib', 'pandas']
include_files = [os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tk86t.dll'),
                 os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tcl86t.dll'),
                 os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'sqlite3.dll'),
                 'apoio1.txt', 'apoio2.txt', 'caa.txt',
                 'project_data.txt', 'results.txt', 'tipo.txt']

options = {
      'build_exe': {
            'packages': packages,
            'include_files': include_files,
      }
}

setup(name='BeamOptimizer',
      version='0.1',
      description='AutoDesign',
      executables=executables)
