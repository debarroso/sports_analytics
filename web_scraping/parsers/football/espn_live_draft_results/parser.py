import time
import pathlib
import sys


project_path = pathlib.Path(__file__).parent.parent.parent.parent.parent.resolve()
sys.path.append(f"{project_path}/")
from library.classes.base_parser import BaseParser


class EspnLiveDraftResultsParser(BaseParser):
    def __init__(self, glob_string="*"):
        super().__init__(
            parser_path=pathlib.Path(__file__).parent.resolve(),
            glob_string=glob_string
        )
        self.data = []
    
    def parse(self):
        for draft_result_file in self.files():
            with open(draft_result_file) as f:
                pass

    def save_parsed_data(self):
        pass


if __name__ == "__main__":
    run_start = time.perf_counter()
    parser = EspnLiveDraftResultsParser()
    parser.parse()
    parser.save_parsed_data()
    print(f"Total run time = {time.perf_counter() - run_start}")
