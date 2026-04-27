import streamlit as st
import pandas as pd
from io import BytesIO

import cv2
from pyzbar import pyzbar
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase

st.set_page_config(page_title="CMDB Batch Scan", layout="centered")

st.title("📦 CMDB Batch + Scan po polju")

# =========================
# SCANNER STATE
# =========================
if "scan_target" not in st.session_state:
    st.session_state.scan_target = None

if "scan_value" not in st.session_state:
    st.session_state.scan_value = ""

# =========================
# SCANNER
# =========================
class Scanner(VideoTransformerBase):
    def __init__(self):
        self.code = None

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        barcodes = pyzbar.decode(img)

        for b in barcodes:
            x, y, w, h = b.rect
            cv2.rectangle(img, (x, y), (x+w, y+h), (0,255,0), 2)

            self.code = b.data.decode("utf-8")

            cv2.putText(img, self.code, (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)

        return img

# =========================
# CAMER STREAM
# =========================
def start_scan(target_key):
    st.session_state.scan_target = target_key

st.subheader("📷 Kamera Scan")

ctx = webrtc_streamer(
    key="scanner",
    video_transformer_factory=Scanner
)

if ctx.video_transformer and ctx.video_transformer.code:
    code = ctx.video_transformer.code

    if st.session_state.scan_target:
        st.session_state[st.session_state.scan_target] = code
        st.success(f"✔ Upisano u {st.session_state.scan_target}: {code}")
        st.session_state.scan_target = None

# =========================
# BATCH INPUT
# =========================
count = st.number_input("Broj uređaja", 1, 20, 1)

devices = []

for i in range(int(count)):
    st.subheader(f"📦 Uređaj {i+1}")

    name = st.text_input("Name", key=f"name{i}")
    model = st.text_input("Model", key=f"model{i}")
    type_ = st.text_input("Type", key=f"type{i}")
    vendor = st.text_input("Vendor", key=f"vendor{i}")

    # =========================
    # SERIAL + CAMERA
    # =========================
    col1, col2 = st.columns([3,1])

    with col1:
        serial = st.text_input("SerialNumber", key=f"serial{i}")

    with col2:
        if st.button("📷", key=f"scan_serial{i}"):
            start_scan(f"serial{i}")

    # =========================
    # INVENTORY + CAMERA
    # =========================
    col1, col2 = st.columns([3,1])

    with col1:
        inventory = st.text_input("InventoryNumber", key=f"inv{i}")

    with col2:
        if st.button("📷", key=f"scan_inv{i}"):
            start_scan(f"inv{i}")

    # =========================
    # SP + CAMERA
    # =========================
    col1, col2 = st.columns([3,1])

    with col1:
        sp = st.text_input("SPInventoryNumber", key=f"sp{i}")

    with col2:
        if st.button("📷", key=f"scan_sp{i}"):
            start_scan(f"sp{i}")

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
# EXPORT
# =========================
if st.button("💾 Preuzmi Excel"):

    df = pd.DataFrame(devices)

    if df.empty:
        st.error("❌ Nema podataka")
    else:
        output = BytesIO()

        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)

        st.download_button(
            "📥 Download Excel",
            data=output.getvalue(),
            file_name="cmdb_scan.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )