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
    "💻 Desktop","💻 Laptop","💵 Cash drawer","📟 Cradle","☎️ IP Phone",
    "🖥️ Monitor","🖥️ Monitor Touch Screen","🧾 Printer Pos","🏷️ Printer label",
    "📡 Router","🔀 Switch","📟 Scanner Counter","✋ Scanner Hand",
    "📱 Scanner Terminal","🔋 UPS","🖧 Server","🖥️ POS Beetle",
    "🖥️ POS Custom","🖥️ POS ELO All in One","🖥️ POS NCR","📦 Other"
]

PROJECTS_MAP = {
    "107 Tendam": "107","108 Deichmann": "108","109 Takko": "109",
    "112 Mercator-S": "112","115 H&M": "115","118 Metre Cash & Carry": "118",
    "119 Ikea": "119","123 Decathlon": "123","193 Lidl": "193"
}

PROJECTS_LABELS = list(PROJECTS_MAP.keys())

UPS_VENDORS = ["APC", "CyberPower", "Socomec", "Inform", "Mustec"]
APC_MODELS = ["APC350", "APC500", "APC650", "APC1000"]

devices = []
valid = True

count = st.number_input("Broj uređaja", 1, 50, 1)

for i in range(int(count)):
    st.markdown("---")
    st.subheader(f"📦 Uređaj {i+1}")

    name = st.text_input("Name *", key=f"name{i}")
    if not name:
        valid = False

    if name == "UPS":
        vendor = st.selectbox("Vendor", [""] + UPS_VENDORS, key=f"vendor{i}")
    else:
        vendor = st.text_input("Vendor", key=f"vendor{i}")

    if vendor == "APC":
        model = st.selectbox("Model", [""] + APC_MODELS, key=f"model{i}")
    else:
        model = st.text_input("Model", key=f"model{i}")

    type_label = st.selectbox("Type *", [""] + TYPE_OPTIONS, key=f"type{i}")
    if not type_label:
        valid = False

    sp = st.text_input("SPInventoryNumber *", key=f"sp{i}")
    sp_clean = sp.strip()

    if not sp_clean or len(sp_clean) != 7 or not (sp_clean.startswith("FS") or sp_clean.startswith("SP")):
        valid = False

    inventory = st.text_input("InventoryNumber", key=f"inv{i}")
    serial = st.text_input("SerialNumber", key=f"serial{i}")

    deployment = st.selectbox("Deployment State", [""] + DEPLOYMENT_STATES, key=f"dep{i}")
    incident = st.selectbox("Incident State", [""] + INCIDENT_STATES, key=f"inc{i}")

    project_label = st.selectbox("Project", [""] + PROJECTS_LABELS, key=f"proj{i}")
    project_value = PROJECTS_MAP.get(project_label, "")

    devices.append({
        "Name": name,
        "Vendor": vendor,
        "Model": model,
        "Type": type_label,
        "SPInventoryNumber": sp_clean,
        "InventoryNumber": inventory,
        "SerialNumber": serial,
        "Deployment State": deployment,
        "Incident State": incident,
        "Project": project_value
    })

# =========================
# EXPORT + DUP CHECK
# =========================
if st.button("📥 Download Excel"):

    if not valid:
        st.error("❌ Popuni obavezna polja")
        st.stop()

    df = pd.DataFrame(devices)

    # =========================
    # LOAD EXISTING (SAMO OVDE)
    # =========================
    try:
        existing_df = pd.read_excel("data.xlsx")
    except:
        existing_df = pd.DataFrame()

    # =========================
    # DUP CHECK (BRZO I JEDNOM)
    # =========================
    for col in ["SPInventoryNumber", "InventoryNumber", "SerialNumber"]:
        if col in existing_df.columns:
            duplicates = df[df[col].isin(existing_df[col])]
            if not duplicates.empty:
                st.error(f"❌ Već postoji {col}")
                st.stop()

    # duplikati u samom unosu
    for col in ["SPInventoryNumber", "InventoryNumber", "SerialNumber"]:
        if df[col].duplicated().any():
            st.error(f"❌ Duplikati u unetim podacima: {col}")
            st.stop()

    # clean type
    df["Type"] = df["Type"].str.replace(r"[^\w\s\-\/]", "", regex=True).str.strip()

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="CMDB")

    st.download_button(
        "📥 Preuzmi Excel",
        data=output.getvalue(),
        file_name="cmdb_unos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )