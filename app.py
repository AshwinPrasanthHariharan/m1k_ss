import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
import requests
# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
url = "http://localhost:8000/"
st.set_page_config(layout="wide")
st.title("ADALM1000 DC Sweep Signal Analysis")

st.markdown(
    "Live DC Sweep Characterization"
)

# --------------------------------------------------
# SIDEBAR INPUTS
# --------------------------------------------------

st.sidebar.markdown("## DC SWEEP SETTINGS")

v_start = st.sidebar.number_input(
    "V Start (V)",
    value=0.0,
    step=0.1
)

v_end = st.sidebar.number_input(
    "V End (V)",
    value=5.0,
    step=0.1
)

v_step = st.sidebar.number_input(
    "Step Size (V)",
    value=0.1,
    step=0.1,
    min_value=0.1
)

run_button = st.sidebar.button(
    "Run DC Sweep"
)

# --------------------------------------------------
# DATA
# --------------------------------------------------

vin_array = np.arange(
    v_start,
    v_end + v_step,
    v_step
)

vout_array = (
    0.65 * vin_array + 0.15
)

# --------------------------------------------------
# READY SCREEN
# --------------------------------------------------

if not run_button:

    st.info(
        "Configure sweep parameters and press Run DC Sweep"
    )

# --------------------------------------------------
# RUN SWEEP
# --------------------------------------------------

else:

    plot_placeholder = st.empty()

    table_placeholder = st.empty()

    status_placeholder = st.empty()

    vin_live = []

    vout_live = []

    for i in range(len(vin_array)):

        current_vin = vin_array[i]

        current_vout = vout_array[i]

        vin_live.append(current_vin)
        requests.get(url+"sva/"+str(current_vin))
        time.sleep(0.1)
        response = requests.get(url+"rva")
        if response.status_code == 200:
            current_vout = response.json().get("channel_a", 0.0)
        else:
            current_vout = 0.0  # Default to 0 if there's an error  

        vout_live.append(current_vout)

        # ------------------------------------------
        # CREATE NEW FIGURE EACH LOOP
        # ------------------------------------------

        fig, ax = plt.subplots(
            figsize=(10, 6)
        )

        ax.scatter(
            vin_live,
            vout_live,
            s=80
        )

        ax.set_title(
            "Live DC Sweep Characterization"
        )

        ax.set_xlabel(
            "Vin (V)"
        )

        ax.set_ylabel(
            "Vout (V)"
        )

        ax.set_xlim(
            v_start,
            v_end
        )

        ax.set_ylim(
            np.min(vout_array) - 0.5,
            np.max(vout_array) + 0.5
        )

        plot_placeholder.pyplot(fig)

        # ------------------------------------------
        # STATUS
        # ------------------------------------------

        status_placeholder.markdown(
            f"""
            ### Acquisition Running

            **Current Vin:** {current_vin:.2f} V  
            **Measured Vout:** {current_vout:.2f} V
            """
        )

        # ------------------------------------------
        # TABLE
        # ------------------------------------------

        df = pd.DataFrame({
            "Vin (V)": vin_live,
            "Vout (V)": vout_live
        })

        table_placeholder.dataframe(
            df,
            width="stretch"
        )

        time.sleep(0.15)

        plt.close(fig)