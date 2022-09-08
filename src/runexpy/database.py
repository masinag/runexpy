import copy
import operator
import os
import shutil
from dataclasses import dataclass, field
from functools import partial, reduce
from pathlib import Path
from typing import ClassVar, Dict, List, Set, cast

import tinydb
from tinydb.database import TinyDB
from tinydb.middlewares import CachingMiddleware
from tinydb.queries import Query, QueryInstance, where
from tinydb.storages import JSONStorage
from tinydb.table import Document, Table

from runexpy.result import Result, ResultJSON
from runexpy.utils import DefaultParamsT, ParamsT


@dataclass
class Database:
    # public fields
    db: TinyDB
    dir: str

    # private fields
    _fields: Set[str] = field(init=False)

    # private class fields

    # fields
    _F_SCRIPT: ClassVar[str] = "script"
    _F_CMPDIR: ClassVar[str] = "campaign_dir"
    _F_PARAMS: ClassVar[str] = "default_params"
    # tables
    _T_CONFIG: ClassVar[str] = "config"
    _T_RESULT: ClassVar[str] = "result"

    def __post_init__(self):
        self._fields = set(self.get_default_params().keys())

    @staticmethod
    def _name(dir: str) -> str:
        return f"{os.path.basename(dir)}.json"

    @classmethod
    def new(
        cls,
        script: List[str],
        default_params: DefaultParamsT,
        campaign_dir: str,
        overwrite: bool,
    ):
        # Make sure the directory does not exist already
        if Path(campaign_dir).exists() and not overwrite:
            raise FileExistsError("The specified directory already exists")

        db_name = cls._name(campaign_dir)

        if Path(campaign_dir).exists() and overwrite:
            # Verify we are not deleting files belonging to the user
            folder_contents = set(os.listdir(campaign_dir))
            allowed_files = {"data", db_name}

            if not folder_contents.issubset(allowed_files):
                raise ValueError(
                    "The specified directory cannot be overwritten "
                    "because it contains user files."
                )
            # This operation destroys data.
            shutil.rmtree(campaign_dir)

        # Create the directory and database file in it
        # The indent and separators ensure the database is human readable.
        os.makedirs(campaign_dir)
        db = tinydb.TinyDB(
            os.path.join(campaign_dir, db_name),
            storage=CachingMiddleware(partial(JSONStorage, indent=2)),
        )

        # Save the configuration in the database
        config = {
            cls._F_SCRIPT: copy.deepcopy(script),
            cls._F_CMPDIR: campaign_dir,
            cls._F_PARAMS: copy.deepcopy(default_params),
        }

        db.table("config").insert(config)
        db = cls(db, campaign_dir)
        db.flush()
        return db

    @classmethod
    def load(cls, campaign_dir: str):
        # Verify file exists
        if not Path(campaign_dir).exists():
            raise ValueError("Directory does not exist")

        # Extract filename from campaign dir
        db_name = cls._name(campaign_dir)
        filepath = os.path.join(campaign_dir, db_name)

        # Read TinyDB instance from file
        db = TinyDB(filepath, storage=CachingMiddleware(partial(JSONStorage, indent=2)))

        # # Make sure the configuration is a valid dictionary
        # if set(tinydb.table("config").get.all()[0].keys()) != {"script", "params"}:
        #     # Remove the database instance created by tinydb
        #     os.remove(filepath)
        #     raise ValueError("Specified campaign directory seems corrupt")

        return cls(db, campaign_dir)

    def _result_table(self) -> Table:
        return self.db.table(self._T_RESULT)

    def _config_table(self) -> Table:
        return self.db.table(self._T_CONFIG)

    def get_config(self) -> Document:
        return self._config_table().all()[0]

    def get_script(self) -> List[str]:
        return self.get_config()[self._F_SCRIPT]

    def get_campaign_dir(self) -> str:
        return self.get_config()[self._F_CMPDIR]

    def get_data_dir(self) -> str:
        return os.path.join(self.get_campaign_dir(), "data")

    def get_default_params(self) -> DefaultParamsT:
        return self.get_config()[self._F_PARAMS]

    def _correct_structure(self, result: ParamsT) -> bool:
        return self._fields == set(result.keys())

    @staticmethod
    def _problem_query(problem: ParamsT) -> QueryInstance:
        query = Query()
        if not problem:
            return query.noop()
        return reduce(
            operator.and_, map(lambda p: query.params[p[0]] == p[1], problem.items())
        )

    def count_results_for(self, problem: ParamsT) -> int:
        query = self._problem_query(problem)
        return self._result_table().count(query)

    def _search_results_for(self, problem: ParamsT) -> List[ResultJSON]:
        query = self._problem_query(problem)
        return list(
            map(lambda x: cast(ResultJSON, x), self._result_table().search(query))
        )

    def get_results_for(self, problem: ParamsT) -> List[Result]:
        return list(map(Result.from_json, self._search_results_for(problem)))

    def get_files_for(self, result: Result) -> Dict[str, str]:
        experiment_dir = os.path.join(self.get_data_dir(), result.id)
        return {f: os.path.join(experiment_dir, f) for f in os.listdir(experiment_dir)}

    def insert_result(self, result: Result) -> None:
        if not self._correct_structure(result.params):
            raise ValueError(
                f"Bad structure for result {result}, the following fields "
                f"are expected: {self._fields}"
            )
        if self._result_table().contains(where("id") == result.id):
            raise ValueError("An entry with the same id is present")
        self._result_table().insert(result.to_json())
        self.flush()

    def flush(self):
        assert isinstance(self.db.storage, CachingMiddleware)
        self.db.storage.flush()
