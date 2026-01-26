import streamlit as st
import requests
import json

# ----------------------------
# Configuration
# ----------------------------
API_URL = "http://127.0.0.1:8000/predict"

st.set_page_config(
    page_title="Home Credit Risk Scoring Demo",
    layout="centered"
)

# ----------------------------
# Page Header
# ----------------------------
st.title("Home Credit Risk Scoring – Demo")
st.write(
    """
    This demo provides a simple user interface for credit officers to interact
    with the credit risk scoring API.
    
    The application sends a small set of input features to a FastAPI service
    and displays the predicted default probability, risk band, recommendation,
    and data quality indicators.
    """
)

# ----------------------------
# Input Section
# ----------------------------
st.header("Applicant Information (Partial Input)")

st.caption(
    "Only a subset of features is required. "
    "Missing system-level features will be automatically filled by the API."
)

ext1 = st.slider(
    "External Source 1 Score",
    min_value=0.0,
    max_value=1.0,
    value=0.5,
    step=0.01
)

ext2 = st.slider(
    "External Source 2 Score",
    min_value=0.0,
    max_value=1.0,
    value=0.7,
    step=0.01
)

ext3 = st.slider(
    "External Source 3 Score",
    min_value=0.0,
    max_value=1.0,
    value=0.2,
    step=0.01
)

income = st.number_input(
    "Annual Income (amt_income_total)",
    min_value=0,
    value=120000,
    step=1000
)

features = {
    "ext_source_1": ext1,
    "ext_source_2": ext2,
    "ext_source_3": ext3,
    "amt_income_total": income,
}

# ----------------------------
# Request Preview
# ----------------------------
st.subheader("Request Payload")
st.code(
    json.dumps({"features": features}, indent=2),
    language="json"
)

# ----------------------------
# API Call
# ----------------------------
if st.button("Run Credit Risk Scoring"):
    try:
        response = requests.post(
            API_URL,
            json={"features": features},
            timeout=10
        )

        if response.status_code != 200:
            st.error(
                f"API returned an error ({response.status_code}): {response.text}"
            )
        else:
            data = response.json()

            st.success("Scoring completed successfully")

            # ----------------------------
            # Results
            # ----------------------------
            st.header("Scoring Results")

            st.metric(
                label="Default Probability (PD)",
                value=f"{data['default_probability_pct']} %"
            )

            st.write("**Risk Band:**", data.get("risk_band"))
            st.write("**Recommendation:**", data.get("recommendation"))
            st.write("**Data Quality:**", data.get("data_quality"))

            with st.expander("Auto-filled (Missing) Features"):
                st.write(data.get("missing_features", []))

            with st.expander("Raw API Response"):
                st.json(data)

    except Exception as e:
        st.error(f"Failed to connect to API: {e}")
        st.info(
            "Make sure the FastAPI service is running:\n"
            "`uv run uvicorn api.main:app --reload`"
        )
