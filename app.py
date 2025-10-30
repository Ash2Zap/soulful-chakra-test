def create_pdf(profile: dict) -> bytes:
    import re
    def clean(txt: str) -> str:
        if txt is None:
            return ""
        txt = re.sub(r"[^\x00-\xFF]", "", txt)
        txt = txt.replace("•", "- ").replace("→", "->").replace("—", "-")
        return txt

    LOGO_URL = "https://ik.imagekit.io/86edsgbur/Untitled%20design%20(73)%20(3)%20(1).jpg?updatedAt=1759258123716"
    LOGO_PATH = "soulful_logo.jpg"

    # download logo once
    if not os.path.exists(LOGO_PATH):
        try:
            resp = requests.get(LOGO_URL, timeout=10)
            if resp.status_code == 200:
                with open(LOGO_PATH, "wb") as f:
                    f.write(resp.content)
        except Exception:
            pass

    scores = profile["scores"]
    # lowest chakra for story
    lowest_chakra = sorted(scores.items(), key=lambda x: x[1])[0][0]

    # chakra-specific story text
    chakra_story = {
        "Root": (
            "You have a Root Chakra pattern. This usually forms in childhood when there is too much change, "
            "too much responsibility too early, or when money and safety were not consistent. Because of this, "
            "the nervous system learns to stay alert. You may overmanage, overgive, or hold on to control to feel safe. "
            "Nothing is 'wrong' with you — your body simply chose survival first. Now we can teach it prosperity."
        ),
        "Sacral": (
            "You have a Sacral Chakra pattern. This is the emotional and relationship centre. When this centre is tired, "
            "the person becomes emotional but guarded — you feel a lot, but you do not always feel received. "
            "Very often this is the 'I love everyone but who really sees me?' pattern. That creates attraction to emotionally "
            "unavailable people or relationships with unequal emotional labour. Healing here brings back creativity, sensuality, and joy."
        ),
        "Solar": (
            "You have a Solar Plexus pattern. This is the power, visibility, and pricing centre. Many healers and coaches have this. "
            "You do a lot for others but hesitate to claim your place, raise your price, or be visible because somewhere in the past "
            "visibility was linked with judgment. So the mind says 'I know' but the body says 'not safe.' "
            "We heal this by combining structure with worthiness."
        ),
        "Heart": (
            "You have a Heart Chakra pattern. You are naturally a nurturer. You notice people's pain, you remember details, "
            "and you want everyone to feel included. That is beautiful, but it also made you accept less than you deserved. "
            "Heart patterns are not about romance only — they are about receiving, forgiving, and allowing yourself to be seen "
            "without performing. You do not have to earn love every day."
        ),
        "Throat": (
            "You have a Throat Chakra pattern. You have wisdom, but you have learned to edit yourself. Maybe in childhood you were told "
            "'not now', 'do not say this', or you had to keep family matters private. So the body linked 'expression' with 'rejection'. "
            "Now as a healer/leader, you want to speak but the voice comes late. Healing the throat brings boundaries, bold content, and calm speech."
        ),
        "Third Eye": (
            "You have a Third Eye pattern. This is the overthinking, replaying, mental load pattern. You sense energy fast, you can read people, "
            "but you can also doubt yourself and stay in planning. It happens when the mind was used to stay safe in childhood — scanning, predicting, "
            "pleasing. Now we gently shift from 'thinking for safety' to 'seeing for guidance.'"
        ),
        "Crown": (
            "You have a Crown Chakra pattern. You are spiritually open, but not always grounded. You receive a lot of guidance, dreams, pulls, "
            "but daily routines and money actions do not always match that guidance. This happens when a person is called to be a channel, "
            "but the lower chakras still want safety. We will anchor your spiritual gifts in the body."
        ),
    }

    # daily-life pattern text
    daily_life_text = (
        "How this shows up daily:\n"
        "- You take more emotional responsibility than others.\n"
        "- You know what to do but you do it in bursts, not consistently.\n"
        "- You attract people who love your energy but do not always pour back.\n"
        "- You want a system that understands your feminine pace."
    )

    # 7-day plan
    seven_day_plan = (
        "7-Day Soulful Reset Plan:\n"
        "Day 1 – Awareness: Write the earliest memory connected to this chakra.\n"
        "Day 2 – Energy Cleanse: 108x Ho'oponopono on the main person/situation.\n"
        "Day 3 – Body Anchor: 15 minutes of breath + name the emotion aloud.\n"
        "Day 4 – Expression: Write or record what you never said about this.\n"
        "Day 5 – Money/Value Action: One tangible action (offer, price, ask, boundary).\n"
        "Day 6 – Receive Mode: 30 minutes receiving only (music, nature, self-care).\n"
        "Day 7 – Integration: Journal ‘What did I learn about my soul pattern?’."
    )

    # affirmations by chakra
    chakra_affirm = {
        "Root": [
            "I am fully supported by life.",
            "Money flows to me when I am regulated.",
            "I belong in every room I enter.",
        ],
        "Sacral": [
            "My emotions are allowed.",
            "I can receive love without overgiving.",
            "I attract relationships that honour me.",
        ],
        "Solar": [
            "My power is safe.",
            "Visibility increases my impact.",
            "I deserve to be well paid for my healing.",
        ],
        "Heart": [
            "I deserve gentle love.",
            "I can give without abandoning myself.",
            "It is safe for me to be seen.",
        ],
        "Throat": [
            "My voice is valuable.",
            "I can say no with love.",
            "My truth creates my tribe.",
        ],
        "Third Eye": [
            "I trust my inner guidance.",
            "I do not need to overthink to stay safe.",
            "Clarity comes when I act.",
        ],
        "Crown": [
            "I am guided and protected.",
            "I can be spiritual and prosperous.",
            "Divine ideas flow through me.",
        ],
    }

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # header bars
    pdf.set_fill_color(139, 92, 246)
    pdf.rect(0, 0, 210, 18, "F")
    pdf.set_fill_color(236, 72, 153)
    pdf.rect(0, 18, 6, 279, "F")

    # logo
    if os.path.exists(LOGO_PATH):
        pdf.image(LOGO_PATH, x=10, y=2, w=18)

    # title
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(32, 4)
    pdf.set_font("Arial", "B", 15)
    pdf.cell(0, 8, clean("Soulful Chakra & Behaviour Report"), ln=True)

    # body start
    pdf.set_text_color(0, 0, 0)
    pdf.ln(15)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 7, clean(f"Name: {profile['name']}"), ln=True)
    pdf.cell(0, 7, clean(f"Gender: {profile['gender']}"), ln=True)
    if profile.get("email"):
        pdf.cell(0, 7, clean(f"Email: {profile['email']}"), ln=True)
    pdf.cell(0, 7, clean(f"Generated at: {profile['generated_at']}"), ln=True)
    pdf.ln(3)

    # section 1: scores
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 7, clean("1. Chakra Snapshot"), ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 6, clean(f"Average Chakra Balance: {profile['avg_score']:.1f} / 10"), ln=True)
    pdf.ln(1)
    for ch, val in profile["scores"].items():
        pdf.cell(0, 6, clean(f"- {ch}: {val}/10"), ln=True)

    # section 2: core story
    pdf.ln(3)
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 7, clean("2. Your Core Story"), ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 6, clean(chakra_story.get(lowest_chakra, "")))
    pdf.ln(1)
    pdf.multi_cell(0, 6, clean(daily_life_text))

    # section 3: personality
    pdf.ln(3)
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 7, clean("3. Personality Lens"), ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 6, clean(f"You are showing signs of: {profile['personality']}"))
    pdf.multi_cell(
        0,
        6,
        clean(
            "This means you respond better to compassionate coaching, step-by-step actions, and spiritual logic. "
            "You do not need more information. You need a container that reminds you of your worth and keeps you consistent."
        )
    )

    # section 4: 7 day plan
    pdf.ln(3)
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 7, clean("4. 7-Day Soulful Reset Plan"), ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 6, clean(seven_day_plan))

    # section 5: affirmations
    pdf.ln(3)
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 7, clean("5. Affirmations to Repeat 21 Times"), ln=True)
    pdf.set_font("Arial", "", 11)
    for line in chakra_affirm.get(lowest_chakra, []):
        pdf.cell(0, 6, clean(f"- {line}"), ln=True)

    # section 6: next step
    pdf.ln(3)
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 7, clean("6. Recommended Next Step with Soulful Academy"), ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(
        0,
        6,
        clean(
            "Start with a 21-day guided container (Moonathon / Heal Mind & Soul) so that this pattern does not come back. "
            "One report can give awareness, but community gives momentum. If this report was done for a client, share this with them "
            "and ask them which day they want to start with."
        )
    )

    # footer
    pdf.ln(4)
    pdf.set_font("Arial", "I", 9)
    pdf.multi_cell(0, 5, clean("Soulful Academy · What You Seek Is Seeking You · Auto-generated report from your answers."))

    # return as bytes (ignore non-latin)
    return pdf.output(dest="S").encode("latin-1", "ignore")
