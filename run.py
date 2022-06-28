import argparse
import datetime as dt

import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st
from dateutil.relativedelta import relativedelta  # to add days or years

from db import Search
from utils import TimeStamp, create_logger


logger = create_logger("st")


class StreamlitDemoApp:

    def __init__(self):
        cood_df = Search.get_all_cood()

        # calc view point
        Search.view_center = (cood_df.latitude.values.mean(),
                              cood_df.longitude.values.mean())
        logger.info(f"ViewPoint set: {Search.view_center}")

        self.mode = "stay"

    def draw_place(self, s: TimeStamp, e: TimeStamp) -> pd.DataFrame:

        res_df = Search.place_time_within(s, e)
        cood_df = res_df[["longitude", "latitude"]]
        cood_df.columns = ["lon", "lat"]

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
                    "ScatterplotLayer",
                    data=cood_df,
                    get_position="[lon, lat]",
                    get_color="[200, 30, 0, 160]",
                    get_radius=200,
                ),
            ],
            width="100%",
            height=800,
        ))

        return res_df

    def draw_move(self, s: TimeStamp, e: TimeStamp) -> pd.DataFrame:

        res_df = Search.move_time_within(s, e)
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

        return res_df

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

        s_start_date: TimeStamp = cols_l.slider("Start date", min_value=start_date,
                                                value=end_date,
                                                max_value=end_date, format=format)
        s_end_date: TimeStamp = cols_r.slider("End date", min_value=start_date,
                                              value=end_date,
                                              max_value=end_date, format=format)

        self.mode = st.selectbox(
            "Select Viewer Mode",
            ("stay", "move"))

        if self.mode == "stay":
            res_df = self.draw_place(s_start_date, s_end_date)
        else:
            res_df = self.draw_move(s_start_date, s_end_date)

        st.text("Curent Data")
        st.table(pd.DataFrame([[s_start_date, s_end_date]],
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
