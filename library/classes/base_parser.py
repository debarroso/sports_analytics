from bs4 import BeautifulSoup
import pathlib
import logging
import glob
import os


class BaseParser:
    
    def __init__(
        self,
        parser_path,
        glob_string="*"
    ):
        self.base_path = pathlib.Path(__file__).parents[2].resolve()
        self.parser_path = parser_path
        self.parser_name = parser_path.parts[-1]
        self.datalake_path = pathlib.Path(
            str(self.parser_path).replace('web_scraping', 'datalake').replace("parsers", "sources")
        )
        self.parsed_path = pathlib.Path(
            str(self.datalake_path).replace("sources", "parsed") 
        )
        self.files = self.get_files(glob_string=glob_string)
        if len(self.files) == 0:
            exit()
        self.data = []

    def get_logger(self, logger_format="%(asctime)s - %(levelname)s - %(message)s"):
        logging.basicConfig(level=logging.INFO, format=logger_format)
        return logging.getLogger(self.parser_name)

    def get_files(self, glob_string="*"):
        glob_path = self.datalake_path / "unprocessed" / glob_string
        return glob.glob(str(glob_path))
    
    @staticmethod
    def get_soup(file_name=""):
        with open(file_name, mode="r", encoding="utf-8") as fp:
            soup = BeautifulSoup(fp, features="lxml")
        return soup

    @staticmethod
    def move_to_processed(file_name=""):
        os.rename(file_name, file_name.replace("unprocessed", "processed"))
