import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="CMDB Unos", layout="centered")

st.title("📦 CMDB Unos")

# =========================
# DROPDOWNS
# =========================
DEPLOYMENT_STATES = ["Functional", "Malfunctioned", "Retired"]
INCIDENT_STATES = ["Operational", "Incident"]

PROJECTS_MAP = {
    "107 Tendam": "107",
    "108 Deichmann": "108",
    "109 Takko": "109",
    "112 Mercator-S": "112",
    "115 H&M": "115",
    "118 Metre Cash & Carry": "118",
    "119 Ikea": "119",
    "123 Decathlon": "123",
    "193 Lidl": "193"
}

PROJECTS_LABELS = list(PROJECTS_MAP.keys())

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

    deployment = st.selectbox(
        "Deployment State *",
        DEPLOYMENT_STATES,
        key=f"dep{i}"
    )

    incident = st.selectbox(
        "Incident State *",
        INCIDENT_STATES,
        key=f"inc{i}"
    )

    project_label = st.selectbox(
        "Project *",
        PROJECTS_LABELS,
        key=f"proj{i}"
    )

    project_value = PROJECTS_MAP[project_label]

    # =========================
    # OSTALA POLJA
    # =========================
    vendor = st.text_input("Vendor", key=f"vendor{i}")
    type_ = st.text_input("Type", key=f"type{i}")
    serial = st.text_input("SerialNumber", key=f"serial{i}")
    inventory = st.text_input("InventoryNumber", key=f"inv{i}")

    # =========================
    # VALIDACIJA (STRICT)
    # =========================
    if name and model and sp and deployment and incident and project_value:

        # duplikati
        if exists(sp, "SPInventoryNumber"):
            st.error("❌ SP već postoji")

        if serial and exists(serial, "SerialNumber"):
            st.error("❌ Serial već postoji")

        if inventory and exists(inventory, "InventoryNumber"):
            st.error("❌ Inventory već postoji")

        st.success("✔ Uređaj validan")

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
            "Project": project_value
        })

    else:
        st.warning("⚠ Popuni sva OBAVEZNA polja")

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