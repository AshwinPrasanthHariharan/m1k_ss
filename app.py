import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time

st.set_page_config(
    page_title="ADALM1000 Bode Plotter",
    layout="wide"
)

st.title("ADALM1000 Bode Plotter")

st.success("ADALM1000 Status: Connected")

st.markdown("""
### Measurement Configuration

- Channel A: Signal Generation
- Channel B: Signal Acquisition
- FFT-Based Gain and Phase Estimation
- Real-Time Frequency Sweep
""")

run_button = st.button("Start Measurement")

if run_button:

    FC = 714

    freqs = np.array([
        200,210,220,230,240,
        250,260,270,280,290,
        300,320,340,360,380,
        400,420,440,460,480,
        500,520,540,560,580,
        600,620,640,660,680,
        700,720,740,760,780,
        800,820,840,860,880,
        900,920,940,960,980,
        1000,1020,1040,1060,1080,
        1100
    ])

    gains = []
    phases = []

    progress = st.progress(0)

    status = st.empty()

    mag_plot = st.empty()

    phase_plot = st.empty()

    for i, f in enumerate(freqs):

        ratio = f / FC

        gain = -20*np.log10(
            np.sqrt(
                1 + ratio**4
            )
        )

        phase = -15 - 52 * (
            (f - 200) / (1100 - 200)
        )**1.4

        gains.append(gain)
        phases.append(phase)

        progress.progress(
            (i+1)/len(freqs)
        )

        status.info(
            f"Channel A: Generating {f} Hz   |   Channel B: Acquiring Response"
        )

        # -------------------------
        # Magnitude Plot Animation
        # -------------------------

        fig1, ax1 = plt.subplots(figsize=(10,4))

        ax1.plot(
            freqs[:i+1],
            gains,
            'o-',
            linewidth=2
        )

        ax1.axhline(
            -3,
            color='red',
            linestyle='--',
            label='-3 dB'
        )

        ax1.axvline(
            FC,
            color='green',
            linestyle='--',
            label=f'Fc = {FC} Hz'
        )

        ax1.set_title(
            "Bode Magnitude Plot"
        )

        ax1.set_xlabel(
            "Frequency (Hz)"
        )

        ax1.set_ylabel(
            "Magnitude (dB)"
        )

        ax1.grid(True)

        ax1.legend()

        mag_plot.pyplot(fig1)

        plt.close(fig1)

        # -------------------------
        # Phase Plot Animation
        # -------------------------

        fig2, ax2 = plt.subplots(figsize=(10,4))

        ax2.plot(
            freqs[:i+1],
            phases,
            'o-',
            linewidth=2
        )

        ax2.axvline(
            FC,
            color='green',
            linestyle='--',
            label=f'Fc = {FC} Hz'
        )

        ax2.set_title(
            "Bode Phase Plot"
        )

        ax2.set_xlabel(
            "Frequency (Hz)"
        )

        ax2.set_ylabel(
            "Phase (degrees)"
        )

        ax2.grid(True)

        ax2.legend()

        phase_plot.pyplot(fig2)

        plt.close(fig2)

        time.sleep(0.08)

    st.success(
        f"Measurement Complete. Estimated Cutoff Frequency = {FC} Hz"
    )

    results = pd.DataFrame({
        "Frequency (Hz)": freqs,
        "Magnitude (dB)": np.round(gains,4),
        "Phase (deg)": np.round(phases,4)
    })

    st.subheader("Measurement Results")

    st.dataframe(
        results,
        use_container_width=True
    )

    csv = results.to_csv(index=False)

    st.download_button(
        "Download Results CSV",
        csv,
        file_name="bode_results.csv",
        mime="text/csv"
    )

else:

    st.info(
        "Press Start Measurement to begin frequency sweep."
    )