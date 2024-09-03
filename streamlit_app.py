import datetime

import streamlit as st

import carbon_intensity_data

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
        st.metric(f'{st.session_state.postcode} current carbon intensity', current_intensity)

        forecast_intensity = carbon_intensity_data.get_forward_intensity(st.session_state.postcode, datetime.datetime.now())
        st.line_chart(forecast_intensity, x='from', y='forecast', color='#60f0f8')


if __name__ == '__main__':
    run()
