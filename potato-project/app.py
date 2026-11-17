import requests
import streamlit as st
from PIL import Image

API_URL = "http://127.0.0.1:8000/predict"
DOCS_URL = "http://127.0.0.1:8000/docs"

st.set_page_config(page_title="Potato Leaf Doctor", page_icon="🥔", layout="wide")

# ---------- Styling (works in both light and dark Streamlit themes) ----------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@600;700;800&family=Figtree:wght@400;500;600&display=swap');

.block-container { padding-top: 2rem; max-width: 1100px; }
.stApp p, .stApp li, .stApp label, .stApp button { font-family: 'Figtree', sans-serif; }

.hero {
    background: linear-gradient(135deg, #1f4d2e 0%, #2f6b3a 60%, #4c8a4f 100%);
    border-radius: 18px;
    padding: 2.2rem 2.4rem;
    margin-bottom: 1.8rem;
}
.hero-title {
    font-family: 'Bricolage Grotesque', sans-serif;
    font-weight: 800;
    font-size: 2.6rem;
    line-height: 1.1;
    color: #ffffff;
    letter-spacing: -0.02em;
}
.hero-sub {
    font-family: 'Figtree', sans-serif;
    color: #dcebdd;
    font-size: 1.05rem;
    margin-top: 0.6rem;
    max-width: 38rem;
}

.verdict {
    border: 1px solid rgba(127,127,127,0.28);
    border-left: 8px solid var(--tone);
    border-radius: 14px;
    padding: 1.3rem 1.5rem;
    background: rgba(127,127,127,0.07);
    margin-bottom: 1rem;
}
.verdict-name {
    font-family: 'Bricolage Grotesque', sans-serif;
    font-weight: 800;
    font-size: 2.1rem;
    line-height: 1.15;
    color: var(--tone);
}
.verdict-sev { font-family: 'Figtree', sans-serif; font-size: 0.98rem; opacity: 0.8; margin-top: 0.2rem; }
.meter {
    height: 12px;
    border-radius: 999px;
    background: rgba(127,127,127,0.25);
    overflow: hidden;
    margin-top: 1rem;
}
.meter-fill { height: 100%; border-radius: 999px; background: var(--tone); }
.meter-text { font-family: 'Figtree', sans-serif; font-weight: 600; margin-top: 0.45rem; }

.empty {
    border: 2px dashed rgba(127,127,127,0.35);
    border-radius: 14px;
    padding: 2.4rem 1.5rem;
    text-align: center;
    opacity: 0.8;
    font-family: 'Figtree', sans-serif;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ---------- Disease information ----------
GREEN, AMBER, RED = "#3f9b57", "#d99a1e", "#d4533f"

DISEASES = {
    "Early_blight": {
        "name": "Early blight",
        "severity": "Moderate. Treat soon to protect the crop.",
        "tone": AMBER,
        "about": (
            "A fungal disease (Alternaria solani). It shows up as dark brown spots with "
            "ring-like patterns, usually on the older, lower leaves first."
        ),
        "actions": [
            "Remove and bin the affected leaves.",
            "Water at the base of the plant and avoid wetting the leaves.",
            "Rotate potatoes with a different crop next season.",
            "If it keeps spreading, use a recommended fungicide at the label dose.",
        ],
    },
    "Late_blight": {
        "name": "Late blight",
        "severity": "Severe. It can destroy a field within days.",
        "tone": RED,
        "about": (
            "A fast-spreading disease (Phytophthora infestans). Look for dark, water-soaked "
            "patches, often with white mold underneath the leaf in humid weather."
        ),
        "actions": [
            "Act quickly: remove infected plants and keep them out of your compost.",
            "Avoid working in the field when plants are wet, so it doesn't spread.",
            "Ask your local agriculture officer which fungicide is right for your area.",
            "Plant resistant varieties and certified seed potatoes next season.",
        ],
    },
    "healthy": {
        "name": "Healthy leaf",
        "severity": "No signs of disease found.",
        "tone": GREEN,
        "about": "The leaf looks normal, with no spots or lesions that the model recognises.",
        "actions": [
            "Keep checking the plants every few days.",
            "Water evenly and leave space between plants for airflow.",
            "Re-test any leaf that starts to show spots or yellow patches.",
        ],
    },
}


def clean_label(raw: str) -> str:
    """'Potato___Early_blight' -> 'Early_blight'"""
    return raw.replace("Potato___", "").strip()


def backend_online() -> bool:
    try:
        return requests.get(DOCS_URL, timeout=1.5).status_code == 200
    except requests.exceptions.RequestException:
        return False


# ---------- Sidebar ----------
with st.sidebar:
    st.subheader("Photo tips")
    st.markdown(
        "- Photograph a single leaf.\n"
        "- Use daylight and keep the leaf in focus.\n"
        "- Fill most of the frame with the leaf.\n"
        "- A plain background works best."
    )
    st.divider()
    if backend_online():
        st.success("Model server is running.")
    else:
        st.error("Model server is offline.")
        st.caption("Start it in a second terminal:")
        st.code("uvicorn main:app --reload --port 8000", language="powershell")
    st.divider()
    st.caption("Detects: early blight, late blight and healthy potato leaves.")

# ---------- Hero ----------
st.markdown(
    """
    <div class="hero">
        <div class="hero-title">Potato Leaf Doctor</div>
        <div class="hero-sub">Upload a photo of a potato leaf. The model checks it for
        early blight and late blight in a few seconds.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns([1, 1], gap="large")

# ---------- Left: upload + preview ----------
with left:
    uploaded = st.file_uploader("Choose a potato leaf photo", type=["jpg", "jpeg", "png"])
    if uploaded is not None:
        image = Image.open(uploaded)
        st.image(image, caption=uploaded.name, width="stretch")  # FIXED: replaces use_column_width
        check = st.button("Check this leaf", type="primary", width="stretch")
    else:
        check = False

# ---------- Right: result ----------
with right:
    if uploaded is None:
        st.markdown(
            '<div class="empty">Upload a leaf photo on the left.<br>Your result will appear here.</div>',
            unsafe_allow_html=True,
        )
    else:
        file_id = f"{uploaded.name}-{uploaded.size}"

        if check:
            with st.spinner("Checking the leaf..."):
                try:
                    files = {"file": (uploaded.name, uploaded.getvalue(), uploaded.type)}
                    response = requests.post(API_URL, files=files, timeout=60)
                    if response.status_code == 200:
                        st.session_state["result"] = (file_id, response.json())
                    else:
                        st.session_state.pop("result", None)
                        st.error(f"The model server returned an error ({response.status_code}).")
                        st.caption(response.text[:300])
                except requests.exceptions.ConnectionError:
                    st.session_state.pop("result", None)
                    st.error("Can't reach the model server.")
                    st.caption("Start it with: uvicorn main:app --reload --port 8000")
                except requests.exceptions.Timeout:
                    st.session_state.pop("result", None)
                    st.error("The model server took too long to answer. Try again.")

        saved = st.session_state.get("result")
        if saved and saved[0] == file_id:
            data = saved[1]
            key = clean_label(data["class"])
            info = DISEASES.get(
                key,
                {"name": key, "severity": "", "tone": AMBER, "about": "", "actions": []},
            )
            confidence = float(data["confidence"])

            st.markdown(
                f"""
                <div class="verdict" style="--tone:{info['tone']}">
                    <div class="verdict-name">{info['name']}</div>
                    <div class="verdict-sev">{info['severity']}</div>
                    <div class="meter"><div class="meter-fill" style="width:{min(confidence, 100)}%"></div></div>
                    <div class="meter-text">{confidence:.1f}% confident</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if confidence < 70:
                st.warning(
                    "The model isn't very sure about this one. Try a clearer, closer photo "
                    "of a single leaf in daylight."
                )

            if info["about"]:
                st.markdown(info["about"])
            if info["actions"]:
                st.markdown("**What to do**")
                st.markdown("\n".join(f"- {a}" for a in info["actions"]))

            st.caption(
                "This is an AI estimate from one photo. Confirm with a local agriculture "
                "officer before making treatment decisions."
            )
        elif not check:
            st.markdown(
                '<div class="empty">Photo ready.<br>Select <b>Check this leaf</b> to see the result.</div>',
                unsafe_allow_html=True,
            )