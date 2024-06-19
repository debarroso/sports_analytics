from library.classes.base_parser import BaseParser
import pandas as pd
import pathlib
import time


class EspnLiveDraftTrendsParser(BaseParser):
    def __init__(self, glob_string="*"):
        super().__init__(
            parser_path=pathlib.Path(__file__).parent.resolve(), glob_string=glob_string
        )
        self.logger = self.get_logger()
        self.data = []

    def parse(self):
        for draft_result_file in self.files:
            self.logger.info(f"Processing file {draft_result_file}")
            df = pd.read_csv(draft_result_file)

            file_date_string = draft_result_file.split("_")[-1].replace(".csv", "")
            date_object = pd.to_datetime(file_date_string).date()
            df.insert(0, "date", str(date_object))
            self.data.append(df)

            self.move_to_processed(draft_result_file)

    def save_parsed_data(self):
        parsed_file_path = self.parsed_path / "draft_trends.csv"
        combined_df = pd.concat(self.data, ignore_index=True)
        combined_df.to_csv(str(parsed_file_path), index=False, header=True)


if __name__ == "__main__":
    run_start = time.perf_counter()
    parser = EspnLiveDraftTrendsParser()
    parser.parse()
    parser.save_parsed_data()
    parser.logger.info(f"Total run time = {time.perf_counter() - run_start}")
