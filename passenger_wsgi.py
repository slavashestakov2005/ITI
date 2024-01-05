import sys
import os
from dotenv import load_dotenv
os.chdir(os.path.dirname(os.path.abspath(__file__)))
load_dotenv('.env')


INTERP = os.path.expanduser(os.getenv('INTERPRETER'))
if sys.executable != INTERP:
   os.execl(INTERP, INTERP, *sys.argv)

sys.path.append(os.getcwd())

from main import app as application
