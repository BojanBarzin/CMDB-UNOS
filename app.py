import streamlit as st
import pandas as pd
from io import BytesIO
from openpyxl import load_workbook
from datetime import date

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

# =========================
# DOCUMENT INPUT
# =========================
st.subheader("📄 Podaci za dokument")

doc_broj = st.text_input("Broj dokumenta")
doc_datum = st.date_input("Datum", value=date.today())

# 🔹 ODVOJENA POLJA
prijemnica_iz_magacina = st.text_input("Prijemnica - Iz magacina / Ime i prezime")
otpremnica_uredjaj_zaduzio = st.text_input("Otpremnica - UREĐAJ ZADUŽIO")

objekat = st.text_input("Objekat")
adresa = st.text_input("Adresa")
mesto = st.text_input("Mesto")

# =========================
# INPUT
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
        "Project": project_value
    })

# =========================
# VALIDATION
# =========================
def validate(df):
    errors = {}

    try:
        existing_df = pd.read_excel("data.xlsx")
    except:
        existing_df = pd.DataFrame()

    for col in ["SPInventoryNumber", "InventoryNumber", "SerialNumber"]:
        if col in existing_df.columns:
            existing = set(existing_df[col].astype(str))
            for idx, val in enumerate(df[col]):
                if val and val in existing:
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

def prepare():
    df = pd.DataFrame(devices)
    df["Type"] = df["Type"].str.replace(r"[^\w\s\-\/]", "", regex=True).str.strip()
    return df

# =========================
# CMDB EXPORT
# =========================
if st.button("📥 Download CMDB"):
    if not valid:
        st.error("❌ Popuni obavezna polja")
        st.stop()

    df = prepare()
    err = validate(df)

    if err:
        show_errors(err)
        st.stop()

    out = BytesIO()
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)

    st.download_button("Preuzmi", data=out.getvalue(), file_name="cmdb.xlsx")

# =========================
# OTPREMNICA
# =========================
if st.button("📄 Otpremnica"):
    df = prepare()
    err = validate(df)

    if err:
        show_errors(err)
        st.stop()

    wb = load_workbook("otpremnica_template.xlsx")
    ws = wb.active

    ws["F4"] = doc_broj
    ws["F5"] = doc_datum.strftime("%d.%m.%Y")

    # 🔹 OVO SI TRAŽIO
    ws["F8"] = otpremnica_uredjaj_zaduzio

    ws["F9"] = objekat
    ws["F10"] = adresa
    ws["F11"] = mesto

    for i, d in enumerate(devices):
        r = 14 + i
        ws[f"A{r}"] = i + 1
        ws[f"B{r}"] = d["Name"]
        ws[f"C{r}"] = d["Model"]
        ws[f"D{r}"] = d["InventoryNumber"]
        ws[f"E{r}"] = d["SerialNumber"]
        ws[f"F{r}"] = d["SPInventoryNumber"]

    out = BytesIO()
    wb.save(out)

    st.download_button("📥 Preuzmi Otpremnicu", out.getvalue(), "otpremnica.xlsx")

# =========================
# PRIJEMNICA
# =========================
if st.button("📄 Prijemnica"):
    df = prepare()
    err = validate(df)

    if err:
        show_errors(err)
        st.stop()

    wb = load_workbook("prijemnica_template.xlsx")
    ws = wb.active

    ws["D4"] = doc_broj
    ws["D5"] = doc_datum.strftime("%d.%m.%Y")

    # 🔹 OVO SI TRAŽIO
    ws["B8"] = prijemnica_iz_magacina

    ws["D9"] = objekat
    ws["D10"] = adresa
    ws["D11"] = mesto

    for i, d in enumerate(devices):
        r = 14 + i
        ws[f"A{r}"] = i + 1
        ws[f"B{r}"] = d["Name"]
        ws[f"C{r}"] = d["SerialNumber"]
        ws[f"D{r}"] = d["SPInventoryNumber"]
        ws[f"E{r}"] = d["InventoryNumber"]

    out = BytesIO()
    wb.save(out)

    st.download_button("📥 Preuzmi Prijemnicu", out.getvalue(), "prijemnica.xlsx")