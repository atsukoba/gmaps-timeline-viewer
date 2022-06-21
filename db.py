import argparse
import json
import os
from enum import unique
from glob import glob
from logging import PlaceHolder
from sqlite3 import Cursor
from typing import Dict, List

import pandas as pd
from sqlalchemy import (ARRAY, TIMESTAMP, Column, Float, ForeignKey, Integer,
                        String, create_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, scoped_session, sessionmaker
from sqlalchemy.sql import text
from tqdm import tqdm

from utils import create_logger, env

logger = create_logger("db")

connection_config = {
    "user": env["DATABASE_USER"],
    "password": env["DATABASE_PASSWORD"],
    "host": env["DATABASE_HOST"],
    "socket": env["DATABASE_SOCKET"],
    "database": "gmap_demo_app"
}

if connection_config["host"]:
    engine = create_engine(
        "postgresql://{user}:{password}@{host}/{database}".format(
            **connection_config), echo=True)
else:
    engine = create_engine(
        "postgresql://{user}:{password}@/{database}?host={socket}".format(
            **connection_config), echo=True)


class SearchQueries:
    hoge = text("SELECT * FROM User WHERE age >= :age_min AND age <= :age_max")


def search_hoge() -> pd.DataFrame:
    rec = engine.execute(SearchQueries.hoge)
    rec_df = pd.DataFrame.from_records(rec)
    return rec_df


if __name__ == "__main__":

    """ Create Database
    [name, latitude, longitude, address, start_time, end_time]
    """

    visitted_places = []

    data_files = [f for f in glob(
        "./Takeout/**/*.json", recursive=True) if "Records" not in f and "Settings" not in f]

    for path in tqdm(data_files, desc="Loading history data"):
        try:
            with open(path, "r") as f:
                data = json.load(f)
        except:
            print(f"Failed to load json file: {path}")
            continue

        for d in tqdm(data["timelineObjects"], desc="Extracting data", leave=False):
            if (p := d.get("placeVisit", None)) is not None:
                try:
                    visitted_places.append([
                        p["location"].get("name", "No name"),
                        p["location"]["latitudeE7"] / 1e7,
                        p["location"]["longitudeE7"] / 1e7,
                        p["location"].get("address", "No Address"),
                        p["duration"]["startTimestamp"],
                        p["duration"]["endTimestamp"]
                    ])
                except KeyError as e:
                    logger.debug(f"Keyerror, {e}")
                    logger.debug(p)
                    continue

    visitted_places = pd.DataFrame(
        visitted_places,
        columns=["name", "latitude", "longitude", "address", "start_time", "end_time"])
    visitted_places.head(10)

    visitted_places.to_sql("place", con=engine,
                           if_exists="append", index=False)
