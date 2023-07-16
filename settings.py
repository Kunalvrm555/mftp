# settings.py
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_files = ['.env', '.session_token']

for dotenv_file in dotenv_files:
    dotenv_path = join(dirname(__file__), dotenv_file)
    load_dotenv(dotenv_path)
