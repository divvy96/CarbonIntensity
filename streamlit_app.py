import datetime

import altair as alt
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


def area_chart(banding_df) -> alt.Chart:
    """returns banding chart for intensity levels"""

    chart = (alt.Chart(banding_df).
             mark_area(opacity=0.25).
             encode(
                 x='from:T',
                 y='lower_bound:Q',
                 y2='upper_bound:Q',
                 color=alt.Color('color:N', scale=None)
                 )
             )

    return chart


def run():
    """app that displays some metrics about electricty generation in the uk"""

    st.set_page_config(page_title="electricity generation uk")

    st.title("UK Carbon Intensity Forecast")
    st.subheader("Find the best times to use electricty to minimise gCO₂/kWh")

    st.text_input(
        "Enter postcode for current carbon intensity of your region", key="postcode"
    )

    intensity_banding_df = carbon_intensity_data.intensity_bands()
    st.dataframe(
        data=intensity_banding_df[['intensity', 'upper_bound']],
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
                    label=f"current carbon intensity {st.session_state.postcode}",
                    value=f"{current_intensity} gCO₂/kWh",
                    delta=f"{(int(current_intensity - forecast_intensity['forecast'].mean()))} vs avg",
                    delta_color='inverse'
                )

            with col2:

                st.caption(f"best time to charge car is:")
                st.markdown(
                    f'## {find_minimum_carbon_window(forecast_intensity).strftime("%a %d-%b @ %H:%M")}'
                )

        if isinstance(forecast_intensity, pandas.DataFrame):

            # shouldn't use itertuples, maybe replace with matrix product
            banding_charts = []
            for row in intensity_banding_df.itertuples(index=False):
                banding_area_chart = area_chart(pandas.DataFrame(
                    [{'from': forecast_intensity['from'].min(),
                      'lower_bound': row.lower_bound,
                      'upper_bound': row.upper_bound,
                      'color': row.color},
                     {'from': forecast_intensity['from'].max(),
                      'lower_bound': row.lower_bound,
                       'upper_bound': row.upper_bound,
                       'color': row.color}]
                ))
                banding_charts.append(banding_area_chart)

            banding_charts = alt.layer(*banding_charts)

            forecast_chart = (
                alt.Chart(forecast_intensity)
                .mark_line()
                .encode(x='from:T', y='forecast:Q')
            )

            final_chart = forecast_chart + banding_charts
            st.altair_chart(final_chart, use_container_width=True)
        else:
            st.write(f"unable to find postcode {st.session_state.postcode}")


if __name__ == "__main__":
    run()
