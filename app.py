import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="CMDB Unos", layout="centered")

st.title("📦 CMDB Unos")

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
# BROJ UREĐAJA
# =========================
count = st.number_input("Broj uređaja", min_value=1, max_value=50, value=1)

devices = []

# =========================
# INPUT LOOP
# =========================
for i in range(int(count)):
    st.markdown("---")
    st.subheader(f"📦 Uređaj {i+1}")

    # OBAVEZNA POLJA
    name = st.text_input("Name *", key=f"name{i}")
    model = st.text_input("Model *", key=f"model{i}")
    sp = st.text_input("SPInventoryNumber *", key=f"sp{i}")

    # OPCIONALNA POLJA
    type_ = st.text_input("Type", key=f"type{i}")
    vendor = st.text_input("Vendor", key=f"vendor{i}")
    serial = st.text_input("SerialNumber", key=f"serial{i}")
    inventory = st.text_input("InventoryNumber", key=f"inv{i}")

    # =========================
    # VALIDACIJA OBAVEZNIH
    # =========================
    if name and model and sp:

        # duplikat check (SP najbitniji)
        if exists(sp, "SPInventoryNumber"):
            st.error("❌ SP već postoji u CMDB")

        if serial and exists(serial, "SerialNumber"):
            st.error("❌ Serial već postoji u CMDB")

        if inventory and exists(inventory, "InventoryNumber"):
            st.error("❌ Inventory već postoji u CMDB")

        st.success("✔ Uređaj OK")

        devices.append({
            "Name": name.strip(),
            "Model": model.strip(),
            "Type": type_.strip() if type_ else "",
            "Vendor": vendor.strip() if vendor else "",
            "SerialNumber": serial.strip() if serial else "",
            "InventoryNumber": inventory.strip() if inventory else "",
            "SPInventoryNumber": sp.strip()
        })

    else:
        st.warning("⚠ Name, Model i SP su obavezni")

# =========================
# EXPORT EXCEL
# =========================
if st.button("💾 Preuzmi Excel"):

    df = pd.DataFrame(devices)

    if df.empty:
        st.error("❌ Nema validnih uređaja za export")
    else:
        output = BytesIO()

        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="CMDB")

        st.success(f"✅ Export: {len(df)} uređaja")

        st.download_button(
            "📥 Download Excel",
            data=output.getvalue(),
            file_name="cmdb_unos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )