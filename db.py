import argparse
import hashlib
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
from sqlalchemy.sql.elements import TextClause
from tqdm import tqdm

from utils import Coordinate, TimeStamp, create_logger, env

logger = create_logger("db")

# build db connection
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


class Search:
    """ build queries from spatio-temporal info """

    view_center: Coordinate = (35.0, 135.0)  # latitude / longitude
    radius: float = 30.0  # km

    @classmethod
    def get_all_cood(cls) -> pd.DataFrame:
        q = text(
            f"SELECT longitude, latitude FROM place;"
        )
        logger.debug(q)
        df = pd.read_sql_query(sql=q, con=engine)
        return df

    @classmethod
    def place_time_within(cls, start_date: str, end_date: str) -> pd.DataFrame:
        q = text(
            f"SELECT P.* FROM place P INNER JOIN event E on E.id = P.event_id WHERE start_time >= '{start_date}' AND start_time <= '{end_date}';"
        )
        logger.debug(q)
        df = pd.read_sql_query(sql=q, con=engine)
        logger.debug(df.head(5))
        return df
    
    @classmethod
    def move_time_within(cls, start_date: str, end_date: str) -> pd.DataFrame:
        q = text(
            f"SELECT A.* FROM activity A INNER JOIN event E on E.id = A.event_id WHERE start_time >= '{start_date}' AND start_time <= '{end_date}';"
        )
        logger.debug(q)
        df = pd.read_sql_query(sql=q, con=engine)
        logger.debug(df.head(5))
        return df


if __name__ == "__main__":


    events = []
    visitted_places = []
    activities = []

    """
    - events
        [id (PK), start_time, end_time]
    - visitted_places
        [event_id (FK), name, latitude, longitude, address]
    - activities
        [event_id (FK), activity_type, start_latitude, start_longitude, 
        end_latitude, end_longitude, distance]
    """

    data_files = [f for f in glob(
        "./Takeout/**/*.json", recursive=True) if "Records" not in f and "Settings" not in f]

    for f_idx, path in enumerate(tqdm(data_files, desc="Loading history data")):
        try:
            with open(path, "r") as f:
                data = json.load(f)
        except:
            print(f"Failed to load json file: {path}")
            continue
        for d_idx, d in enumerate(tqdm(data["timelineObjects"], desc="Extracting data", leave=False)):
            _id = hashlib.md5((str(f_idx) + "_" + str(d_idx)).encode()).hexdigest()
            if (p := d.get("placeVisit", None)) is not None:
                try:
                    events_el = [
                        _id,
                        p["duration"]["startTimestamp"],
                        p["duration"]["endTimestamp"]
                    ]
                    visitted_place_el = [
                        _id,
                        p["location"].get("name", "no name"),
                        p["location"]["latitudeE7"] / 1e7,
                        p["location"]["longitudeE7"] / 1e7,
                        p["location"].get("address", "No Address"),
                    ]
                except KeyError as e:
                    continue
                events.append(events_el)
                visitted_places.append(visitted_place_el)
            if (p := d.get("activitySegment", None)) is not None:
                try:
                    events_el = [
                        _id,
                        p["duration"]["startTimestamp"],
                        p["duration"]["endTimestamp"]
                    ]
                    activit_el = [
                        _id,
                        p["activityType"],
                        p["startLocation"]["latitudeE7"] / 1e7,
                        p["startLocation"]["longitudeE7"] / 1e7,
                        p["endLocation"]["latitudeE7"] / 1e7,
                        p["endLocation"]["longitudeE7"] / 1e7,
                        p["distance"]
                    ]
                except KeyError as e:
                    continue
                events.append(events_el)
                activities.append(activit_el)

    events = pd.DataFrame(
        events,
        columns=["id", "start_time", "end_time"]
    )
    activities = pd.DataFrame(
        activities,
        columns=["event_id",
                 "activity_type",
                 "start_latitude",
                 "start_longitude",
                 "end_latitude",
                 "end_longitude",
                 "distance"
                 ])
    visitted_places = pd.DataFrame(
        visitted_places,
        columns=["event_id", "name", "latitude", "longitude", "address"])

    events.to_sql("event", con=engine,
                  if_exists="append", index=False)
    visitted_places.to_sql("place", con=engine,
                           if_exists="append", index=False)
    activities.to_sql("activity", con=engine,
                      if_exists="append", index=False)
