import argparse
import datetime as dt

import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st
from dateutil.relativedelta import relativedelta  # to add days or years


class StreamlitDemoApp:

    def __init__(self):
        ...

    def draw_map(self):
        df = pd.DataFrame(
            np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
            columns=["lat", "lon"])

        st.pydeck_chart(pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            initial_view_state=pdk.ViewState(
                latitude=37.76,
                longitude=-122.4,
                zoom=11,
                pitch=50,
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
                    data=df,
                    get_position="[lon, lat]",
                    get_color="[200, 30, 0, 160]",
                    get_radius=200,
                ),
            ],
            width="100%",
            height=600,
        ))

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

        self.draw_map()

        # Range selector
        format = "YYYY/MM/DD"  # format output
        # I need some range in the past
        cols_l, cols_r = st.columns((1, 1))  # To make it narrower
        start_date = dt.date(year=2021, month=1, day=1) - \
            relativedelta(years=2)
        end_date = dt.datetime.now().date() - relativedelta(years=2)
        max_days = end_date - start_date

        s_start_date = cols_l.slider("Start date", min_value=start_date,
                                     value=end_date,
                                     max_value=end_date, format=format)
        s_end_date = cols_r.slider("End date", min_value=start_date,
                                   value=end_date,
                                   max_value=end_date, format=format)

        st.text("Curent Data")
        st.table(pd.DataFrame([[s_start_date, s_end_date]],
                              columns=["start",
                                       "end"],
                              index=["date"]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generation Result Demo App",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    args = parser.parse_args()
    app = StreamlitDemoApp()
    app.run()
