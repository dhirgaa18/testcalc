import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

st.title("Aplikasi Perhitungan Konsentrasi Sampel dan Kurva Kalibrasi")

st.header("1. Input Data Kalibrasi")
st.write("Masukkan data kalibrasi (konsentrasi dan absorbansi):")

calib_data = st.text_area("Contoh format:\nKonsentrasi,Absorbansi\n1,0.12\n2,0.23\n3,0.35", height=200)

if calib_data:
    try:
        df_calib = pd.read_csv(pd.compat.StringIO(calib_data))
        df_calib.columns = ["Konsentrasi", "Absorbansi"]

        # Regresi linier
        X = df_calib["Konsentrasi"].values.reshape(-1, 1)
        y = df_calib["Absorbansi"].values
        model = LinearRegression()
        model.fit(X, y)

        slope = model.coef_[0]
        intercept = model.intercept_
        r_squared = r2_score(y, model.predict(X))

        st.success("Regresi Linier Berhasil:")
        st.write(f"**Slope (m)** = {slope:.4f}")
        st.write(f"**Intercept (b)** = {intercept:.4f}")
        st.write(f"**R²** = {r_squared:.4f}")

        # Plot
        st.subheader("Kurva Kalibrasi")
        fig, ax = plt.subplots()
        ax.scatter(df_calib["Konsentrasi"], df_calib["Absorbansi"], color='blue', label='Data Kalibrasi')
        ax.plot(df_calib["Konsentrasi"], model.predict(X), color='red', label='Regresi Linier')
        ax.set_xlabel("Konsentrasi")
        ax.set_ylabel("Absorbansi")
        ax.legend()
        st.pyplot(fig)

        # Input sampel
        st.header("2. Hitung Konsentrasi Sampel")
        absorbansi_sample = st.text_input("Masukkan absorbansi sampel (pisahkan dengan koma):", "0.15, 0.21")

        try:
            absorbansi_list = [float(a) for a in absorbansi_sample.split(",")]
            konsentrasi_sample = [(a - intercept) / slope for a in absorbansi_list]

            df_sample = pd.DataFrame({
                "Absorbansi Sampel": absorbansi_list,
                "Konsentrasi Terhitung": konsentrasi_sample
            })

            st.write("Hasil Konsentrasi Sampel:")
            st.dataframe(df_sample)

            # Akurasi (jika nilai aktual tersedia)
            st.header("3. Perhitungan Akurasi dan RPD")
            known_values = st.text_input("Masukkan konsentrasi sebenarnya (pisahkan dengan koma):", "")
            if known_values:
                known_list = [float(x) for x in known_values.split(",")]
                if len(known_list) == len(konsentrasi_sample):
                    recovery = [100 * found / known for found, known in zip(konsentrasi_sample, known_list)]
                    rpd = (np.std(konsentrasi_sample, ddof=1) / np.mean(konsentrasi_sample)) * 100

                    df_sample["Konsentrasi Aktual"] = known_list
                    df_sample["Recovery (%)"] = recovery
                    st.write("Hasil Evaluasi:")
                    st.dataframe(df_sample)

                    st.success(f"RPD = {rpd:.2f}%")
                else:
                    st.warning("Jumlah data aktual tidak sama dengan jumlah sampel.")

        except:
            st.error("Format absorbansi salah atau tidak bisa dihitung.")

    except:
        st.error("Format data kalibrasi salah. Pastikan format CSV benar.")
