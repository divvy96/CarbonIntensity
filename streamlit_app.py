import datetime

import streamlit as st

import carbon_intensity_data

def find_minimum_carbon_window(df):
    """returns the start of period with the lowest mean carbon intensity"""

    WINDOW_SIZE = 4
    window_average = df['forecast'].rolling(WINDOW_SIZE).mean()

    return df.loc[window_average.idxmin() - WINDOW_SIZE, 'from']


def run():
    """app that displays some metrics about electricty generation in the uk"""


    st.set_page_config(page_title='electricity genration uk')

    st.title("electricity genration uk")

    st.text_input('Enter postcode for current carbon intensity of your region', key='postcode')

    if st.session_state.postcode == '':
        current_intensity = carbon_intensity_data.get_current_intensity()
        st.metric('uk current carbon intensity', current_intensity)

    else:
        current_intensity = carbon_intensity_data.get_current_postcode_intensity(st.session_state.postcode)
        forecast_intensity = carbon_intensity_data.get_forward_intensity(st.session_state.postcode, datetime.datetime.now())

        col1, col2 = st.columns(2)
        col1.metric(f'{st.session_state.postcode} current carbon intensity', current_intensity)
        col2.metric(f'best time to charge car is: ', find_minimum_carbon_window(forecast_intensity).strftime('%a %d-%b @ %H:%M'))
        st.line_chart(forecast_intensity, x='from', y='forecast', color='#60f0f8')


if __name__ == '__main__':
    run()
