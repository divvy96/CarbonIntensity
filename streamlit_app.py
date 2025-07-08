import datetime

import altair as alt
import pandas

import streamlit as st

import carbon_intensity_data


def find_minimum_carbon_window(df):
    """returns the start of period with the lowest mean carbon intensity"""

    WINDOW_SIZE = 4
    indexer = pandas.api.indexers.FixedForwardWindowIndexer(window_size=WINDOW_SIZE)
    window_average = df["intensity"].rolling(indexer).mean()
    df["window"] = window_average
    return df.loc[window_average.idxmin(), "start_time"]


def run():
    """app that displays some metrics about electricty generation in the uk"""

    st.set_page_config(page_title="electricity generation uk")

    st.title("UK Carbon Intensity Forecast")
    st.subheader("Find the best times to use electricty to minimise gCO₂/kWh")

    st.text_input(
        "Enter postcode for current carbon intensity of your region", key="postcode"
    )

    intensity_banding_df = pandas.DataFrame(carbon_intensity_data.intensity_bands())

    if st.session_state.postcode == "":
        current_intensity = carbon_intensity_data.get_current_intensity()
        st.metric(
            label="uk current carbon intensity",
            value=current_intensity.carbon_intensity,
        )

    else:
        postcode = st.session_state.postcode.strip()
        current_intensity = carbon_intensity_data.get_current_postcode_intensity(
            postcode
        ).carbon_intensity
        forecast_intensity = pandas.DataFrame(
            carbon_intensity_data.get_48hr_postcode_intensity(
                start_datetime=datetime.datetime.now(), postcode=postcode
            )
        )
        forecast_intensity["start_time"] = pandas.to_datetime(
            forecast_intensity["start_time"]
        )
        forecast_intensity["end_time"] = pandas.to_datetime(
            forecast_intensity["end_time"]
        )

        forecast_intensity = forecast_intensity.sort_values("intensity")
        banding = pandas.DataFrame(carbon_intensity_data.intensity_bands()).sort_values(
            "lower_bound"
        )
        banding = banding.rename(columns={"intensity": "intensity_label"})

        forecast_intensity = pandas.merge_asof(
            forecast_intensity, banding, left_on="intensity", right_on="lower_bound"
        )

        if current_intensity != "":
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    label=f"current carbon intensity {st.session_state.postcode}",
                    value=f"{current_intensity} gCO₂/kWh",
                    delta=f"{(int(current_intensity - forecast_intensity['intensity'].mean()))} vs avg",
                    delta_color="inverse",
                )

            with col2:
                st.caption(f"best time to charge car is:")
                st.markdown(
                    f"## {find_minimum_carbon_window(forecast_intensity).strftime('%a %d-%b @ %H:%M')}"
                )

        if isinstance(forecast_intensity, pandas.DataFrame):
            forecast_chart = (
                alt.Chart(forecast_intensity)
                .mark_bar()
                .encode(
                    x=alt.X("start_time:T", title="period"),
                    y="intensity:Q",
                    color=alt.Color(
                        "intensity_label:N",
                        scale=alt.Scale(
                            domain=banding["intensity_label"], range=banding["color"]
                        ),
                        legend=alt.Legend(False),
                    ),
                )
            )
            st.altair_chart(forecast_chart, use_container_width=True)
        else:
            st.write(f"unable to find postcode {st.session_state.postcode}")

    st.dataframe(
        data=intensity_banding_df[["intensity", "upper_bound"]],
        hide_index=True,
    )


if __name__ == "__main__":
    run()
