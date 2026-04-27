import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="CMDB Unos", layout="centered")
st.title("📦 CMDB Unos")

# =========================
# DATA
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
    "115 H&M": "115"
}

PROJECTS_LABELS = list(PROJECTS_MAP.keys())

UPS_VENDORS = ["APC", "CyberPower", "Socomec", "Inform", "Mustec"]
APC_MODELS = ["APC350", "APC500", "APC650", "APC1000"]

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
    # NAME (obavezno)
    # =========================
    name = st.text_input("Name *", key=f"name{i}")

    # =========================
    # VENDOR (conditional)
    # =========================
    if name == "UPS":
        vendor = st.selectbox(
            "Vendor",
            UPS_VENDORS,
            key=f"vendor{i}"
        )
    else:
        vendor = st.text_input("Vendor", key=f"vendor{i}")

    # =========================
    # MODEL (conditional + OBAVEZNO)
    # =========================
    if vendor == "APC":
        model = st.selectbox(
            "Model *",
            APC_MODELS,
            key=f"model{i}"
        )
    else:
        model = st.text_input("Model *", key=f"model{i}")

    if not model:
        st.error("❌ Model je obavezan")
        valid = False

    # =========================
    # SP (obavezno)
    # =========================
    sp = st.text_input("SPInventoryNumber *", key=f"sp{i}")
    sp_clean = sp.strip()

    if not sp_clean:
        st.error("❌ SP je obavezan")
        valid = False
    elif len(sp_clean) != 7:
        st.error("❌ SP mora imati 7 karaktera")
        valid = False
    elif not (sp_clean.startswith("FS") or sp_clean.startswith("SP")):
        st.error("❌ SP mora počinjati sa FS ili SP")
        valid = False

    # =========================
    # OPTIONAL FIELDS (VRACENO SVE)
    # =========================
    type_label = st.selectbox("Type", TYPE_OPTIONS, key=f"type{i}")

    deployment = st.selectbox("Deployment State", DEPLOYMENT_STATES, key=f"dep{i}")
    incident = st.selectbox("Incident State", INCIDENT_STATES, key=f"inc{i}")

    project_label = st.selectbox("Project", PROJECTS_LABELS, key=f"proj{i}")
    project_value = PROJECTS_MAP[project_label]

    serial = st.text_input("SerialNumber", key=f"serial{i}")
    inventory = st.text_input("InventoryNumber", key=f"inv{i}")

    # =========================
    # SAVE
    # =========================
    devices.append({
        "Name": name,
        "Vendor": vendor,
        "Model": model,
        "Type": type_label,
        "Deployment State": deployment,
        "Incident State": incident,
        "Project": project_value,
        "SerialNumber": serial,
        "InventoryNumber": inventory,
        "SPInventoryNumber": sp_clean
    })

# =========================
# EXPORT
# =========================
if st.button("📥 Download Excel"):

    if not valid:
        st.error("❌ Greške u unosu")
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