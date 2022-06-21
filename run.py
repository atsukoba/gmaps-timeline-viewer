import argparse
import numpy as np
import pandas as pd
import streamlit as st


if __name__ == "__main__":

    lat, lon = 35.68184, 139.76718
    df = pd.DataFrame(
        np.random.randn(1000, 2) / [100, 100] + [lat, lon],
        columns=['lat', 'lon']
    )

    st.title("GoogleMaps Timeline History Demo App")
    # st.subheader("")
    st.map(df)
