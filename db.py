import argparse
import json
from glob import glob
from typing import Dict, List

import pandas as pd
from tqdm import tqdm

if __name__ == "__main__":

    visitted_places = []

    """
    [name, latitude, longitude, address, start_time, end_time]
    """

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
                        p["location"]["latitudeE7"],
                        p["location"]["longitudeE7"],
                        p["location"].get("address", "No Address"),
                        p["duration"]["startTimestamp"],
                        p["duration"]["endTimestamp"]
                    ])
                except KeyError as e:
                    continue

    visitted_places = pd.DataFrame(
        visitted_places,
        columns=["name", "latitude", "longitude", "address", "start_time", "end_time"])
    visitted_places.head(10)
