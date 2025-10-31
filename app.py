import streamlit as st
from fpdf import FPDF
import datetime
import os
import requests
import re  # for cleaning pdf text

st.set_page_config(
    page_title="Soulful Chakra & Behaviour Profiler",
    page_icon="🪬",
    layout="centered"
)

# =============== HELPERS ===============
def clean_txt(txt: str) -> str:
    """Remove characters fpdf cannot render."""
    if txt is None:
        return ""
    # drop non-latin
    txt = re.sub(r"[^\x00-\xFF]", "", txt)
    # normalize some chars
    txt = txt.replace("•", "- ").replace("→", "->").replace("—", "-").replace("–", "-")
    return txt


# =============== QUESTIONS ===============
QUESTIONS = [
    # 1–10: Root / Foundation
    ("When life is uncertain, I first worry about money / security.", {"Root": -2}),
    ("I felt I had to grow up faster than others.", {"Root": -1}),
    ("I like planning and knowing what's next.", {"Root": +1}),
    ("I often feel 'I must manage everything myself.'", {"Root": -1}),
    ("I sometimes fear I will lose what I have built.", {"Root": -1}),
    ("I find it easy to ask for practical help.", {"Root": +1}),
    ("I had frequent changes in house/school/place in childhood.", {"Root": -1}),
    ("I feel supported by my family/system right now.", {"Root": +1}),
    ("I worry about family approval in money decisions.", {"Root": -1, "Heart": -1}),
    ("I want to feel rooted in my dharma / purpose.", {"Root": -1, "Crown": +1}),

    # 11–20: Sacral / Relationships / Emotions
    ("I sometimes suppress emotions to avoid drama.", {"Sacral": -1, "Throat": -1}),
    ("I crave emotional intimacy / deep connection.", {"Sacral": -1, "Heart": -1}),
    ("I compare myself with other women / leaders.", {"Sacral": -1}),
    ("I find it easy to receive compliments / love.", {"Sacral": +1, "Heart": +1}),
    ("Childhood: I felt emotionally unseen / misunderstood.", {"Sacral": -1, "Throat": -1}),
    ("I sometimes attract emotionally unavailable people.", {"Sacral": -2}),
    ("I am comfortable with my feminine energy (rest, play, receiving).", {"Sacral": +1}),
    ("I overshare and later feel drained.", {"Sacral": -1, "Solar": -1}),
    ("My relationship patterns repeat with different people.", {"Sacral": -1, "Heart": -1}),
    ("I want to heal my relationship with mother/father energy.", {"Sacral": -1, "Heart": -1, "Root": -1}),

    # 21–30: Solar / Power / Visibility
    ("I take responsibility for everyone and burn out.", {"Solar": -1, "Heart": -1}),
    ("I sometimes procrastinate even when I know the step.", {"Solar": -1}),
    ("I feel guilty increasing my prices / asking more.", {"Solar": -1, "Throat": -1}),
    ("I get triggered by criticism / judgment.", {"Solar": -1, "Heart": -1}),
    ("I like taking the lead and making decisions.", {"Solar": +1}),
    ("I sometimes overwork to feel worthy.", {"Solar": -1}),
    ("I want to be more visible (reels, stage, sessions).", {"Solar": +1, "Throat": +1}),
    ("I reduce myself to keep others comfortable.", {"Solar": -1, "Throat": -1}),
    ("I fear success may create jealousy around me.", {"Solar": -1, "Heart": -1}),
    ("I want to operate from power + devotion both.", {"Solar": +1, "Crown": +1}),

    # 31–40: Throat / Third Eye / Intuition
    ("I find it hard to say NO to family / clients.", {"Throat": -2}),
    ("I rehearse conversations in my head.", {"Throat": -1, "Third Eye": -1}),
    ("I sense people's energy quickly.", {"Third Eye": +1}),
    ("Overthinking stops me from acting fast.", {"Third Eye": -2}),
    ("I receive intuitive nudges / angel signs.", {"Third Eye": +1, "Crown": +1}),
    ("I second-guess my own guidance.", {"Third Eye": -1}),
    ("I want to speak more on spiritual / healing topics online.", {"Throat": +1, "Crown": +1}),
    ("I am afraid of being judged if I show my spiritual gifts.", {"Throat": -1, "Third Eye": -1}),
    ("I can't always put my emotions into words.", {"Throat": -1, "Sacral": -1}),
    ("I want to channel and teach like my coach / mentor.", {"Crown": +1, "Third Eye": +1}),

    # 41–50: Behaviour / Coaching Style / Integration
    ("When someone is hurting, I immediately go into fixing mode.", {"Heart": +1, "Solar": -1}),
    ("I need people to also hold space for ME.", {"Heart": -1}),
    ("I love guiding women, I just need better structure.", {"Throat": +1, "Solar": +1}),
    ("I sometimes absorb clients' or family's energy.", {"Sacral": -1, "Heart": -1}),
    ("I want rituals I can follow daily.", {"Crown": +1, "Root": +1}),
    ("I know my purpose, I just need confidence.", {"Solar": -1, "Third Eye": +1}),
    ("I keep learning but do not implement enough.", {"Solar": -1, "Third Eye": -1}),
    ("I want to be spoken to gently, not with too much logic.", {"Heart": -1}),
    ("I respond better when someone gives me 1 or 2 actions, not 10.", {"Throat": +1}),
    ("I am ready to rise as Soulful Queen or Leader.", {"Solar": +1, "Crown": +1}),
]

