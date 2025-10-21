import streamlit as st

st.title("👋 My Bio")

# ---------- TODO: Replace with your own info ----------
NAME = "Joshua Parra"
PROGRAM = "Streamlit Lab / CS / Student"
INTRO = (
    "I'm a bilingual CS senior learning about data visualization. Currently" \
    "I'm having a lot of fun creating creative charts that show data accurately." \
    "CS offers many branches so data visualization is crucial to learn."
)
FUN_FACTS = [
    "I love gaming, chocolate candy, and computer science.",
    "I’m learning data visualization and 3d printing and modeling.",
    "I want to build video games, websites, browser extensions, and apps that I would use.",
]
PHOTO_PATH = "assets\abstract-momentary-10k-fg.jpg"  # Put a file in repo root or set a URL

# ---------- Layout ----------
col1, col2 = st.columns([1, 2], vertical_alignment="center")

with col1:
    try:
        st.image(PHOTO_PATH, caption=NAME, use_container_width=True)
    except Exception:
        st.info("Add a photo named `your_photo.jpg` to the repo root, or change PHOTO_PATH.")
with col2:
    st.subheader(NAME)
    st.write(PROGRAM)
    st.write(INTRO)

st.markdown("### Fun facts")
for i, f in enumerate(FUN_FACTS, start=1):
    st.write(f"- {f}")

st.divider()
st.caption("Edit `pages/1_Bio.py` to customize this page.")
