from bs4 import BeautifulSoup
import pathlib
import logging
import glob
import os


class BaseParser:

    def __init__(self, parser_path, glob_string="*"):
        self.base_path = pathlib.Path(__file__).parents[2].resolve()
        self.parser_path = parser_path
        self.parser_name = parser_path.parts[-1]
        self.logger = self.get_logger()
        self.datalake_path = pathlib.Path(
            str(self.parser_path)
            .replace("web_scraping", "datalake")
            .replace("parsers", "sources")
        )
        self.parsed_path = pathlib.Path(
            str(self.datalake_path).replace("sources", "parsed")
        )
        self.files = self.get_files(glob_string=glob_string)
        if len(self.files) == 0:
            exit()
        self.data = []

    def get_logger(self):
        logger = logging.getLogger(self.parser_name)
        logger.setLevel(logging.DEBUG)

        file_handler = logging.FileHandler(
            f"{self.base_path}/logs/{self.parser_name}_pipeline/logfile.log"
        )
        file_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        return logger

    def get_files(self, glob_string="*"):
        glob_path = self.datalake_path / "unprocessed" / glob_string
        return glob.glob(str(glob_path))

    @staticmethod
    def get_soup(file_name=""):
        with open(file_name, encoding="utf-8") as fp:
            soup = BeautifulSoup(fp, features="lxml")
        return soup

    @staticmethod
    def move_to_processed(file_name=""):
        os.rename(file_name, file_name.replace("unprocessed", "processed"))
