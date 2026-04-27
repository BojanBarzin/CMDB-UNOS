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
# LOAD EXISTING DATA
# =========================
@st.cache_data
def load_main():
    try:
        return pd.read_excel("data.xlsx")
    except:
        return pd.DataFrame()

main_df = load_main()

def exists(value, column):
    if not value:
        return False
    if main_df.empty:
        return False
    if column not in main_df.columns:
        return False
    return str(value) in main_df[column].astype(str).values

# =========================
# STATE
# =========================
devices = []
valid = True

# =========================
# INPUT
# =========================
count = st.number_input("Broj uređaja", 1, 50, 1)

for i in range(int(count)):
    st.markdown("---")
    st.subheader(f"📦 Uređaj {i+1}")

    # =========================
    # NAME
    # =========================
    name = st.text_input("Name *", key=f"name{i}")
    if not name:
        st.error("❌ Name je obavezan")
        valid = False

    # =========================
    # MODEL
    # =========================
    model = st.text_input("Model *", key=f"model{i}")
    if not model:
        st.error("❌ Model je obavezan")
        valid = False

    # =========================
    # SP VALIDACIJA
    # =========================
    sp = st.text_input("SPInventoryNumber *", key=f"sp{i}")
    sp_clean = sp.strip()

    if not sp_clean:
        st.error("❌ SP je obavezan")
        valid = False

    elif len(sp_clean) != 7:
        st.error("❌ SP mora imati tačno 7 karaktera")
        valid = False

    elif not (sp_clean.startswith("FS") or sp_clean.startswith("SP")):
        st.error("❌ SP mora počinjati sa FS ili SP")
        valid = False

    elif exists(sp_clean, "SPInventoryNumber"):
        st.error("❌ SP već postoji u CMDB")
        valid = False

    # =========================
    # SERIAL VALIDACIJA
    # =========================
    serial = st.text_input("SerialNumber", key=f"serial{i}")
    serial_clean = serial.strip()

    if serial_clean:
        if exists(serial_clean, "SerialNumber"):
            st.error("❌ Serial već postoji u CMDB")
            valid = False

    # =========================
    # INVENTORY VALIDACIJA
    # =========================
    inventory = st.text_input("InventoryNumber", key=f"inv{i}")
    inventory_clean = inventory.strip()

    if inventory_clean:
        if exists(inventory_clean, "InventoryNumber"):
            st.error("❌ Inventory već postoji u CMDB")
            valid = False

    # =========================
    # DROPDOWNS
    # =========================
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
    # OPTIONAL
    # =========================
    vendor = st.text_input("Vendor", key=f"vendor{i}")
    type_ = st.text_input("Type", key=f"type{i}")

    # =========================
    # SAVE
    # =========================
    devices.append({
        "Name": name,
        "Model": model,
        "Type": type_,
        "Vendor": vendor,
        "SerialNumber": serial_clean,
        "InventoryNumber": inventory_clean,
        "SPInventoryNumber": sp_clean,
        "Deployment State": deployment,
        "Incident State": incident,
        "Project": project_value
    })

# =========================
# EXPORT (BLOCK IF INVALID)
# =========================
if st.button("📥 Download Excel"):

    if not valid:
        st.error("❌ Ne može download - postoje greške u unosu")
        st.stop()

    df = pd.DataFrame(devices)

    if df.empty:
        st.error("❌ Nema podataka")
    else:
        output = BytesIO()

        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="CMDB")

        st.download_button(
            "📥 Preuzmi Excel",
            data=output.getvalue(),
            file_name="cmdb_unos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )