# app.py
import streamlit as st
import datetime as dt
import requests
import pandas as pd

st.set_page_config(page_title="TaxiFareModel front", page_icon="🚕")
st.title("TaxiFareModel front")
st.caption("Streamlit UI → call a prediction API and show the fare")

# 1) Where is your API?
api_url = st.text_input(
    "Prediction API URL",
    value="https://taxifare.lewagon.ai/predict",
    help="Use your own FastAPI endpoint if you have one. Open /docs on that URL to see the exact parameter names and method."
)

# 2) User inputs
with st.form("fare_form"):
    cdt1, cdt2, cpass = st.columns([1, 1, 1])
    with cdt1:
        pickup_date = st.date_input("Pickup date", value=dt.date(2013, 7, 6))
    with cdt2:
        pickup_time = st.time_input("Pickup time", value=dt.time(17, 18))
    with cpass:
        passenger_count = st.number_input("Passenger count", min_value=1, max_value=8, value=1, step=1)

    c1, c2 = st.columns(2)
    with c1:
        pickup_longitude = st.number_input("Pickup longitude", value=-73.985428, format="%.6f", min_value=-180.0, max_value=180.0)
        pickup_latitude  = st.number_input("Pickup latitude",  value=40.748817,  format="%.6f", min_value=-90.0,  max_value=90.0)
    with c2:
        dropoff_longitude = st.number_input("Dropoff longitude", value=-73.985664, format="%.6f", min_value=-180.0, max_value=180.0)
        dropoff_latitude  = st.number_input("Dropoff latitude",  value=40.748441,  format="%.6f", min_value=-90.0,  max_value=90.0)

    submitted = st.form_submit_button("Predict fare 🚕")

# 3) Build payload and call the API
if submitted:
    pickup_datetime = dt.datetime.combine(pickup_date, pickup_time).strftime("%Y-%m-%d %H:%M:%S")

    params = {
        "pickup_datetime": pickup_datetime,
        "pickup_longitude": float(pickup_longitude),
        "pickup_latitude": float(pickup_latitude),
        "dropoff_longitude": float(dropoff_longitude),
        "dropoff_latitude": float(dropoff_latitude),
        "passenger_count": int(passenger_count),
    }

    with st.expander("Request payload (debug)"):
        st.json(params)

    try:
        with st.spinner("Calling prediction API..."):
            # Many FastAPI examples use GET with query params; if that fails, try POST+JSON
            r = requests.get(api_url, params=params, timeout=10)
            if r.status_code >= 400:
                r = requests.post(api_url, json=params, timeout=10)
            r.raise_for_status()
            data = r.json()

        # 4) Extract the fare from common key names
        fare = None
        for k in ("fare_amount", "fare", "prediction", "pred"):
            if k in data:
                fare = data[k]
                break

        if fare is not None:
            st.success(f"Estimated fare: **${float(fare):.2f}**")
        else:
            st.warning("The API responded, but I couldn't find the fare in the JSON. Here it is:")
            st.json(data)

        # Optional: quick map of pickup/dropoff
        points = pd.DataFrame(
            [{"lat": pickup_latitude, "lon": pickup_longitude},
             {"lat": dropoff_latitude, "lon": dropoff_longitude}]
        )
        st.map(points)

    except requests.RequestException as e:
        st.error(f"API call failed: {e}")
        st.info("Tip: open your API’s /docs to confirm the method (GET vs POST) and parameter names.")
