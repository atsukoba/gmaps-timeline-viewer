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

    def draw_map(self, s: TimeStamp, e: TimeStamp) -> pd.DataFrame:

        res_df = Search.time_within(s, e)
        cood_df = res_df[["longitude", "latitude"]]
        cood_df.columns = ["lon", "lat"]

        st.pydeck_chart(pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            initial_view_state=pdk.ViewState(
                latitude=Search.view_center[0],
                longitude=Search.view_center[1],
                zoom=15,
                pitch=25,
            ),
            layers=[
                # pdk.Layer(
                #     "HexagonLayer",
                #     data=df,
                #     get_position="[lon, lat]",
                #     radius=200,
                #     elevation_scale=4,
                #     elevation_range=[0, 1000],
                #     pickable=True,
                #     extruded=True,
                # ),
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

        res_df = self.draw_map(s_start_date, s_end_date)

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
