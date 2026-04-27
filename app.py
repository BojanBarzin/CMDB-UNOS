# =========================
# CLICKABLE ERROR STATE
# =========================
if "focus_device" not in st.session_state:
    st.session_state.focus_device = None

if errors:
    st.error("❌ Pronađeni duplikati (klikni uređaj):")

    for idx, msgs in errors.items():

        if st.button(f"➡ Uređaj {idx+1}: " + " | ".join(set(msgs)), key=f"err_{idx}"):
            st.session_state.focus_device = idx

    first = list(errors.keys())[0]
    focus = st.session_state.focus_device if st.session_state.focus_device is not None else first

    st.markdown(f"""
    <script>
    const inputs = window.parent.document.querySelectorAll('input');

    if(inputs[{focus * 6}] ){{
        inputs[{focus * 6}].scrollIntoView({{behavior: 'smooth', block: 'center'}});
        inputs[{focus * 6}].style.border = "3px solid red";
        inputs[{focus * 6}].style.backgroundColor = "#ffe6e6";
    }}
    </script>
    """, unsafe_allow_html=True)

    st.stop()