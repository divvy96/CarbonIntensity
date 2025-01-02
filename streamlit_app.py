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

    st.set_page_config(page_title="electricity genration uk")

    st.title("electricity genration uk")

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
        current_intensity = carbon_intensity_data.get_current_postcode_intensity(
            st.session_state.postcode
        )
        forecast_intensity = carbon_intensity_data.get_forward_intensity(
            st.session_state.postcode, datetime.datetime.now()
        )

        if current_intensity != "":
            col1, col2 = st.columns(2)
            col1.metric(
                f"{st.session_state.postcode} current carbon intensity",
                current_intensity,
            )

            col2.caption(f"best time to charge car is:")
            col2.markdown(
                f'## {find_minimum_carbon_window(forecast_intensity).strftime("%a %d-%b @ %H:%M")}'
            )

        if isinstance(forecast_intensity, pandas.DataFrame):
            st.line_chart(forecast_intensity, x="from", y="forecast")
        else:
            st.write(f"unable to find postcode {st.session_state.postcode}")


if __name__ == "__main__":
    run()
