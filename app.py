import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="CMDB Batch Unos", layout="centered")

st.title("📦 CMDB Batch Unos")

# =========================
# LOAD MASTER EXCEL
# =========================
@st.cache_data
def load_main():
    try:
        return pd.read_excel("data.xlsx")
    except:
        return pd.DataFrame()

main_df = load_main()

# =========================
# DUPLIKAT CHECK
# =========================
def exists(value, column):
    if main_df.empty:
        return False
    if column not in main_df.columns:
        return False
    return str(value) in main_df[column].astype(str).values

# =========================
# BATCH INPUT
# =========================
count = st.number_input("Broj uređaja", min_value=1, max_value=50, value=1)

devices = []

for i in range(int(count)):
    st.markdown("---")
    st.subheader(f"📦 Uređaj {i+1}")

    name = st.text_input("Name", key=f"name{i}")
    model = st.text_input("Model", key=f"model{i}")
    type_ = st.text_input("Type", key=f"type{i}")
    vendor = st.text_input("Vendor", key=f"vendor{i}")

    serial = st.text_input("SerialNumber", key=f"serial{i}")
    inventory = st.text_input("InventoryNumber", key=f"inv{i}")
    sp = st.text_input("SPInventoryNumber", key=f"sp{i}")

    # =========================
    # LIVE VALIDATION
    # =========================
    if serial:
        if exists(serial, "SerialNumber"):
            st.error("❌ Serial već postoji")
        else:
            st.success("✔ Serial OK")

    if inventory:
        if exists(inventory, "InventoryNumber"):
            st.error("❌ Inventory već postoji")
        else:
            st.success("✔ Inventory OK")

    if sp:
        if exists(sp, "SPInventoryNumber"):
            st.error("❌ SP već postoji")
        else:
            st.success("✔ SP OK")

    # =========================
    # SAVE ROW
    # =========================
    if name or inventory:
        devices.append({
            "Name": name,
            "Model": model,
            "Type": type_,
            "Vendor": vendor,
            "SerialNumber": serial,
            "InventoryNumber": inventory,
            "SPInventoryNumber": sp
        })

# =========================
# EXPORT
# =========================
if st.button("💾 Generiši Excel"):

    df = pd.DataFrame(devices)

    if df.empty:
        st.error("❌ Nema unetih uređaja")
    else:
        output = BytesIO()

        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="CMDB")

        st.success(f"✅ Uređaja uneto: {len(df)}")

        st.download_button(
            "📥 Preuzmi Excel",
            data=output.getvalue(),
            file_name="cmdb_batch.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )