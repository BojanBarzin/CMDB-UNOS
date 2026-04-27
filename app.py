import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="CMDB Unos", layout="centered")
st.title("📦 CMDB Unos")

# =========================
# SESSION STATE (DRAFT SAVE)
# =========================
if "devices" not in st.session_state:
    st.session_state.devices = []

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

# =========================
# INPUT
# =========================
for i in range(int(count)):
    st.markdown(f"""
    <div id="device_{i}" style="
        padding:10px;
        border-radius:10px;
        background:#f8f9fa;
        margin-bottom:10px;">
    </div>
    """, unsafe_allow_html=True)

    st.subheader(f"📦 Uređaj {i+1}")

    name = st.text_input("Name *", key=f"name{i}")
    if not name:
        valid = False

    vendor = st.selectbox("Vendor", [""] + UPS_VENDORS if name == "UPS" else [""] , key=f"vendor{i}") \
        if name == "UPS" else st.text_input("Vendor", key=f"vendor{i}")

    model = st.selectbox("Model", [""] + APC_MODELS, key=f"model{i}") \
        if vendor == "APC" else st.text_input("Model", key=f"model{i}")

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

    try:
        existing_df = pd.read_excel("data.xlsx")
    except:
        existing_df = pd.DataFrame()

    errors = {}
    error_devices = set()

    # CHECK EXISTING
    for col in ["SPInventoryNumber", "InventoryNumber", "SerialNumber"]:
        if col in existing_df.columns:
            existing_values = set(existing_df[col].astype(str))

            for idx, val in enumerate(df[col]):
                if val and val in existing_values:
                    errors.setdefault(idx, []).append(f"{col} već postoji ({val})")
                    error_devices.add(idx)

    # DUP IN INPUT
    for col in ["SPInventoryNumber", "InventoryNumber", "SerialNumber"]:
        dup_mask = df[col].duplicated(keep=False)
        for idx in df[dup_mask].index:
            val = df.loc[idx, col]
            if val:
                errors.setdefault(idx, []).append(f"Duplikat ({col}: {val})")
                error_devices.add(idx)

    # =========================
    # SHOW ERRORS (CLICKABLE STYLE)
    # =========================
    if errors:
        st.error("❌ Pronađeni duplikati (klikni uređaj):")

        for idx, msgs in errors.items():
            if st.button(f"➡ Uređaj {idx+1}: " + " | ".join(set(msgs))):
                st.markdown(f"👉 Fokus na uređaj {idx+1}")

        # highlight + scroll first error
        first = list(error_devices)[0]

        st.markdown(f"""
        <script>
        const inputs = window.parent.document.querySelectorAll('input');
        if(inputs[{first * 6}] ){{
            inputs[{first * 6}].scrollIntoView({{behavior: 'smooth', block: 'center'}});
            inputs[{first * 6}].style.border = "3px solid red";
            inputs[{first * 6}].style.backgroundColor = "#ffe6e6";
        }}
        </script>
        """, unsafe_allow_html=True)

        st.stop()

    # =========================
    # EXPORT
    # =========================
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