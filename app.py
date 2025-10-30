import streamlit as st
from fpdf import FPDF
import datetime
import os
import requests

st.set_page_config(
    page_title="Soulful Chakra & Behaviour Profiler",
    page_icon="🪬",
    layout="centered"
)

# -------------------------------------------------------------------
# GLOBAL STYLE
# -------------------------------------------------------------------
st.markdown(
    """
    <style>
    .main {
        background: radial-gradient(circle at top, #0f0618 0%, #150020 45%, #0a0a0a 100%);
        color: #fff;
    }
    .shell {
        background: rgba(15,5,26,0.45);
        border: 1px solid rgba(236,72,153,0.25);
        border-radius: 1.5rem;
        padding: 1.1rem 1.4rem 1.1rem 1.4rem;
        backdrop-filter: blur(12px);
        box-shadow: 0 12px 38px rgba(0,0,0,0.22);
        margin-bottom: 1.1rem;
    }
    .title {
        font-size: 1.5rem;
        font-weight: 800;
        letter-spacing: .03em;
        margin-bottom: .1rem;
    }
    .sub {
        font-size: 0.78rem;
        opacity: 0.85;
    }
    .download-btn > button {
        background: linear-gradient(120deg, #f97316 0%, #ec4899 40%, #8b5cf6 100%) !important;
        border: none !important;
        color: white !important;
        font-weight: 600 !important;
        border-radius: 999px !important;
    }
    .email-btn > button {
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
        border-radius: 999px !important;
    }
    /* radios */
    div[role='radiogroup'] {
        gap: 1.5rem !important;
        margin-bottom: 0.3rem !important;
    }
    hr {
        border: none;
        border-bottom: 1px solid rgba(255,255,255,0.04);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------------------------
# 50 QUESTIONS
# -------------------------------------------------------------------
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
    ("I sometimes absorb clients’/family energy.", {"Sacral": -1, "Heart": -1}),
    ("I want rituals I can follow daily.", {"Crown": +1, "Root": +1}),
    ("I know my purpose, I just need confidence.", {"Solar": -1, "Third Eye": +1}),
    ("I keep learning but don’t implement enough.", {"Solar": -1, "Third Eye": -1}),
    ("I want to be spoken to gently, not with too much logic.", {"Heart": -1}),
    ("I respond better when someone gives me 1–2 actions, not 10.", {"Throat": +1}),
    ("I am ready to rise as Soulful Queen / Leader.", {"Solar": +1, "Crown": +1}),
]

TOTAL_QUESTIONS = len(QUESTIONS)
QUESTIONS_PER_PAGE = 10
TOTAL_PAGES = TOTAL_QUESTIONS // QUESTIONS_PER_PAGE  # 5

# -------------------------------------------------------------------
# STATE
# -------------------------------------------------------------------
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

# -------------------------------------------------------------------
# HEADER
# -------------------------------------------------------------------
st.markdown("<div class='shell'>", unsafe_allow_html=True)
st.markdown("<div class='title'>🪬 Soulful Chakra & Behaviour Profiler</div>", unsafe_allow_html=True)
st.markdown("<div class='sub'>5 parts · 10 questions each · energy + personality · FREE mode</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------------------------
# USER INFO
# -------------------------------------------------------------------
col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Name", value=st.session_state.get("name", ""), placeholder="Your name")
    st.session_state["name"] = name
with col2:
    g_default = st.session_state.get("gender", "Female")
    gender = st.radio("Gender", ["Female", "Male", "Other"], horizontal=True,
                      index=["Female", "Male", "Other"].index(g_default))
    st.session_state["gender"] = gender

email = st.text_input("Email (to send report later)", value=st.session_state.get("email", ""), placeholder="queen@example.com")
st.session_state["email"] = email

st.markdown(f"### Part {st.session_state.page} of {TOTAL_PAGES}")

# -------------------------------------------------------------------
# SHOW QUESTIONS FOR CURRENT PAGE (with radio)
# -------------------------------------------------------------------
start_idx = (st.session_state.page - 1) * QUESTIONS_PER_PAGE
end_idx = start_idx + QUESTIONS_PER_PAGE
current_questions = QUESTIONS[start_idx:end_idx]

for i, (qtext, impact) in enumerate(current_questions, start=start_idx + 1):
    ans_key = f"q_{i}"
    prev_val = st.session_state.answers.get(i, "Sometimes")  # default to middle

    st.markdown(f"#### {i}. {qtext}")
    ans = st.radio(
        "",
        ["Yes", "Sometimes", "No"],
        index=["Yes", "Sometimes", "No"].index(prev_val) if prev_val in ["Yes", "Sometimes", "No"] else 1,
        key=ans_key,
        horizontal=True,
    )
    st.session_state.answers[i] = ans
    st.markdown("<hr>", unsafe_allow_html=True)

# -------------------------------------------------------------------
# NAVIGATION
# -------------------------------------------------------------------
col_prev, col_next = st.columns(2)
with col_prev:
    if st.session_state.page > 1:
        if st.button("⬅️ Back"):
            st.session_state.page -= 1
            st.stop()

with col_next:
    if st.session_state.page < TOTAL_PAGES:
        if st.button("Next ➡️"):
            st.session_state.page += 1
            st.stop()
    else:
        # LAST PAGE → GENERATE
        if st.button("✨ Generate Report"):
            # reset chakra scores
            st.session_state.scores = {
                "Root": 5, "Sacral": 5, "Solar": 5,
                "Heart": 5, "Throat": 5, "Third Eye": 5, "Crown": 5
            }
            # apply answers
            for idx, (qtext, impact) in enumerate(QUESTIONS, start=1):
                ans = st.session_state.answers.get(idx, "Sometimes")
                for chakra, delta in impact.items():
                    if ans == "Yes":
                        st.session_state.scores[chakra] += delta
                    elif ans == "Sometimes":
                        st.session_state.scores[chakra] += (delta * 0.5)
                    # "No" → no change

            scores = st.session_state.scores
            avg_score = sum(scores.values()) / len(scores)
            lowest = sorted(scores.items(), key=lambda x: x[1])[:3]
            primary_low = lowest[0][0]

            # personality + real need
            if primary_low == "Root":
                personality = "4. The Safety Seeker"
                real_need = "Safety, money trust, support, grounded spirituality."
            elif primary_low == "Sacral":
                personality = "9. The Lover-Healer"
                real_need = "Emotional permission, receiving love without guilt, clearing old love pain."
            elif primary_low == "Solar":
                personality = "3. The Action Builder"
                real_need = "Power activation, self-worth, visibility without guilt."
            elif primary_low == "Heart":
                personality = "1. The Nurturer Queen"
                real_need = "Forgiveness, self-love, balanced giving, being seen."
            elif primary_low == "Throat":
                personality = "5. The Expressor"
                real_need = "Voice, boundaries, safe expression, softer communication."
            elif primary_low == "Third Eye":
                personality = "2. The Vision Queen"
                real_need = "Mental calm, clarity, trust in guidance."
            else:
                personality = "7. The Mystic"
                real_need = "Surrender, faith, letting the divine lead, but staying grounded."

            st.session_state.profile = {
                "name": st.session_state.get("name") or "Soulful Being",
                "gender": st.session_state.get("gender") or "Female",
                "email": st.session_state.get("email"),
                "scores": scores,
                "avg_score": avg_score,
                "lowest": lowest,
                "personality": personality,
                "real_need": real_need,
                "generated_at": datetime.datetime.now().strftime("%d-%m-%Y %H:%M"),
            }
            st.session_state.submitted = True
            st.stop()

# -------------------------------------------------------------------
# PDF CREATOR (with your logo)
# -------------------------------------------------------------------
def create_pdf(profile: dict) -> bytes:
    LOGO_URL = "https://ik.imagekit.io/86edsgbur/Untitled%20design%20(73)%20(3)%20(1).jpg?updatedAt=1759258123716"
    LOGO_PATH = "soulful_logo.jpg"

    # try to download logo once
    if not os.path.exists(LOGO_PATH):
        try:
            resp = requests.get(LOGO_URL, timeout=10)
            if resp.status_code == 200:
                with open(LOGO_PATH, "wb") as f:
                    f.write(resp.content)
        except Exception:
            pass  # ignore download error; we'll just not show the logo

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # chakra frame
    pdf.set_fill_color(139, 92, 246)  # purple top bar
    pdf.rect(0, 0, 210, 18, "F")
    pdf.set_fill_color(236, 72, 153)  # pink left strip
    pdf.rect(0, 18, 6, 279, "F")

    # logo
    if os.path.exists(LOGO_PATH):
        pdf.image(LOGO_PATH, x=10, y=2, w=18)

    # title
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(32, 4)
    pdf.set_font("Arial", "B", 15)
    pdf.cell(0, 8, "Soulful Chakra & Behaviour Report", ln=True)

    # back to text
    pdf.set_text_color(0, 0, 0)
    pdf.ln(15)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 7, f"Name: {profile['name']}", ln=True)
    pdf.cell(0, 7, f"Gender: {profile['gender']}", ln=True)
    if profile.get("email"):
        pdf.cell(0, 7, f"Email: {profile['email']}", ln=True)
    pdf.cell(0, 7, f"Generated at: {profile['generated_at']}", ln=True)
    pdf.ln(3)

    # chakra overview
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 7, "1. Chakra Overview", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 6, f"Average Chakra Balance: {profile['avg_score']:.1f} / 10", ln=True)
    pdf.ln(2)
    for ch, val in profile["scores"].items():
        pdf.cell(0, 6, f"• {ch}: {val}/10", ln=True)

    # lowest
    pdf.ln(3)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, "Chakras asking for attention:", ln=True)
    pdf.set_font("Arial", "", 11)
    for ch, v in profile["lowest"]:
        pdf.cell(0, 6, f"- {ch} → {v}/10", ln=True)

    # personality
    pdf.ln(3)
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 7, "2. Soulful Personality (9-type)", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 6, f"You are showing signs of: {profile['personality']}")
    personality_desc = {
        "1. The Nurturer Queen": "Heart-first, gives more than receives. Needs boundaries & receiving.",
        "2. The Vision Queen": "Intuitive, future-led. Needs grounding & implementation.",
        "3. The Action Builder": "Gets things done. Needs feminine rest.",
        "4. The Safety Seeker": "Needs stability before expression. Heal root, money, parents.",
        "5. The Expressor": "Truth-first. Heal heart + throat to speak with love.",
        "6. The Harmony Keeper": "Avoids conflict. Needs throat + solar.",
        "7. The Mystic": "Spiritual, needs body anchoring.",
        "8. The Boss Creator": "Leader, needs softness.",
        "9. The Lover-Healer": "Absorbs emotions. Needs sacral cleanse.",
    }
    if profile["personality"] in personality_desc:
        pdf.multi_cell(0, 6, personality_desc[profile["personality"]])

    # communication
    pdf.ln(3)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, "3. How to coach / talk to you", ln=True)
    pdf.set_font("Arial", "", 11)
    if profile["gender"] == "Female":
        pdf.multi_cell(0, 6, "• Start with emotion → then give action.\n• Don't give 10 tasks.\n• Add feminine ritual.")
    elif profile["gender"] == "Male":
        pdf.multi_cell(0, 6, "• Be direct but kind.\n• Give ownership steps.\n• Invite heart/sacral opening.")
    else:
        pdf.multi_cell(0, 6, "• Create safety first.\n• Allow expression.\n• Then give structure.")

    # real need
    pdf.ln(3)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, "4. Your Real Need Right Now", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 6, profile["real_need"])

    # prescription
    pdf.ln(3)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, "5. Soulful Prescription (3 days)", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(
        0,
        6,
        "Day 1 – Reflect: journal earliest memory of today's pain.\n"
        "Day 2 – Rewire: Ho’oponopono 108x on person/situation.\n"
        "Day 3 – Rise: 1 bold aligned action (money / relationship / visibility)."
    )

    # footer
    pdf.ln(3)
    pdf.set_font("Arial", "I", 9)
    pdf.multi_cell(0, 5, "Soulful Academy · What You Seek Is Seeking You · Report auto-generated.")
    return pdf.output(dest="S").encode("latin-1")

# -------------------------------------------------------------------
# SHOW RESULT
# -------------------------------------------------------------------
if st.session_state.submitted and st.session_state.profile:
    st.success("Report is ready ✅ Scroll down to download.")

    pdf_bytes = create_pdf(st.session_state.profile)

    # radiant download
    st.markdown("<div class='download-btn'>", unsafe_allow_html=True)
    st.download_button(
        label="🌈 Download Your Chakra Report (PDF)",
        data=pdf_bytes,
        file_name=f"{st.session_state.profile['name']}_chakra_report.pdf",
        mime="application/pdf",
        use_container_width=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # email placeholder
    st.markdown("<div class='email-btn'>", unsafe_allow_html=True)
    if st.button("📧 Send to Email (connect SMTP later)", use_container_width=True):
        st.info("In live version: connect SendGrid / Gmail API → send this PDF to the above email.")
    st.markdown("</div>", unsafe_allow_html=True)
