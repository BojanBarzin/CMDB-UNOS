import streamlit as st
import pandas as pd
from io import BytesIO
from openpyxl import load_workbook
from openpyxl.styles import Alignment
from datetime import date

st.set_page_config(page_title="CMDB Unos", layout="centered")
st.title("📦 CMDB Unos")

# =========================
# SESSION STATE
# =========================
if "doc_type" not in st.session_state:
    st.session_state.doc_type = None

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
# INPUT DEVICES
# =========================
devices = []
valid = True

count = st.number_input("Broj uređaja", 1, 50, 1)

for i in range(int(count)):
    st.markdown("---")
    st.subheader(f"📦 Uređaj {i+1}")

    name = st.text_input("Name *", key=f"name{i}")
    if not name:
        valid = False

    vendor = st.selectbox("Vendor", [""] + UPS_VENDORS, key=f"vendor{i}") if name == "UPS" else st.text_input("Vendor", key=f"vendor{i}")

    model = st.selectbox("Model", [""] + APC_MODELS, key=f"model{i}") if vendor == "APC" else st.text_input("Model", key=f"model{i}")

    type_label = st.selectbox("Type *", [""] + TYPE_OPTIONS, key=f"type{i}")
    if not type_label:
        valid = False

    sp = st.text_input("SPInventoryNumber *", key=f"sp{i}")
    sp_clean = sp.strip()

    if not sp_clean or len(sp_clean) != 7 or not (sp_clean.startswith("FS") or sp_clean.startswith("SP")):
        valid = False

    inventory = st.text_input("InventoryNumber", key=f"inv{i}")
    serial = st.text_input("SerialNumber", key=f"serial{i}")

    devices.append({
        "Name": name,
        "Vendor": vendor,
        "Model": model,
        "Type": type_label,
        "SPInventoryNumber": sp_clean,
        "InventoryNumber": inventory,
        "SerialNumber": serial
    })

# =========================
# HELPERS
# =========================
def center(ws, cell):
    ws[cell].alignment = Alignment(horizontal="center", vertical="center")

def prepare_df():
    df = pd.DataFrame(devices)
    df["Type"] = df["Type"].str.replace(r"[^\w\s\-\/]", "", regex=True).str.strip()
    return df

def validate_devices(df):
    errors = {}

    try:
        existing_df = pd.read_excel("data.xlsx")
    except:
        existing_df = pd.DataFrame()

    for col in ["SPInventoryNumber", "InventoryNumber", "SerialNumber"]:
        if col in existing_df.columns:
            existing_values = set(existing_df[col].astype(str))
            for idx, val in enumerate(df[col]):
                if val and val in existing_values:
                    errors.setdefault(idx, []).append(f"{col} postoji ({val})")

    for col in ["SPInventoryNumber", "InventoryNumber", "SerialNumber"]:
        dup = df[col].duplicated(keep=False)
        for idx in df[dup].index:
            val = df.loc[idx, col]
            if val:
                errors.setdefault(idx, []).append(f"Duplikat ({col}: {val})")

    return errors

def show_errors(errors):
    st.error("❌ Greške:")
    for i, msgs in errors.items():
        st.warning(f"Uređaj {i+1}: " + " | ".join(set(msgs)))

def check(df):
    if not valid:
        st.error("❌ Popuni obavezna polja")
        st.stop()

    err = validate_devices(df)
    if err:
        show_errors(err)
        st.stop()

# =========================
# DOCUMENT SELECT
# =========================
st.markdown("---")
col1, col2 = st.columns(2)

if col1.button("📄 Otpremnica"):
    st.session_state.doc_type = "otpremnica"

if col2.button("📄 Prijemnica"):
    st.session_state.doc_type = "prijemnica"

# =========================
# OTPREMNICA
# =========================
if st.session_state.doc_type == "otpremnica":
    st.subheader("📄 Otpremnica")

    broj = st.text_input("Broj")
    datum = st.date_input("Datum", value=date.today())
    zaduzio = st.text_input("UREĐAJ ZADUŽIO")
    objekat = st.text_input("Objekat")
    adresa = st.text_input("Adresa")
    mesto = st.text_input("Mesto")

    if st.button("Generiši Otpremnicu"):
        df = prepare_df()
        check(df)

        wb = load_workbook("otpremnica_template.xlsx")
        ws = wb.active

        ws["F4"] = broj; center(ws, "F4")
        ws["F5"] = datum.strftime("%d.%m.%Y"); center(ws, "F5")

        ws["G8"] = zaduzio; center(ws, "G8")
        ws["F9"] = objekat; center(ws, "F9")
        ws["F10"] = adresa; center(ws, "F10")
        ws["F11"] = mesto; center(ws, "F11")

        for i, d in enumerate(devices):
            r = 14 + i
            ws[f"A{r}"] = i+1; center(ws, f"A{r}")
            ws[f"B{r}"] = d["Name"]; center(ws, f"B{r}")
            ws[f"C{r}"] = d["Model"]; center(ws, f"C{r}")
            ws[f"D{r}"] = d["InventoryNumber"]; center(ws, f"D{r}")
            ws[f"E{r}"] = d["SerialNumber"]; center(ws, f"E{r}")
            ws[f"F{r}"] = d["SPInventoryNumber"]; center(ws, f"F{r}")

        out = BytesIO()
        wb.save(out)

        st.download_button("Preuzmi", out.getvalue(), "otpremnica.xlsx")

# =========================
# PRIJEMNICA
# =========================
if st.session_state.doc_type == "prijemnica":
    st.subheader("📄 Prijemnica")

    broj = st.text_input("Broj")
    datum = st.date_input("Datum", value=date.today())
    magacin = st.text_input("Iz magacina / Ime i prezime")
    objekat = st.text_input("Objekat")
    adresa = st.text_input("Adresa")
    mesto = st.text_input("Mesto")

    if st.button("Generiši Prijemnicu"):
        df = prepare_df()
        check(df)

        wb = load_workbook("prijemnica_template.xlsx")
        ws = wb.active

        ws["F4"] = broj; center(ws, "F4")
        ws["F5"] = datum.strftime("%d.%m.%Y"); center(ws, "F5")

        ws["B8"] = magacin; center(ws, "B8")
        ws["F9"] = objekat; center(ws, "F9")
        ws["F10"] = adresa; center(ws, "F10")
        ws["F11"] = mesto; center(ws, "F11")

        for i, d in enumerate(devices):
            r = 14 + i
            ws[f"A{r}"] = i+1; center(ws, f"A{r}")
            ws[f"B{r}"] = d["Name"]; center(ws, f"B{r}")
            ws[f"C{r}"] = d["SerialNumber"]; center(ws, f"C{r}")
            ws[f"D{r}"] = d["SPInventoryNumber"]; center(ws, f"D{r}")
            ws[f"E{r}"] = d["InventoryNumber"]; center(ws, f"E{r}")

        out = BytesIO()
        wb.save(out)

        st.download_button("Preuzmi", out.getvalue(), "prijemnica.xlsx")