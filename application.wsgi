from os import path
import sys

appdir = path.dirname(path.abspath(__file__))
sys.path.append(appdir)

from website import app as application
