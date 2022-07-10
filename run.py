import argparse
import datetime as dt
from turtle import ondrag

import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st
from dateutil.relativedelta import relativedelta  # to add days or years

from db import Search
from utils import TimeStamp, create_logger, Coordinate


logger = create_logger("st")


class StreamlitDemoApp:

    def __init__(self):
        cood_df = Search.get_all_cood()
        # calc view point
        Search.view_center = (cood_df.latitude.values.mean(),
                              cood_df.longitude.values.mean())
        logger.info(f"ViewPoint set: {Search.view_center}")
        self.mode = "stay"
        # store
        self.current_start: TimeStamp = str(
            dt.datetime.now().date() - relativedelta(years=1))
        self.current_end: TimeStamp = str(dt.datetime.now().date())
        self.current_max_move_distance = 5000
        self.current_view_position: Coordinate = Search.view_center  # not used yet

    def ondrag_callback(self, widget_instance, payload: dict):
        """ Deck `on_view_state_change` callback

        Note: streamlit not suporting PyDeck widget callbacks yet

        payload (dict):
        {
            "type": "deck-view-state-change-event",
            "data": {
                "width": int,
                "height": int,
                "latitude": float,
                "longitude": float,
                "zoom": float,
                "bearing": float,
                "pitch": float,
                "altitude": float,
                "maxZoom": float,
                "minZoom": float
                "maxPitch": float,
                "minPitch": float,
                "nw": [float, float],
                "se": [float, float]
            }
        }
        """
        west_lng, north_lat = payload["data"]["nw"]
        east_lng, south_lat = payload["data"]["se"]
        logger.info("map moved")
        logger.info(f"west: {west_lng}")
        logger.info(f"north: {north_lat}")
        logger.info(f"east: {east_lng}")
        logger.info(f"south: {south_lat}")
        self.current_view_position = ((north_lat + south_lat) / 2,
                                      (east_lng + west_lng) / 2)

    def draw_place(self) -> pd.DataFrame:
        res_df = Search.place_time_within(self.current_start,
                                          self.current_end)
        cood_df = res_df[["name", "longitude", "latitude"]]
        deck = pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            layers=[
                pdk.Layer(
                    "ScatterplotLayer",
                    data=cood_df,
                    get_position="[longitude, latitude]",
                    get_color="[200, 30, 0, 160]",
                    get_radius=200,
                    pickable=True,
                ),
            ],
            initial_view_state=pdk.ViewState(
                latitude=Search.view_center[0],
                longitude=Search.view_center[1],
                zoom=5,
                pitch=25,
            ),
            tooltip={"html": "<b>Name: </b>{name}<br /> " +
                     "<b>Longitude: </b>{longitude}<br /> " +
                     "<b>Latitude: </b>{latitude}"},
            width="100%",
            height=1000,
        )
        # NOTE: not supported yet
        # deck.deck_widget.on_view_state_change(self.ondrag_callback,
        #                                       remove=True)
        st.pydeck_chart(deck)
        return res_df[["name", "latitude", "longitude", "address"]]

    def draw_move(self) -> pd.DataFrame:
        res_df = Search.move_time_distance_within(self.current_start,
                                                  self.current_end,
                                                  self.current_max_move_distance)
        cood_df = res_df[["start_longitude", "start_latitude",
                          "end_longitude", "end_latitude"]]
        cood_df.columns = ["slon", "slat", "elon", "elat"]
        st.pydeck_chart(pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            initial_view_state=pdk.ViewState(
                latitude=Search.view_center[0],
                longitude=Search.view_center[1],
                zoom=5,
                pitch=25,
            ),
            layers=[
                pdk.Layer(
                    "LineLayer",
                    data=cood_df,
                    get_source_position="[slon, slat]",
                    get_target_position="[elon, elat]",
                    get_color="[200, 30, 0, 160]",
                    get_width=1,
                    highlight_color=[255, 255, 0],
                    picking_radius=10,
                    auto_highlight=True,
                    pickable=True,
                )
            ],
            width="100%",
            height=800,
        ))
        return res_df[["activity_type", "distance"]]

    def run(self):
        st.title("Timeline History")
        st.subheader("Google Maps History Viewer Demo App")
        st.sidebar.title("About Demo App")
        st.sidebar.title("Note")
        st.sidebar.write(
            """This demo app is built by [Atsuya Kobayashi](https://www.atsuya.xyz), with
            Python backend (streamlit) and PostgreSQL to handle Google Maps Location History data.
            """
        )
        # Range selector
        format = "YYYY/MM/DD"  # format output
        # I need some range in the past
        cols_l, cols_r = st.columns((1, 1))  # To make it narrower
        start_date = dt.datetime.now().date() - relativedelta(years=8)
        end_date = dt.datetime.now().date()
        max_days = end_date - start_date
        self.current_start: TimeStamp = cols_l.slider("Start date", min_value=start_date,
                                                      value=start_date,
                                                      max_value=end_date, format=format)
        self.current_end: TimeStamp = cols_r.slider("End date", min_value=start_date,
                                                    value=end_date,
                                                    max_value=end_date, format=format)
        self.mode = st.selectbox(
            "Select Viewer Mode",
            ("stay", "move"))
        if self.mode == "stay":
            res_df = self.draw_place()
        else:
            self.current_max_move_distance = st.number_input("Max Distance (m)",
                                                             step=100,
                                                             value=5000,
                                                             min_value=10,
                                                             max_value=1000000)
            res_df = self.draw_move()
        st.text("Curent Data")
        st.table(pd.DataFrame([[self.current_start, self.current_end]],
                              columns=["start",
                                       "end"],
                              index=["date"]))
        st.table(res_df.head(20))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generation Result Demo App",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    args = parser.parse_args()
    app = StreamlitDemoApp()
    app.run()
