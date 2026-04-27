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
    "UPS",
    "Printer label",
    "Router",
    "Monitor",
    "IP Phone"
]

PROJECTS_MAP = {
    "107 Tendam": "107",
    "108 Deichmann": "108",
    "109 Takko": "109"
}

PROJECTS_LABELS = list(PROJECTS_MAP.keys())

# =========================
# DEPENDENCY MAP
# =========================
TYPE_VENDOR_MODEL = {
    "UPS": {
        "APC": ["Smart-UPS 1000", "Smart-UPS 1500"],
        "Eaton": ["Eaton 5E", "Eaton 9PX"]
    },
    "Printer label": {
        "Zebra": ["ZD220", "ZD421"],
        "Brother": ["QL-820NWB"]
    },
    "Router": {
        "Cisco": ["ISR 1100", "ISR 4000"],
        "TP-Link": ["Archer C6", "Archer AX50"]
    }
}

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
    # TYPE FIRST (DRIVES FLOW)
    # =========================
    type_selected = st.selectbox(
        "Type *",
        TYPE_OPTIONS,
        key=f"type{i}"
    )

    # =========================
    # NAME
    # =========================
    name = st.text_input("Name *", key=f"name{i}")

    # =========================
    # DEPENDENT VENDOR
    # =========================
    vendors = list(TYPE_VENDOR_MODEL.get(type_selected, {"Default": []}).keys())

    if len(vendors) > 0:
        vendor = st.selectbox("Vendor *", vendors, key=f"vendor{i}")
    else:
        vendor = st.text_input("Vendor", key=f"vendor{i}")

    # =========================
    # DEPENDENT MODEL
    # =========================
    models = TYPE_VENDOR_MODEL.get(type_selected, {}).get(vendor, [])

    if models:
        model = st.selectbox("Model *", models, key=f"model{i}")
    else:
        model = st.text_input("Model *", key=f"model{i}")

    # =========================
    # SP VALIDATION
    # =========================
    sp = st.text_input("SPInventoryNumber *", key=f"sp{i}")
    sp_clean = sp.strip()

    if not sp_clean:
        st.error("❌ SP obavezan")
        valid = False
    elif len(sp_clean) != 7:
        st.error("❌ SP mora imati 7 karaktera")
        valid = False
    elif not (sp_clean.startswith("FS") or sp_clean.startswith("SP")):
        st.error("❌ SP mora počinjati sa FS ili SP")
        valid = False

    # =========================
    # OPTIONAL
    # =========================
    serial = st.text_input("SerialNumber", key=f"serial{i}")
    inventory = st.text_input("InventoryNumber", key=f"inv{i}")

    deployment = st.selectbox("Deployment State", DEPLOYMENT_STATES, key=f"dep{i}")
    incident = st.selectbox("Incident State", INCIDENT_STATES, key=f"inc{i}")

    project_label = st.selectbox("Project", PROJECTS_LABELS, key=f"proj{i}")
    project_value = PROJECTS_MAP[project_label]

    # =========================
    # SAVE
    # =========================
    devices.append({
        "Name": name,
        "Type": type_selected,
        "Vendor": vendor,
        "Model": model,
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