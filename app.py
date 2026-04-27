import streamlit as st
import pandas as pd
from io import BytesIO
from PIL import Image
from pyzbar.pyzbar import decode

st.set_page_config(page_title="CMDB Batch + Scan + Validation", layout="centered")

st.title("📦 CMDB Batch Unos + Scan + Duplikat Check")

# =========================
# LOAD CMDB EXCEL
# =========================
@st.cache_data
def load_main():
    try:
        return pd.read_excel("data.xlsx")
    except:
        return pd.DataFrame()

main_df = load_main()

# =========================
# DUPLIKAT FUNKCIJA
# =========================
def check_duplicate(value, column):
    if main_df.empty:
        return False
    if column not in main_df.columns:
        return False
    return str(value) in main_df[column].astype(str).values

# =========================
# CAMERA SCAN (CLOUD SAFE)
# =========================
st.subheader("📷 Scan QR / Barcode")

img = st.camera_input("Skeniraj kod")

scanned_value = None

if img is not None:
    image = Image.open(img)
    result = decode(image)

    for r in result:
        scanned_value = r.data.decode("utf-8")
        st.success(f"📌 Skenirano: {scanned_value}")

# =========================
# AUTOCOMPLETE NAME
# =========================
st.subheader("🔎 Pretraga uređaja")

search = st.text_input("Kucaj Name")

if not main_df.empty and "Name" in main_df.columns:
    if search:
        filtered = main_df[
            main_df["Name"].astype(str).str.contains(search, case=False, na=False)
        ]
    else:
        filtered = main_df

    options = filtered["Name"].dropna().unique()[:10]
else:
    options = []

selected = st.selectbox("Izaberi uređaj", [""] + list(options))

# =========================
# AUTO FILL
# =========================
autofill = {}

if selected and not main_df.empty:
    row = main_df[main_df["Name"] == selected]

    if not row.empty:
        r = row.iloc[0]
        autofill = {
            "Name": r.get("Name", ""),
            "Model": r.get("Model", ""),
            "Type": r.get("Type", ""),
            "Vendor": r.get("Vendor", "")
        }

# =========================
# BATCH INPUT
# =========================
count = st.number_input("Broj uređaja", 1, 20, 1)

devices = []

for i in range(int(count)):
    st.markdown("---")
    st.subheader(f"📦 Uređaj {i+1}")

    # NAME
    name = st.text_input("Name", value=autofill.get("Name", ""), key=f"name{i}")
    model = st.text_input("Model", value=autofill.get("Model", ""), key=f"model{i}")
    type_ = st.text_input("Type", value=autofill.get("Type", ""), key=f"type{i}")
    vendor = st.text_input("Vendor", value=autofill.get("Vendor", ""), key=f"vendor{i}")

    # SERIAL + CHECK
    serial = st.text_input(
        "SerialNumber",
        value=scanned_value if scanned_value else "",
        key=f"serial{i}"
    )

    if serial:
        if check_duplicate(serial, "SerialNumber"):
            st.error("❌ Serial već postoji u CMDB")
        else:
            st.success("✔ Serial OK")

    # INVENTORY + CHECK
    inventory = st.text_input("InventoryNumber", key=f"inv{i}")

    if inventory:
        if check_duplicate(inventory, "InventoryNumber"):
            st.error("❌ Inventory već postoji u CMDB")
        else:
            st.success("✔ Inventory OK")

    # SP + CHECK
    sp = st.text_input("SPInventoryNumber", key=f"sp{i}")

    if sp:
        if check_duplicate(sp, "SPInventoryNumber"):
            st.error("❌ SP već postoji u CMDB")
        else:
            st.success("✔ SP OK")

    # SKIP EMPTY ROWS
    if name or inventory:
        devices.append({
            "Name": name,
            "Model": model,
            "Type": type_,
            "Vendor": vendor,
            "SerialNumber": serial,
            "InventoryNumber": inventory,
            "SPInventoryNumber": sp
        })

# =========================
# EXPORT EXCEL
# =========================
if st.button("💾 Sačuvaj i preuzmi Excel"):

    df = pd.DataFrame(devices)

    if df.empty:
        st.error("❌ Nema unetih uređaja!")
    else:
        output = BytesIO()

        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="CMDB")

        st.success(f"✅ Sačuvano uređaja: {len(df)}")

        st.download_button(
            "📥 Preuzmi Excel",
            data=output.getvalue(),
            file_name="cmdb_batch_final.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )