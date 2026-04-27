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
    "118 Metro Cash & Carry": "118",
    "119 Ikea": "119",
    "123 Decathlon": "123",
    "193 Lidl": "193"
}

PROJECTS_LABELS = list(PROJECTS_MAP.keys())

# =========================
# LOAD MASTER (DUPLIKATI)
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
# STORAGE
# =========================
devices = []
valid = True
error_msg = ""

# =========================
# FORM (ENTER SUPPORT)
# =========================
with st.form("cmdb_form"):

    count = st.number_input("Broj uređaja", 1, 50, 1)

    for i in range(int(count)):
        st.markdown("---")
        st.subheader(f"📦 Uređaj {i+1}")

        # OBAVEZNA
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

        # OPCIONALNO
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
        # DUPLIKATI
        # =========================
        if sp and exists(sp, "SPInventoryNumber"):
            valid = False
            error_msg = "❌ SP već postoji u CMDB"

        if serial and exists(serial, "SerialNumber"):
            valid = False
            error_msg = "❌ Serial već postoji u CMDB"

        if inventory and exists(inventory, "InventoryNumber"):
            valid = False
            error_msg = "❌ Inventory već postoji u CMDB"

        # =========================
        # SAVE TEMP DATA
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

    submitted = st.form_submit_button("💾 Sačuvaj")

# =========================
# FEEDBACK
# =========================
if submitted:

    if not valid:
        st.error(error_msg)
        st.stop()

    st.success("✔ Validacija prošla - spremno za download")

# =========================
# EXPORT (BLOKIRAN AKO NIJE VALIDNO)
# =========================
if st.button("📥 Download Excel"):

    if not valid:
        st.error("❌ Download blokiran - postoji greška u unosu")
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