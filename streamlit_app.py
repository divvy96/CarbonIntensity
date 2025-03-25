import datetime
import pandas

import streamlit as st

import carbon_intensity_data


def find_minimum_carbon_window(df):
    """returns the start of period with the lowest mean carbon intensity"""

    WINDOW_SIZE = 4
    indexer = pandas.api.indexers.FixedForwardWindowIndexer(window_size=WINDOW_SIZE)
    window_average = df["forecast"].rolling(indexer).mean()
    df["window"] = window_average
    return df.loc[window_average.idxmin(), "from"]


def run():
    """app that displays some metrics about electricty generation in the uk"""

    st.set_page_config(page_title="electricity generation uk")

    st.title("UK Carbon Intensity Forecast")
    st.subheader("Find the best times to use electricty to minimise gCO₂/kWh")

    st.text_input(
        "Enter postcode for current carbon intensity of your region", key="postcode"
    )

    df_intensity_banding = pandas.DataFrame(
        carbon_intensity_data.intensity_bands(),
        columns=["minimum carbon level", "intensity label"],
    )
    st.dataframe(
        data=df_intensity_banding,
        hide_index=True,
    )

    if st.session_state.postcode == "":
        current_intensity = carbon_intensity_data.get_current_intensity()
        st.metric(label="uk current carbon intensity", value=current_intensity)

    else:
        postcode = st.session_state.postcode.strip()
        current_intensity = carbon_intensity_data.get_current_postcode_intensity(
            postcode
        )
        forecast_intensity = carbon_intensity_data.get_forward_intensity(
            postcode, datetime.datetime.now()
        )

        if current_intensity != "":
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    f"current carbon intensity {st.session_state.postcode}",
                    f"{current_intensity} gCO₂/kWh",
                )

            with col2:

                st.caption(f"best time to charge car is:")
                st.markdown(
                    f'## {find_minimum_carbon_window(forecast_intensity).strftime("%a %d-%b @ %H:%M")}'
                )

        if isinstance(forecast_intensity, pandas.DataFrame):
            st.line_chart(forecast_intensity, x="from", y="forecast")
        else:
            st.write(f"unable to find postcode {st.session_state.postcode}")


if __name__ == "__main__":
    run()
