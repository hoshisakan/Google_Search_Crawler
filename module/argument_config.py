import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from argparse import ArgumentParser
from instance.config import Initialization as Init
from module.log_generate import Loggings
# from pathlib import Path


logger = Loggings()

class ArgumentConfig():
    @staticmethod
    def run():
        parser = ArgumentParser()
        parser.add_argument("-i", "--ini", help="setting ini file path", type=str)
        args = parser.parse_args()

        if args.ini:
            Init.setting_file_path = args.ini
        else:
            logger.error(f"argument task and output is required.")
            os._exit(0)