TOTAL_QUESTIONS = len(QUESTIONS)
QUESTIONS_PER_PAGE = 10
TOTAL_PAGES = TOTAL_QUESTIONS // QUESTIONS_PER_PAGE  # 5


# =============== STATE ===============
if "page" not in st.session_state:
    st.session_state.page = 1
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "scores" not in st.session_state:
    st.session_state.scores = {
        "Root": 5, "Sacral": 5, "Solar": 5,
        "Heart": 5, "Throat": 5, "Third Eye": 5, "Crown": 5
    }
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "profile" not in st.session_state:
    st.session_state.profile = None


# =============== HEADER UI ===============
st.markdown(
    """
    <style>
    .shell {
        background: rgba(15,5,26,0.45);
        border: 1px solid rgba(236,72,153,0.25);
        border-radius: 1.2rem;
        padding: 1.1rem 1.4rem;
        margin-bottom: 1.1rem;
        backdrop-filter: blur(10px);
    }
    hr {
        border: none;
        border-bottom: 1px solid rgba(255,255,255,0.04);
    }
    div[role='radiogroup'] {
        gap: 1.5rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<div class='shell'><h3>Soulful Chakra & Behaviour Profiler</h3><p>Answer honestly. 5 pages, 10 questions each.</p></div>", unsafe_allow_html=True)

# =============== USER DETAILS ===============
c1, c2 = st.columns(2)
with c1:
    name = st.text_input("Name", value=st.session_state.get("name", ""))
    st.session_state["name"] = name
with c2:
    gender_default = st.session_state.get("gender", "Female")
    gender = st.radio("Gender", ["Female", "Male", "Other"], horizontal=True,
                      index=["Female", "Male", "Other"].index(gender_default))
    st.session_state["gender"] = gender

email = st.text_input("Email (optional, for sending report)", value=st.session_state.get("email", ""))
st.session_state["email"] = email

st.markdown(f"### Part {st.session_state.page} of {TOTAL_PAGES}")

# =============== QUESTIONS FOR CURRENT PAGE ===============
start_idx = (st.session_state.page - 1) * QUESTIONS_PER_PAGE
end_idx = start_idx + QUESTIONS_PER_PAGE
current_questions = QUESTIONS[start_idx:end_idx]

for i, (qtext, impact) in enumerate(current_questions, start=start_idx + 1):
    key = f"q_{i}"
    prev = st.session_state.answers.get(i, "Sometimes")
    st.markdown(f"**{i}. {qtext}**")
    ans = st.radio(
        "",
        ["Yes", "Sometimes", "No"],
        index=["Yes", "Sometimes", "No"].index(prev) if prev in ["Yes", "Sometimes", "No"] else 1,
        key=key,
        horizontal=True,
    )
    st.session_state.answers[i] = ans
    st.markdown("<hr>", unsafe_allow_html=True)


# =============== NAVIGATION ===============
cprev, cnext = st.columns(2)
go_prev = cprev.button("Back", use_container_width=True)
go_next = cnext.button("Next" if st.session_state.page < TOTAL_PAGES else "Generate Report", use_container_width=True)

if go_prev and st.session_state.page > 1:
    st.session_state.page -= 1
    st.rerun()

if go_next:
    if st.session_state.page < TOTAL_PAGES:
        st.session_state.page += 1
        st.rerun()
    else:
        # calculate profile
        st.session_state.scores = {
            "Root": 5, "Sacral": 5, "Solar": 5,
            "Heart": 5, "Throat": 5, "Third Eye": 5, "Crown": 5
        }
        for idx, (qtext, impact) in enumerate(QUESTIONS, start=1):
            ans = st.session_state.answers.get(idx, "Sometimes")
            for chakra, delta in impact.items():
                if ans == "Yes":
                    st.session_state.scores[chakra] += delta
                elif ans == "Sometimes":
                    st.session_state.scores[chakra] += (delta * 0.5)

        scores = st.session_state.scores
        avg = sum(scores.values()) / len(scores)
        lowest = sorted(scores.items(), key=lambda x: x[1])[0][0]

        # map to personality
        chakra_to_personality = {
            "Root": ("4. The Safety Seeker", "You need grounded money, safe routines, and family approval healing."),
            "Sacral": ("9. The Lover-Healer", "You need emotional permission, receiving, and relationship repair."),
            "Solar": ("3. The Action Builder", "You need visibility, self-worth, pricing, and power rituals."),
            "Heart": ("1. The Nurturer Queen", "You need boundaries, receiving, and soft acknowledgement."),
            "Throat": ("5. The Expressor", "You need to speak, set limits, and create content safely."),
            "Third Eye": ("2. The Vision Queen", "You need mental calm, trust in guidance, and less overthinking."),
            "Crown": ("7. The Mystic", "You need grounding and a way to bring spiritual gifts to money."),
        }
        personality, real_need = chakra_to_personality.get(lowest, ("Soulful Being", "Return to daily energy hygiene."))

        st.session_state.profile = {
            "name": st.session_state.get("name") or "Soulful Being",
            "gender": st.session_state.get("gender") or "Female",
            "email": st.session_state.get("email") or "",
            "scores": scores,
            "avg_score": avg,
            "lowest_chakra": lowest,
            "personality": personality,
            "real_need": real_need,
            "generated_at": datetime.datetime.now().strftime("%d-%m-%Y %H:%M"),
        }
        st.session_state.submitted = True
        st.rerun()


# =============== PDF CREATOR (LONG) ===============
def create_pdf(profile: dict) -> bytes:
    LOGO_URL = "https://ik.imagekit.io/86edsgbur/Untitled%20design%20(73)%20(3)%20(1).jpg?updatedAt=1759258123716"
    LOGO_PATH = "soulful_logo.jpg"

    if not os.path.exists(LOGO_PATH):
        try:
            r = requests.get(LOGO_URL, timeout=10)
            if r.status_code == 200:
                with open(LOGO_PATH, "wb") as f:
                    f.write(r.content)
        except Exception:
            pass

    scores = profile["scores"]
    lowest = profile["lowest_chakra"]

    chakra_story = {
        "Root": (
            "You have a Root Chakra pattern. This forms when childhood or early adult life had change, "
            "responsibility, or money stress. The body learns: stay alert, stay in control, do not relax. "
            "So you may over-manage or over-work to feel safe. We are now moving you from survival to stability."
        ),
        "Sacral": (
            "You have a Sacral Chakra pattern. This is the emotional and relationship centre. You feel deeply "
            "but do not always feel received. That creates attraction to people who do not match your giving level. "
            "Your healing is to receive without guilt and to create emotional boundaries."
        ),
        "Solar": (
            "You have a Solar Plexus pattern. You are capable, but old memories connected visibility to judgment. "
            "So sometimes you delay action, pricing, or being seen. Your healing is power activation with compassion."
        ),
        "Heart": (
            "You have a Heart Chakra pattern. You love nurturing people. That is your gift. But this also made you "
            "take less than you deserved and love from sacrifice. We now restore receiving and self-love."
        ),
        "Throat": (
            "You have a Throat Chakra pattern. You have wisdom but you filtered it. Expression was not always safe. "
            "Now your soul wants to speak, teach, sell, and set boundaries without fear."
        ),
        "Third Eye": (
            "You have a Third Eye pattern. You sense energy fast and think a lot. Overthinking became your safety. "
            "We will move you from thinking to trusting and taking guided action."
        ),
        "Crown": (
            "You have a Crown Chakra pattern. You are spiritually open but not always grounded. "
            "Your journey now is to let divine ideas become daily routines and money actions."
        ),
    }

    daily_life = (
        "How it may show in daily life:\n"
        "- You take more emotional responsibility than others.\n"
        "- You know what to do but do it in bursts.\n"
        "- You attract people who like your energy but not all can hold it.\n"
        "- You want a container that understands feminine pace and spiritual depth."
    )

    seven_day = (
        "7-Day Soulful Reset Plan:\n"
        "Day 1 - Awareness: write earliest memory of this pattern.\n"
        "Day 2 - Energy Cleanse: 108x Ho'oponopono on the main person/situation.\n"
        "Day 3 - Body Anchor: 15 minutes breath and name the emotion aloud.\n"
        "Day 4 - Expression: write or record what you never said.\n"
        "Day 5 - Money or Value Action: one tangible step (ask, offer, price).\n"
        "Day 6 - Receive Mode: 30 minutes only receiving (music, nature, self-care).\n"
        "Day 7 - Integration: journal what changed in energy."
    )

    chakra_affirm = {
        "Root": [
            "I am fully supported.",
            "Money is safe for me.",
            "I belong in every room."
        ],
        "Sacral": [
            "My emotions are valid.",
            "I can receive love easily.",
            "I attract mutually fulfilling relationships."
        ],
        "Solar": [
            "My power is safe.",
            "I am worthy of visibility.",
            "I deserve to be well paid."
        ],
        "Heart": [
            "I deserve gentle love.",
            "I can give without losing myself.",
            "It is safe to be seen."
        ],
        "Throat": [
            "My voice is valuable.",
            "I can say no with love.",
            "My truth calls my tribe."
        ],
        "Third Eye": [
            "I trust my inner guidance.",
            "I do not need to overthink to stay safe.",
            "Clarity comes when I act."
        ],
        "Crown": [
            "I am guided and protected.",
            "I can be spiritual and prosperous.",
            "Divine ideas flow through me."
        ],
    }

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # header
    pdf.set_fill_color(139, 92, 246)
    pdf.rect(0, 0, 210, 18, "F")
    pdf.set_fill_color(236, 72, 153)
    pdf.rect(0, 18, 6, 279, "F")

    if os.path.exists(LOGO_PATH):
        pdf.image(LOGO_PATH, x=10, y=2, w=18)

    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(32, 4)
    pdf.set_font("Arial", "B", 15)
    pdf.cell(0, 8, clean_txt("Soulful Chakra & Behaviour Report"), ln=True)

    pdf.set_text_color(0, 0, 0)
    pdf.ln(15)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 7, clean_txt(f"Name: {profile['name']}"), ln=True)
    pdf.cell(0, 7, clean_txt(f"Gender: {profile['gender']}"), ln=True)
    if profile["email"]:
        pdf.cell(0, 7, clean_txt(f"Email: {profile['email']}"), ln=True)
    pdf.cell(0, 7, clean_txt(f"Generated at: {profile['generated_at']}"), ln=True)
    pdf.ln(3)

    # section 1
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, clean_txt("1. Chakra Snapshot"), ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 6, clean_txt(f"Average Chakra Balance: {profile['avg_score']:.1f} / 10"), ln=True)
    for ch, val in profile["scores"].items():
        pdf.cell(0, 6, clean_txt(f"- {ch}: {val}/10"), ln=True)

    # section 2
    pdf.ln(3)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, clean_txt("2. Your Core Story"), ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 6, clean_txt(chakra_story.get(lowest, "")))
    pdf.multi_cell(0, 6, clean_txt(daily_life))

    # section 3
    pdf.ln(3)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, clean_txt("3. Personality Lens"), ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 6, clean_txt(f"You are showing signs of: {profile['personality']}"))
    pdf.multi_cell(
        0,
        6,
        clean_txt("You respond better to compassionate structure, small actions, and spiritual logic.")
    )

    # section 4
    pdf.ln(3)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, clean_txt("4. 7-Day Soulful Reset Plan"), ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 6, clean_txt(seven_day))

    # section 5
    pdf.ln(3)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, clean_txt("5. Affirmations to Repeat 21 Times"), ln=True)
    pdf.set_font("Arial", "", 11)
    for line in chakra_affirm.get(lowest, []):
        pdf.cell(0, 6, clean_txt(f"- {line}"), ln=True)

    # section 6
    pdf.ln(3)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, clean_txt("6. Recommended Next Step"), ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(
        0,
        6,
        clean_txt("Join a 21-day guided container (Moonathon or Heal Mind & Soul) so that this pattern does not come back.")
    )

    return pdf.output(dest="S").encode("latin-1", "ignore")


# =============== SHOW RESULT ===============
if st.session_state.submitted and st.session_state.profile:
    st.success("Report is ready. Scroll down to download.")
    try:
        pdf_bytes = create_pdf(st.session_state.profile)
        st.download_button(
            label="Download Chakra Report (PDF)",
            data=pdf_bytes,
            file_name=f"{st.session_state.profile['name']}_chakra_report.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    except Exception as e:
        st.error("Could not create PDF. Please simplify text.")
        st.code(str(e))
