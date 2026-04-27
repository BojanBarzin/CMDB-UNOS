import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="CMDB Unos", layout="centered")

st.title("📦 CMDB Unos")

# =========================
# STATIC DATA
# =========================
DEPLOYMENT_STATES = ["Functional", "Malfunctioned", "Retired"]
INCIDENT_STATES = ["Operational", "Incident"]

TYPE_OPTIONS = [
    "Cash drawer",
    "Cradle",
    "IP Phone",
    "Monitor",
    "Monitor Touch Screen",
    "Printer Pos",
    "Printer label",
    "Router",
    "Switch",
    "Scanner Counter",
    "Scanner Hand",
    "Scanner Terminal",
    "UPS"
]

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
# STATE
# =========================
devices = []
valid = True

count = st.number_input("Broj uređaja", 1, 50, 1)

for i in range(int(count)):
    st.markdown("---")
    st.subheader(f"📦 Uređaj {i+1}")

    # =========================
    # 1. NAME
    # =========================
    name = st.text_input("Name *", key=f"name{i}")
    if not name:
        st.error("❌ Name je obavezan")
        valid = False

    # =========================
    # 2. VENDOR
    # =========================
    vendor = st.text_input("Vendor *", key=f"vendor{i}")
    if not vendor:
        st.error("❌ Vendor je obavezan")
        valid = False

    # =========================
    # 3. MODEL
    # =========================
    model = st.text_input("Model *", key=f"model{i}")
    if not model:
        st.error("❌ Model je obavezan")
        valid = False

    # =========================
    # SP VALIDATION
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

    # =========================
    # TYPE
    # =========================
    type_ = st.selectbox(
        "Type *",
        TYPE_OPTIONS,
        key=f"type{i}"
    )

    # =========================
    # OPTIONAL FIELDS
    # =========================
    serial = st.text_input("SerialNumber", key=f"serial{i}")
    inventory = st.text_input("InventoryNumber", key=f"inv{i}")

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
    # SAVE
    # =========================
    devices.append({
        "Name": name,
        "Vendor": vendor,
        "Model": model,
        "Type": type_,
        "SerialNumber": serial,
        "InventoryNumber": inventory,
        "SPInventoryNumber": sp_clean,
        "Deployment State": deployment,
        "Incident State": incident,
        "Project": project_value
    })

# =========================
# EXPORT
# =========================
if st.button("📥 Download Excel"):

    if not valid:
        st.error("❌ Ne može download - postoje greške u unosu")
        st.stop()

    df = pd.DataFrame(devices)

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="CMDB")

    st.download_button(
        "📥 Preuzmi Excel",
        data=output.getvalue(),
        file_name="cmdb_unos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )