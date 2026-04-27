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
# LOAD EXISTING DATA (DUPLIKATI)
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
# INPUT
# =========================
count = st.number_input("Broj uređaja", 1, 50, 1)

devices = []
valid = True
error_msg = ""

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
    # OPCIONALNO
    # =========================
    vendor = st.text_input("Vendor", key=f"vendor{i}")
    type_ = st.text_input("Type", key=f"type{i}")
    serial = st.text_input("SerialNumber", key=f"serial{i}")
    inventory = st.text_input("InventoryNumber", key=f"inv{i}")

    # =========================
    # VALIDACIJA OBAVEZNIH
    # =========================
    if not name or not model or not sp:
        valid = False
        error_msg = "❌ Name, Model i SP su obavezni"

    # =========================
    # SP VALIDACIJA (RULES)
    # =========================
    sp_clean = sp.strip()

    if sp_clean:
        if len(sp_clean) != 7:
            valid = False
            error_msg = "❌ SP mora imati tačno 7 karaktera"

        elif not (sp_clean.startswith("FS") or sp_clean.startswith("SP")):
            valid = False
            error_msg = "❌ SP mora počinjati sa FS ili SP"

    # =========================
    # DUPLIKATI
    # =========================
    sp_duplicate = exists(sp_clean, "SPInventoryNumber")
    serial_duplicate = exists(serial, "SerialNumber")
    inventory_duplicate = exists(inventory, "InventoryNumber")

    if sp_duplicate:
        valid = False
        error_msg = "❌ SP već postoji u CMDB"

    if serial and serial_duplicate:
        valid = False
        error_msg = "❌ Serial već postoji u CMDB"

    if inventory and inventory_duplicate:
        valid = False
        error_msg = "❌ Inventory već postoji u CMDB"

    # =========================
    # VISUAL FEEDBACK
    # =========================
    if sp_duplicate:
        st.error("❌ SP duplikat detektovan")

    # =========================
    # SAVE
    # =========================
    devices.append({
        "Name": name,
        "Model": model,
        "Type": type_,
        "Vendor": vendor,
        "SerialNumber": serial,
        "InventoryNumber": inventory,
        "SPInventoryNumber": sp,
        "Deployment State": deployment,
        "Incident State": incident,
        "Project": project_value
    })

# =========================
# STATUS
# =========================
if st.button("💾 Validacija"):

    if not valid:
        st.error(error_msg)
    else:
        st.success("✔ Sve OK - spremno za download")

# =========================
# EXPORT
# =========================
if st.button("📥 Download Excel"):

    if not valid:
        st.error("❌ Download blokiran - greška u unosu")
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