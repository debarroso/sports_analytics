from library.classes.base_database_handler import BaseDatabaseHandler
import pathlib


class EspnLiveDraftTrendsDatabaseHandler(BaseDatabaseHandler):

    def __init__(self):
        super().__init__(
            handler_path=pathlib.Path(__file__).resolve().parent,
            db_name="nfl_statistics",
            schema="fantasy_draft",
        )
        self.table_name = "espn_mock_draft_trends"


if __name__ == "__main__":
    db_handler = EspnLiveDraftTrendsDatabaseHandler()
    db_handler.upload_parsed_data()
