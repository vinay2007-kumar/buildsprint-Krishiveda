"""KrishiVeda Streamlit demo - zero-install UI fallback for hackathon judges.
Run: streamlit run streamlit_app/demo.py
Works fully offline using the same rule-based services as the FastAPI backend.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st

st.set_page_config(page_title="KrishiVeda", page_icon="🌾", layout="centered")
st.title("🌾 KrishiVeda - किसान सहायक")

lang = st.selectbox("भाषा / ભાષા / Language", ["hi", "gu", "en"])
tab = st.tabs(["💬 Ask", "📷 Disease", "🧪 Soil", "🌦️ Weather", "🏛️ Schemes"])

with tab[0]:
    q = st.text_input("सवाल पूछें / પ્રશ્ન પૂછો / Ask")
    if st.button("Send") and q:
        from backend.services.llm_service import fallback_answer
        st.success(fallback_answer(q, lang))

with tab[1]:
    f = st.file_uploader("Crop image", type=["jpg", "png", "webp"])
    if f and st.button("Check"):
        from backend.services.disease_service import predict_mock
        r = predict_mock(f.read())
        st.metric(r["top_prediction"]["disease_name"], f"{r['top_prediction']['confidence']*100:.0f}%")
        if r.get("warning"): st.warning(r["warning"])
        st.write(r["ai_analysis"])
        st.write("Actions:", r["recommended_actions"])

with tab[2]:
    n = st.slider("Nitrogen", 0, 300, 100); p = st.slider("Phosphorus", 0, 200, 50); k = st.slider("Potassium", 0, 200, 50)
    ph = st.slider("pH", 3.0, 10.0, 7.0)
    if st.button("Advise"):
        from backend.services.soil_service import analyze_soil
        st.json(analyze_soil("wheat", "black", ph, n, p, k, "vegetative"))

with tab[3]:
    st.info("Full forecast needs backend + internet (Open-Meteo). Frontend /weather page shows live data when server runs.")

with tab[4]:
    pdf = st.file_uploader("Scheme PDF", type=["pdf"])
    if pdf:
        import tempfile
        from backend.services import rag_service
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as t:
            t.write(pdf.read()); path = t.name
        text = rag_service.extract_pdf_text(path)
        rag_service.ingest_document("demo", pdf.name, text)
        st.success(f"Indexed {len(text)} chars")
        qq = st.text_input("Question about scheme")
        if st.button("Ask doc") and qq:
            st.write(rag_service.query("demo", qq)["answer"])
