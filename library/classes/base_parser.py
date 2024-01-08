from bs4 import BeautifulSoup
import platform
import glob


class BaseParser:
    
    def __init__(self, parser_path="", glob_string="*"):
        self.parser_path = parser_path
        self.delimiter = "\\" if platform.system() == "Windows" else "/"
        self.datalake_path = str(self.parser_path).replace("web_scraping", "datalake").replace("parsers", "sources")
        self.parsed_path = str(self.parser_path).replace("web_scraping", "datalake").replace("parsers", "parsed")
        self.files = self.get_files(glob_string=glob_string)
        if len(self.files) == 0:
            exit()

    def get_files(self, glob_string="*"):
        return glob.glob(f"{self.datalake_path}{self.delimiter}unprocessed{self.delimiter}{glob_string}")
    
    def get_soup(self, file_name=""):
        with open(file_name, mode="r", encoding="utf-8") as fp:
            soup = BeautifulSoup(fp, features="lxml")
        return soup
