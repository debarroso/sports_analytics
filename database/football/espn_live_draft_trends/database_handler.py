from library.classes.base_database_handler import BaseDatabaseHandler
import pathlib
import time


class EspnLiveDraftTrendsDatabaseHandler(BaseDatabaseHandler):

    def __init__(self):
        super().__init__(
            handler_path=pathlib.Path(__file__).resolve().parent,
            handler_class=self.__class__.__name__,
            db_name="nfl_statistics",
            schema="fantasy_draft",
        )
        self.table_name = "espn_mock_draft_trends"


if __name__ == "__main__":
    run_start = time.perf_counter()
    db_handler = EspnLiveDraftTrendsDatabaseHandler()
    db_handler.upload_parsed_data()
    db_handler.logger.info(
        f"DB connection run time = {time.perf_counter() - run_start}"
    )
