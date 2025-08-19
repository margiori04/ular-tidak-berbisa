import streamlit as st
import pandas as pd
from io import BytesIO

# -----------------------------
# Konfigurasi halaman & state
# -----------------------------
st.set_page_config(page_title="Alat Bantu Hitung LKM", layout="wide")

if 'rekap_df' not in st.session_state:
    st.session_state['rekap_df'] = None
if 'selected_tab' not in st.session_state:
    st.session_state['selected_tab'] = "📊 Input & Hitung"

# -----------------------------
# Custom CSS untuk tampilan mobile
# -----------------------------
st.markdown(
    """
    <style>
    body, div, p, label {
        font-size: 16px !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 20px;
    }
    div[role="radiogroup"] > label {
        background: #f5f5f5;
        border-radius: 10px;
        padding: 6px 12px;
        margin: 2px;
        cursor: pointer;
    }
    div[role="radiogroup"] > label:hover {
        background: #e0e0e0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Judul
# -----------------------------
st.markdown("## 🌐 Aplikasi Alat Bantu Hitung LKM & Rekap SubSLS")

# -----------------------------
# Navigasi dengan radio
# -----------------------------
tab_choice = st.radio(
    "Navigasi",
    ["📊 Input & Hitung", "📈 Rekap SubSLS"],
    index=0 if st.session_state['selected_tab'] == "📊 Input & Hitung" else 1,
    horizontal=True
)
st.session_state['selected_tab'] = tab_choice

# -----------------------------
# Fungsi Reset Session
# -----------------------------
def reset_session():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state['rekap_df'] = None
    st.session_state['selected_tab'] = "📊 Input & Hitung"

# -----------------------------
# TAB 1 : Input & Proses Hitung
# -----------------------------
if tab_choice == "📊 Input & Hitung":
    st.subheader("📝 Input Data Segmen")
    
    # Tombol Reset
    if st.button("🔄 Reset Semua Data"):
        reset_session()
        st.rerun()
    
    with st.container():
        jumlah_kk_sls = st.number_input("👨‍👩‍👧 Jumlah KK SLS:", min_value=1, step=1, key="jumlah_kk_sls")
        jumlah_segmen = st.number_input("📦 Jumlah Segmen:", min_value=1, step=1, key="jumlah_segmen")

    segment_data = []
    if jumlah_kk_sls and jumlah_segmen:
        st.markdown("### 📂 Data per Segmen")

        for i in range(int(jumlah_segmen)):
            with st.expander(f"📌 Segmen {i+1}", expanded=False):
                # Input otomatis tersimpan di session_state dengan key unik
                st.number_input("BTT", min_value=0, step=1, key=f"btt_{i}")
                st.number_input("BTT Kosong", min_value=0, step=1, key=f"btt_kosong_{i}")
                st.number_input("BKU", min_value=0, step=1, key=f"bku_{i}")
                st.number_input("BBTT Non Usaha", min_value=0, step=1, key=f"bbtt_{i}")
                st.number_input("Perkiraan Muatan Usaha", min_value=0, step=1, key=f"muatan_usaha_{i}")

                # Ambil dari state supaya nilai tidak hilang
                segment_data.append({
                    "Segmen": i+1,
                    "BTT": st.session_state.get(f"btt_{i}", 0),
                    "BTT Kosong": st.session_state.get(f"btt_kosong_{i}", 0),
                    "BKU": st.session_state.get(f"bku_{i}", 0),
                    "BBTT Non Usaha": st.session_state.get(f"bbtt_{i}", 0),
                    "Perkiraan Muatan Usaha": st.session_state.get(f"muatan_usaha_{i}", 0),
                })

    # Tombol proses hitung → hasil disimpan ke session_state
    if st.button("🚀 Proses Penghitungan"):
        total_btt = sum([seg['BTT'] for seg in segment_data]) or 1
        rekap_data = []
        for seg in segment_data:
            jumlah_perkiraan_kk = int(round((seg["BTT"]/total_btt) * jumlah_kk_sls)) if total_btt else 0
            total_muatan = max(
                jumlah_perkiraan_kk,
                seg["BTT"] + seg["BTT Kosong"] + seg["BBTT Non Usaha"] + seg["Perkiraan Muatan Usaha"]
            )
            rekap_data.append({
                "Segmen": seg["Segmen"],
                "Perkiraan KK": jumlah_perkiraan_kk,
                "BTT": seg["BTT"],
                "BTT Kosong": seg["BTT Kosong"],
                "BKU": seg["BKU"],
                "BBTT Non Usaha": seg["BBTT Non Usaha"],
                "Perkiraan Muatan Usaha": seg["Perkiraan Muatan Usaha"],
                "Total Muatan": total_muatan,
            })

        st.session_state['rekap_df'] = pd.DataFrame(rekap_data)

    # Tampilkan tabel rekap bila sudah diproses
    if st.session_state['rekap_df'] is not None:
        df_rekap = st.session_state['rekap_df']
        st.markdown("### 📋 Hasil Per Segmen")

        subsls_list = []
        for i, row in df_rekap.iterrows():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.json(row.to_dict())  # tampilkan lebih rapih di mobile
            with col2:
                subsls = st.number_input(
                    f"Subsls {row['Segmen']}",
                    min_value=1, step=1, key=f"subsls_{i}"
                )
                subsls_list.append(subsls)

        # update dataframe dengan Subsls
        df_rekap["Subsls"] = subsls_list
        st.session_state['rekap_df'] = df_rekap

        # jika semua subsls sudah diisi, tampilkan tombol lanjut
        if all(x > 0 for x in subsls_list):
            if st.button("➡️ Lanjut ke Rekap SubSLS"):
                st.session_state['selected_tab'] = "📈 Rekap SubSLS"
                #st.rerun()

# -----------------------------
# TAB 2 : Rekap SubSLS
# -----------------------------
if tab_choice == "📈 Rekap SubSLS":
    st.subheader("📈 Rekapitulasi SubSLS")

    if st.session_state['rekap_df'] is not None:
        df = st.session_state['rekap_df']

        # Agregasi per SubSLS
        df_subsls = df.groupby("Subsls").agg({
            "Perkiraan KK": "sum",
            "BTT": "sum",
            "BTT Kosong": "sum",
            "BKU": "sum",
            "BBTT Non Usaha": "sum",
            "Perkiraan Muatan Usaha": "sum",
            "Total Muatan": "sum"
        }).reset_index()

        st.dataframe(df_subsls, use_container_width=True)

        # Total keseluruhan dengan metrics
        total_muatan = df_subsls["Total Muatan"].sum()
        total_kk = df_subsls["Perkiraan KK"].sum()

        c1, c2 = st.columns(2)
        c1.metric("👨‍👩‍👧 Total KK", f"{total_kk:,}")
        c2.metric("📦 Total Muatan", f"{total_muatan:,}")

        # --- Export Fitur ---
        st.markdown("### 💾 Export Data")

        # Export ke CSV
        #csv = df_subsls.to_csv(index=False).encode("utf-8")
        #st.download_button("⬇️ Download CSV", data=csv, file_name="rekap_subsls.csv", mime="text/csv")

        # Export ke Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name="Rekap Segmen", index=False)
            df_subsls.to_excel(writer, sheet_name="Rekap SubSLS", index=False)
        excel_data = output.getvalue()

        st.download_button(
            label="⬇️ Download Excel",
            data=excel_data,
            file_name="rekap_subsls.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # Tombol kembali
        if st.button("⬅️ Kembali ke Input"):
            st.session_state['selected_tab'] = "📊 Input & Hitung"
            #st.rerun()

    else:
        st.info("⚠️ Silakan lakukan pengisian & rekapitulasi di tab pertama dahulu")
