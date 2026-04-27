import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="CMDB Unos", layout="centered")
st.title("📦 CMDB Unos")

# =========================
# LOAD EXISTING DATA
# =========================
try:
    existing_df = pd.read_excel("data.xlsx")
except:
    existing_df = pd.DataFrame()

def exists(column, value):
    if existing_df is None or existing_df.empty:
        return False
    if column not in existing_df.columns:
        return False
    return str(value) in existing_df[column].astype(str).values

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

# =========================
# STATE
# =========================
devices = []
valid = True

sp_set = set()
inv_set = set()
serial_set = set()

count = st.number_input("Broj uređaja", 1, 50, 1)

for i in range(int(count)):
    st.markdown("---")
    st.subheader(f"📦 Uređaj {i+1}")

    # =========================
    # FIX 2 - 3 COLUMNS
    # =========================
    col1, col2, col3 = st.columns(3)

    with col1:
        name = st.text_input("Name *", key=f"name{i}")
        if name == "UPS":
            vendor = st.selectbox("Vendor", [""] + UPS_VENDORS, key=f"vendor{i}")
        else:
            vendor = st.text_input("Vendor", key=f"vendor{i}")

    with col2:
        if vendor == "APC":
            model = st.selectbox("Model", [""] + APC_MODELS, key=f"model{i}")
        else:
            model = st.text_input("Model", key=f"model{i}")

        type_label = st.selectbox("Type *", [""] + TYPE_OPTIONS, key=f"type{i}")

        if not type_label:
            st.error("❌ Type je obavezan")
            valid = False

    with col3:
        sp = st.text_input("SPInventoryNumber *", key=f"sp{i}")
        inventory = st.text_input("InventoryNumber", key=f"inv{i}")
        serial = st.text_input("SerialNumber", key=f"serial{i}")

    # =========================
    # VALIDATION
    # =========================
    if not name:
        st.error("❌ Name je obavezan")
        valid = False

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
    # DUPLICATES
    # =========================
    if sp_clean:
        if exists("SPInventoryNumber", sp_clean) or sp_clean in sp_set:
            st.error("❌ SP već postoji")
            valid = False
        sp_set.add(sp_clean)

    if inventory:
        if exists("InventoryNumber", inventory) or inventory in inv_set:
            st.error("❌ Inventory već postoji")
            valid = False
        inv_set.add(inventory)

    if serial:
        if exists("SerialNumber", serial) or serial in serial_set:
            st.error("❌ Serial već postoji")
            valid = False
        serial_set.add(serial)

    # =========================
    # EXTRA ROW (3 COLUMNS)
    # =========================
    col4, col5, col6 = st.columns(3)

    with col4:
        deployment = st.selectbox("Deployment State", [""] + DEPLOYMENT_STATES, key=f"dep{i}")

    with col5:
        incident = st.selectbox("Incident State", [""] + INCIDENT_STATES, key=f"inc{i}")

    with col6:
        project_label = st.selectbox("Project", [""] + PROJECTS_LABELS, key=f"proj{i}")

    project_value = PROJECTS_MAP.get(project_label, "")

    # =========================
    # SAVE
    # =========================
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
# EXPORT
# =========================
if st.button("📥 Download Excel"):

    if not valid:
        st.error("❌ Greške u unosu")
        st.stop()

    df = pd.DataFrame(devices)

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