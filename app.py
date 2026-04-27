import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="CMDB Unos", layout="centered")

st.title("📦 CMDB Unos")

# =========================
# DROPDOWNS
# =========================
DEPLOYMENT_STATES = ["In Use", "In Stock", "Retired", "Repair"]
INCIDENT_STATES = ["None", "Open", "Closed", "Pending"]
PROJECTS = ["Project A", "Project B", "Project C", "Other"]

# =========================
# LOAD MASTER (duplikati)
# =========================
@st.cache_data
def load_main():
    try:
        return pd.read_excel("data.xlsx")
    except:
        return pd.DataFrame()

main_df = load_main()

def exists(value, column):
    if main_df.empty:
        return False
    if column not in main_df.columns:
        return False
    return str(value) in main_df[column].astype(str).values

# =========================
# INPUT
# =========================
count = st.number_input("Broj uređaja", 1, 50, 1)

devices = []

for i in range(int(count)):
    st.markdown("---")
    st.subheader(f"📦 Uređaj {i+1}")

    # =========================
    # OBAVEZNA POLJA
    # =========================
    name = st.text_input("Name *", key=f"name{i}")
    model = st.text_input("Model *", key=f"model{i}")
    sp = st.text_input("SPInventoryNumber *", key=f"sp{i}")

    # =========================
    # OSTALA POLJA
    # =========================
    deployment = st.selectbox(
        "Deployment State",
        DEPLOYMENT_STATES,
        key=f"dep{i}"
    )

    incident = st.selectbox(
        "Incident State",
        INCIDENT_STATES,
        key=f"inc{i}"
    )

    vendor = st.text_input("Vendor", key=f"vendor{i}")
    type_ = st.text_input("Type", key=f"type{i}")
    serial = st.text_input("SerialNumber", key=f"serial{i}")
    inventory = st.text_input("InventoryNumber", key=f"inv{i}")

    project = st.selectbox(
        "Project",
        PROJECTS,
        key=f"proj{i}"
    )

    # =========================
    # VALIDACIJA
    # =========================
    if name and model and sp:

        if exists(sp, "SPInventoryNumber"):
            st.error("❌ SP već postoji")

        if serial and exists(serial, "SerialNumber"):
            st.error("❌ Serial već postoji")

        if inventory and exists(inventory, "InventoryNumber"):
            st.error("❌ Inventory već postoji")

        st.success("✔ OK")

        devices.append({
            "Name": name.strip(),
            "Model": model.strip(),
            "Type": type_,
            "Vendor": vendor,
            "SerialNumber": serial,
            "InventoryNumber": inventory,
            "SPInventoryNumber": sp.strip(),
            "Deployment State": deployment,
            "Incident State": incident,
            "Project": project
        })

    else:
        st.warning("⚠ Name, Model i SP su obavezni")

# =========================
# EXPORT
# =========================
if st.button("💾 Preuzmi Excel"):

    df = pd.DataFrame(devices)

    if df.empty:
        st.error("❌ Nema validnih uređaja")
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