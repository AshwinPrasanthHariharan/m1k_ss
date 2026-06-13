import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go #added by neeraj
import time
import requests
# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
url = "http://localhost:8000/"
st.set_page_config(layout="wide")

page = st.sidebar.radio(
    "Select Page",
    ["DC Sweep", "Bode Plot"]
)

if page == "Bode Plot":
    st.title("Bode Plot")
    st.markdown("Use the ADALM1000 backend to sweep frequency and plot magnitude + phase.")

    in_ch = st.sidebar.selectbox(
        "Input channel",
        ["A", "B"],
        index=0
    )
    out_ch = st.sidebar.selectbox(
        "Output channel",
        ["B", "A"],
        index=0
    )

    if in_ch == out_ch:
        st.sidebar.error("Input and output channels must be different.")

    f_start = st.sidebar.number_input(
        "Start frequency (Hz)",
        value=10.0,
        min_value=0.1,
        step=1.0,
        format="%.2f"
    )
    f_end = st.sidebar.number_input(
        "End frequency (Hz)",
        value=1000.0,
        min_value=0.1,
        step=1.0,
        format="%.2f"
    )
    points = st.sidebar.number_input(
        "Sweep points",
        value=20,
        min_value=3,
        max_value=200,
        step=1
    )

    run_button = st.sidebar.button("Run Bode Sweep")

    if not run_button:
        st.info("Configure Bode sweep settings and press Run Bode Sweep.")
        st.stop()

    freq_list = np.logspace(
        np.log10(max(f_start, 0.1)),
        np.log10(max(f_end, f_start + 0.1)),
        num=points
    )

    status_placeholder = st.empty()
    mag_placeholder = st.empty()
    phase_placeholder = st.empty()
    table_placeholder = st.empty()

    freq_live = []
    mag_live = []
    phase_live = []

    for f in freq_list:
        status_placeholder.markdown(f"### Sweeping {f:.3f} Hz")

        try:
            response = requests.get(f"{url}pulse/{in_ch}/{out_ch}/{f}")
            response.raise_for_status()
            data = response.json()
            mag_db = data.get("magnitude_db", np.nan)
            phase_deg = data.get("phase_deg", np.nan)
        except Exception as e:
            mag_db = np.nan
            phase_deg = np.nan
            st.error(f"Sweep error at {f:.3f} Hz: {e}")

        freq_live.append(f)
        mag_live.append(mag_db)
        phase_live.append(phase_deg)

        mag_fig = go.Figure()
        mag_fig.add_trace(
            go.Scatter(
                x=freq_live,
                y=mag_live,
                mode="lines+markers",
                name="Magnitude (dB)"
            )
        )
        mag_fig.update_layout(
            title="Bode Magnitude",
            xaxis=dict(title="Frequency (Hz)", type="log"),
            yaxis=dict(title="Magnitude (dB)"),
            template="plotly_dark"
        )

        phase_fig = go.Figure()
        phase_fig.add_trace(
            go.Scatter(
                x=freq_live,
                y=phase_live,
                mode="lines+markers",
                name="Phase (deg)",
                marker_color="orange"
            )
        )
        phase_fig.update_layout(
            title="Bode Phase",
            xaxis=dict(title="Frequency (Hz)", type="log"),
            yaxis=dict(title="Phase (deg)"),
            template="plotly_dark"
        )

        mag_placeholder.plotly_chart(mag_fig, use_container_width=True)
        phase_placeholder.plotly_chart(phase_fig, use_container_width=True)

        table_placeholder.dataframe(
            pd.DataFrame({
                "Frequency (Hz)": freq_live,
                "Magnitude (dB)": mag_live,
                "Phase (deg)": phase_live,
            })
        )

        time.sleep(0.15)

    status_placeholder.markdown("### Sweep complete")
    st.stop()

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


        vin_live.append(current_vin)
        requests.get(url+"sva/"+str(current_vin))
        time.sleep(0.1)
        response = requests.get(url+"rvb")
        if response.status_code == 200:
            current_vout = response.json().get("channel_b", 0.0)
        else:
            current_vout = 0.0  # Default to 0 if there's an error  

        vout_live.append(current_vout)

        # ------------------------------------------
        # CREATE NEW FIGURE EACH LOOP
        # ------------------------------------------

        # fig, ax = plt.subplots(
        #     figsize=(10, 6)
        # )

        # ax.scatter(
        #     vin_live,
        #     vout_live,
        #     s=80
        # )

        # ax.set_title(
        #     "Live DC Sweep Characterization"
        # )

        # ax.set_xlabel(
        #     "Vin (V)"
        # )

        # ax.set_ylabel(
        #     "Vout (V)"
        # )

        # ax.set_xlim(
        #     v_start,
        #     v_end
        # )

        # ax.set_ylim(
        #     np.min(vout_array) - 0.5,
        #     np.max(vout_array) + 0.5
        # )

        # plot_placeholder.pyplot(fig)

        # ------------------------------------------
        # STATUS
        # ------------------------------------------

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=vin_live,
                y=vout_live,
                mode="lines+markers",
                name="DC Sweep"
            )
        )

        fig.update_layout(

            title="Live DC Sweep Characterization",

            xaxis=dict(
                title="Vin (V)",
                range=[v_start, v_end]
            ),

            yaxis=dict(
                title="Vout (V)",
                range=[
                    0,5
                ]
            ),

            template="plotly_dark"
        )

        plot_placeholder.plotly_chart(
            fig,
            use_container_width=True
        )

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

        #plt.close(fig) //modified by neeraj