import streamlit as st
import pandas as pd
import os
from io import BytesIO

st.set_page_config(page_title="CMDB Unos", layout="centered")

st.title("➕ CMDB Unos uređaja")

# =========================
# LOAD MASTER EXCEL
# =========================
@st.cache_data
def load_main():
    if os.path.exists("data.xlsx"):
        return pd.read_excel("data.xlsx")
    else:
        st.error("❌ Nedostaje data.xlsx (master baza)")
        return pd.DataFrame()

main_df = load_main()

# =========================
# FUNKCIJA PROVERE
# =========================
def exists(value, column):
    if main_df.empty:
        return False
    if column not in main_df.columns:
        return False
    return str(value) in main_df[column].astype(str).values

# =========================
# FORMA
# =========================
with st.form("unos_forma"):

    name = st.text_input("Name")
    model = st.text_input("Model")
    type_ = st.text_input("Type")
    vendor = st.text_input("Vendor")

    serial = st.text_input("SerialNumber")
    inventory = st.text_input("InventoryNumber")
    sp = st.text_input("SPInventoryNumber")

    status = st.selectbox("Status", ["Aktivan", "Na servisu", "Otpisan"])

    submit = st.form_submit_button("💾 Sačuvaj i preuzmi")

# =========================
# VALIDACIJA + EXPORT
# =========================
if submit:

    # obavezna polja
    if not inventory or not sp:
        st.error("❌ Inventory i SP su obavezni!")

    # duplikati
    elif serial and exists(serial, "SerialNumber"):
        st.error("❌ Serial već postoji u CMDB!")

    elif exists(inventory, "InventoryNumber"):
        st.error("❌ Inventory već postoji u CMDB!")

    elif exists(sp, "SPInventoryNumber"):
        st.error("❌ SP već postoji u CMDB!")

    else:
        new_row = pd.DataFrame([{
            "Name": name,
            "Model": model,
            "Type": type_,
            "Vendor": vendor,
            "SerialNumber": serial,
            "InventoryNumber": inventory,
            "SPInventoryNumber": sp,
            "Status": status
        }])

        # =========================
        # EXPORT EXCEL (DOWNLOAD)
        # =========================
        output = BytesIO()

        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            new_row.to_excel(writer, index=False, sheet_name="NoviUredjaj")

        st.success("✅ Uređaj prošao validaciju!")

        st.download_button(
            "📥 Preuzmi Excel",
            data=output.getvalue(),
            file_name=f"cmdb_{inventory}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )