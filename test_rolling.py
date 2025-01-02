import datetime

import pandas

import streamlit_app


def test_first_rolling_window():
    intensity = [125, 125, 150, 150, 155]
    from_dates = pandas.date_range("2025-01-01 12:00:00", periods=5, freq="30min")

    df = pandas.DataFrame(
        {"forecast": intensity, "from": pandas.to_datetime(from_dates)}
    )

    min_start_time = streamlit_app.find_minimum_carbon_window(df)

    expected_result = pandas.to_datetime("2025-01-01 12:00:00")

    assert expected_result == min_start_time


def test_last_rolling_window():
    intensity = [200, 125, 150, 150, 155]
    from_dates = pandas.date_range("2025-01-01 12:00:00", periods=5, freq="30min")

    df = pandas.DataFrame(
        {"forecast": intensity, "from": pandas.to_datetime(from_dates)}
    )

    min_start_time = streamlit_app.find_minimum_carbon_window(df)

    expected_result = pandas.to_datetime("2025-01-01 12:30:00")

    assert expected_result == min_start_time
