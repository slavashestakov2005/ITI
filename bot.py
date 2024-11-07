import os
from dotenv import load_dotenv
os.chdir(os.path.dirname(os.path.abspath(__file__)))
load_dotenv('.env')


from backend.bot import start_bot


if '__main__' == __name__:
    start_bot()
