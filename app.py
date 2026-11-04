import streamlit as st
import pandas as pd
import plotly.express as px
import html
import re
from pathlib import Path
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, PageBreak, Flowable
)


st.set_page_config(
    page_title="CareerCompass",
    page_icon="🧭",
    layout="wide"
)


# CUSTOM CSS
st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(ellipse at 15% 20%, rgba(80, 90, 255, 0.20), transparent 38%),
        radial-gradient(ellipse at 85% 75%, rgba(130, 65, 255, 0.17), transparent 40%),
        linear-gradient(135deg, #070b18, #101a35, #080d1c);
    color: white;
}

.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    background-image:
        linear-gradient(rgba(140, 160, 255, 0.045) 1px, transparent 1px),
        linear-gradient(90deg, rgba(140, 160, 255, 0.045) 1px, transparent 1px);
    background-size: 45px 45px;
    mask-image: linear-gradient(to bottom, black, transparent 90%);
    z-index: 0;
}

.block-container {
    padding-top: 2rem;
    max-width: 1200px;
}

.hero {
    text-align: center;
    padding: 85px 20px 55px 20px;
}

.logo {
    color: #a9b5ff;
    font-size: 28px;
    font-weight: 900;
    letter-spacing: 7px;
    margin-bottom: 30px;
    text-shadow: 0 0 25px rgba(115, 130, 255, 0.6);
}

.hero h1 {
    font-size: 65px;
    font-weight: 900;
    color: white;
    margin-bottom: 20px;
}

.hero h1 span {
    background: linear-gradient(90deg, #8295ff, #bd8aff, #69dfff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.subtitle {
    font-size: 20px;
    color: #b6c3df;
    max-width: 750px;
    margin: auto;
    line-height: 1.8;
}

.feature {
    background: rgba(23, 33, 59, 0.78);
    border: 1px solid rgba(130, 150, 255, 0.2);
    border-radius: 18px;
    padding: 28px;
    min-height: 180px;
    transition: all 0.3s ease;
}

.feature:hover {
    transform: translateY(-7px);
    border-color: #8295ff;
    box-shadow: 0 10px 35px rgba(80, 100, 255, 0.15);
}

.feature h3 {
    color: #a9b5ff;
    font-size: 21px;
}

.feature p {
    color: #b7c2d9;
    line-height: 1.6;
}

.stButton > button {
    background: linear-gradient(100deg, #526dff, #9365ff, #557dff);
    color: white;
    border: 1px solid rgba(255,255,255,0.18);
    border-radius: 14px;
    min-height: 55px;
    font-size: 18px;
    font-weight: 800;
    box-shadow: 0 8px 30px rgba(91, 105, 255, 0.35);
    transition: all 0.3s ease;
}

.stButton > button:hover {
    transform: scale(1.03);
    box-shadow: 0 10px 40px rgba(120, 100, 255, 0.55);
    color: white;
    border-color: #bdc6ff;
}

.stApp p, .stApp label {
    font-size: 17px;
    line-height: 1.7;
}

.stApp h2 {
    font-size: 32px;
}

.stApp h3 {
    font-size: 24px;
}

.score-card {
    background: rgba(23, 33, 59, 0.85);
    border: 1px solid rgba(130, 150, 255, 0.25);
    border-radius: 16px;
    padding: 22px;
    margin-bottom: 15px;
}

.score-name {
    color: #b6c3df;
    font-size: 17px;
    font-weight: 600;
}

.score-value {
    color: #a9b5ff;
    font-size: 32px;
    font-weight: 800;
    margin: 8px 0;
}

.question-card {
    background: rgba(23, 33, 59, 0.65);
    border: 1px solid rgba(130, 150, 255, 0.2);
    border-radius: 14px;
    padding: 15px;
    margin-bottom: 10px;
}

.summary-card {
    background: linear-gradient(145deg, rgba(40, 53, 94, 0.9), rgba(25, 31, 62, 0.9));
    border: 1px solid rgba(130, 150, 255, 0.3);
    border-radius: 18px;
    padding: 24px;
    min-height: 145px;
    margin-bottom: 12px;
}

.summary-title {
    color: #b6c3df;
    font-size: 16px;
    font-weight: 700;
}

.summary-value {
    color: white;
    font-size: 25px;
    font-weight: 800;
    margin-top: 12px;
}

.overview-banner {
    background: linear-gradient(110deg, rgba(76, 91, 190, 0.35), rgba(135, 75, 190, 0.25));
    border: 1px solid rgba(160, 160, 255, 0.3);
    border-radius: 20px;
    padding: 28px;
    margin: 15px 0 25px 0;
}

/* FLOATING-STYLE RESULT TABS */

/* Tab navigation container */
div[data-testid="stTabs"] {
    margin-top: 15px !important;
}

div[data-testid="stTabs"] [role="tablist"] {
    display: flex !important;
    flex-wrap: wrap !important;
    gap: 12px !important;
    border-bottom: none !important;
    padding: 12px 5px 18px 5px !important;
    overflow: visible !important;
}

/* Individual tab buttons - support Streamlit/BaseWeb versions */
div[data-testid="stTabs"] button[role="tab"],
div[data-testid="stTabs"] button[data-baseweb="tab"],
div[data-testid="stTabs"] [data-baseweb="tab"] {
    appearance: none !important;
    -webkit-appearance: none !important;
    background: rgba(23, 33, 59, 0.95) !important;
    color: #c5cee8 !important;
    border: 1px solid rgba(130, 150, 255, 0.40) !important;
    border-radius: 14px !important;
    padding: 12px 20px !important;
    min-height: 48px !important;
    font-size: 15px !important;
    font-weight: 800 !important;
    box-shadow: 0 5px 18px rgba(30, 45, 110, 0.28) !important;
    transition: all 0.25s ease !important;
    margin: 0 !important;
}

/* Text inside tabs */
div[data-testid="stTabs"] button[role="tab"] p,
div[data-testid="stTabs"] [data-baseweb="tab"] p {
    color: inherit !important;
    font-size: 15px !important;
    font-weight: 800 !important;
    margin: 0 !important;
}

/* Remove Streamlit's default active underline */
div[data-testid="stTabs"] button[role="tab"]::after,
div[data-testid="stTabs"] [data-baseweb="tab"]::after {
    display: none !important;
    height: 0 !important;
    background: transparent !important;
}

/* Hover effect */
div[data-testid="stTabs"] button[role="tab"]:hover,
div[data-testid="stTabs"] [data-baseweb="tab"]:hover {
    background: rgba(75, 91, 160, 0.90) !important;
    color: white !important;
    border-color: #8295ff !important;
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 24px rgba(80, 100, 255, 0.35) !important;
}

/* Selected tab */
div[data-testid="stTabs"] button[role="tab"][aria-selected="true"],
div[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(100deg, #526dff, #9365ff, #557dff) !important;
    color: white !important;
    border: 1px solid rgba(255, 255, 255, 0.55) !important;
    box-shadow: 0 8px 28px rgba(91, 105, 255, 0.48) !important;
}

/* Ensure selected tab text also stays white */
div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] p,
div[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"] p {
    color: white !important;
}

</style>
""", unsafe_allow_html=True)


# ASSESSMENT QUESTIONS

questions = [
    {"question": "I enjoy building or repairing physical objects.", "type": "R"},
    {"question": "I like working with machines and tools.", "type": "R"},
    {"question": "I enjoy practical, hands-on activities.", "type": "R"},

    {"question": "I enjoy solving complex mathematical problems.", "type": "I"},
    {"question": "I like investigating how things work.", "type": "I"},
    {"question": "I enjoy analysing data and finding patterns.", "type": "I"},

    {"question": "I enjoy designing creative solutions.", "type": "A"},
    {"question": "I like drawing, designing or creating things.", "type": "A"},
    {"question": "I enjoy experimenting with new ideas.", "type": "A"},

    {"question": "I enjoy teaching or explaining concepts to others.", "type": "S"},
    {"question": "I like helping people solve their problems.", "type": "S"},
    {"question": "I enjoy working in a team.", "type": "S"},

    {"question": "I enjoy leading a team or project.", "type": "E"},
    {"question": "I like convincing others about my ideas.", "type": "E"},
    {"question": "I enjoy making decisions and taking responsibility.", "type": "E"},

    {"question": "I enjoy organising information and records.", "type": "C"},
    {"question": "I like working with structured data and spreadsheets.", "type": "C"},
    {"question": "I enjoy planning tasks and following organised processes.", "type": "C"}
]

interest_names = {
    "R": "Realistic",
    "I": "Investigative",
    "A": "Artistic",
    "S": "Social",
    "E": "Enterprising",
    "C": "Conventional"
}

academic_questions = [
    "Mathematics",
    "Physics",
    "Chemistry",
    "Biology",
    "Computer Science"
]

skill_questions = [
    "Programming",
    "Analytical Thinking",
    "Problem Solving",
    "Creativity and Design",
    "Communication",
    "Practical and Hands-on Work"
]

learning_roadmap = {
    "Programming": "Learn Python, Java and basic programming concepts.",
    "Analytical Thinking": "Practise logical reasoning, mathematics and data analysis.",
    "Problem Solving": "Work on real-world problems and technical projects.",
    "Creativity and Design": "Explore CAD tools, design software and creative projects.",
    "Communication": "Improve presentation, writing and teamwork skills.",
    "Practical and Hands-on Work": "Build prototypes and perform practical experiments."
}

preference_questions = {
    "How do you prefer working?": [
        "Working independently",
        "Working in a team",
        "A balance of both"
    ],
    "Which type of activity interests you more?": [
        "Practical projects",
        "Theoretical research",
        "A combination of both"
    ],
    "What kind of work environment do you prefer?": [
        "Structured tasks and clear plans",
        "Flexible tasks and creative freedom",
        "A balance of both"
    ],
    "What would you rather work with?": [
        "Technology and machines",
        "People and communication",
        "Both technology and people"
    ]
}

goal_questions = {
    "What matters most to you in a career?": [
        "High salary",
        "Job security",
        "Innovation",
        "Social impact"
    ],
    "Which career path are you considering?": [
        "Getting a job",
        "Higher studies or research",
        "Entrepreneurship",
        "Not sure yet"
    ],
    "Would you like to pursue further education?": [
        "Yes",
        "No",
        "Maybe"
    ],
    "What is your biggest career priority?": [
        "Work-life balance",
        "Career growth",
        "Financial rewards",
        "Meaningful work"
    ]
}


# HELPER FUNCTIONS

def show_progress(value):
    st.progress(value)


def show_score_card(name, score, maximum=100):
    st.markdown(f"""
    <div class="score-card">
        <div class="score-name">{name}</div>
        <div class="score-value">{score:.1f}{'%' if maximum == 100 else '/5'}</div>
    </div>
    """, unsafe_allow_html=True)
    st.progress(min(int(score / maximum * 100), 100))


def show_summary_card(name, value):
    st.markdown(f"""
    <div class="summary-card">
        <div class="summary-title">{name}</div>
        <div class="summary-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)


def make_interest_chart(scores, height=380):
    chart_data = pd.DataFrame({
        "Interest": list(scores.keys()),
        "Score": list(scores.values())
    })

    fig = px.bar(
        chart_data,
        x="Interest",
        y="Score",
        text="Score"
    )

    fig.update_traces(
        width=0.45,
        texttemplate="%{text:.1f}%",
        textposition="outside",
        marker_color="#8295ff"
    )

    fig.update_layout(
        height=height,
        yaxis_range=[0, 110],
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        xaxis_title="Interest Area",
        yaxis_title="Interest Score (%)",
        bargap=0.45,
        margin=dict(t=40, b=40)
    )

    return fig



# CAREER MATCHING ENGINE

RIASEC_COLUMNS = [
    "Realistic", "Investigative", "Artistic",
    "Social", "Enterprising", "Conventional"
]

ACADEMIC_MAPPING = {
    "Mathematics": "Mathematics_x",
    "Physics": "Physics",
    "Chemistry": "Chemistry",
    "Biology": "Biology",
    "Computer Science": "Computers and Electronics"
}

SKILL_MAPPING = {
    "Programming": ["Computers and Electronics"],
    "Analytical Thinking": ["Critical Thinking"],
    "Problem Solving": ["Problem Sensitivity", "Deductive Reasoning"],
    "Creativity and Design": ["Originality", "Design"],
    "Communication": ["Speaking", "Active Listening"],
    "Practical and Hands-on Work": ["Manual Dexterity", "Control Precision"]
}


@st.cache_data
def load_career_profiles():
    data_path = (
        Path(__file__).resolve().parent
        / "Data" / "Processed" / "career_profiles.csv"
    )

    if not data_path.exists():
        raise FileNotFoundError(
            "career_profiles.csv was not found. Place it inside Data/Processed/"
        )

    profiles = pd.read_csv(data_path)

    required_columns = (
        ["Title", "Branch"]
        + RIASEC_COLUMNS
        + list(ACADEMIC_MAPPING.values())
        + [column for columns in SKILL_MAPPING.values() for column in columns]
    )

    missing_columns = [
        column for column in required_columns
        if column not in profiles.columns
    ]

    if missing_columns:
        raise ValueError(
            "The career dataset is missing required columns: "
            + ", ".join(missing_columns)
        )

    if profiles.empty:
        raise ValueError("The career dataset contains no career profiles.")

    return profiles


def calculate_career_matches(
    profiles, interest_scores, academic_scores, skill_scores
):
    career_percentages = profiles.copy()

    # Convert O*NET interest values from 1–7 to percentages.
    career_percentages[RIASEC_COLUMNS] = (
        career_percentages[RIASEC_COLUMNS] / 7
    ) * 100

    # Interest Match: 100 minus the average RIASEC difference.
    interest_differences = career_percentages[RIASEC_COLUMNS].sub(
        pd.Series(interest_scores)
    ).abs()

    interest_match = 100 - interest_differences.mean(axis=1)

    best_interest_areas = interest_differences.apply(
        lambda row: ", ".join(row.nsmallest(3).index),
        axis=1
    )

    # Academic Match: compare student ratings with O*NET knowledge features.
    academic_values = {}

    for subject, column in ACADEMIC_MAPPING.items():
        academic_values[column] = academic_scores[subject]

    academic_columns = list(ACADEMIC_MAPPING.values())

    academic_differences = profiles[academic_columns].sub(
        pd.Series(academic_values)
    ).abs()

    academic_match = (
        100 - (academic_differences.mean(axis=1) / 4 * 100)
    )

    # Capability Alignment: compare self-ratings with mapped O*NET skills.
    skill_differences = pd.DataFrame(index=profiles.index)

    for skill, columns in SKILL_MAPPING.items():
        required_level = profiles[columns].mean(axis=1)
        student_level = skill_scores[skill]
        skill_differences[skill] = (
            required_level - student_level
        ).abs()

    capability_alignment = (
        100 - (skill_differences.mean(axis=1) / 4 * 100)
    )

    # Preserve the notebook's 40% + 30% + 30% formula.
    matches = profiles[["Title", "Branch"]].copy()
    matches["Interest Match"] = interest_match
    matches["Academic Match"] = academic_match
    matches["Capability Alignment"] = capability_alignment
    matches["Overall Match"] = (
        matches["Interest Match"] * 0.40
        + matches["Academic Match"] * 0.30
        + matches["Capability Alignment"] * 0.30
    )
    matches["Best Matching Interests"] = best_interest_areas

    return matches.sort_values(
        by="Overall Match", ascending=False
    ).reset_index(drop=True)


# PDF REPORT FUNCTIONS

class ScoreBar(Flowable):
    def __init__(self, label, score, max_score=100):
        Flowable.__init__(self)
        self.label = label
        self.score = score
        self.max_score = max_score
        self.width = 460
        self.height = 35

    def draw(self):
        c = self.canv

        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(colors.HexColor("#26345D"))
        c.drawString(0, 22, self.label)

        value = self.score / self.max_score * 100

        c.setFillColor(colors.HexColor("#E7EAF5"))
        c.roundRect(0, 5, 370, 10, 5, fill=1, stroke=0)

        c.setFillColor(colors.HexColor("#6679E8"))
        c.roundRect(0, 5, 370 * value / 100, 10, 5, fill=1, stroke=0)

        c.setFillColor(colors.HexColor("#26345D"))
        c.setFont("Helvetica-Bold", 9)

        if self.max_score == 5:
            display = f"{self.score}/5"
        else:
            display = f"{self.score:.1f}%"

        c.drawString(385, 7, display)


def create_pdf():
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=27,
        leading=33,
        textColor=colors.HexColor("#5267D8"),
        alignment=TA_CENTER,
        spaceAfter=12
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontSize=11,
        leading=17,
        textColor=colors.HexColor("#59627A"),
        alignment=TA_CENTER,
        spaceAfter=20
    )

    heading_style = ParagraphStyle(
        "ReportHeading",
        parent=styles["Heading2"],
        fontSize=17,
        leading=22,
        textColor=colors.HexColor("#5267D8"),
        spaceBefore=14,
        spaceAfter=10
    )

    normal_style = ParagraphStyle(
        "ReportBody",
        parent=styles["BodyText"],
        fontSize=10,
        leading=15,
        textColor=colors.HexColor("#30384D"),
        spaceAfter=7
    )

    story = []

    interest_scores = st.session_state.interest_scores
    academic_scores = st.session_state.academic_scores
    skill_scores = st.session_state.skill_scores
    preferences = st.session_state.preferences
    goals = st.session_state.goals
    student_name = st.session_state.get("student_name", "Student")

    top_interest = max(interest_scores, key=interest_scores.get)
    top_subject = max(academic_scores, key=academic_scores.get)
    top_skill = max(skill_scores, key=skill_scores.get)

    # COVER
    story.append(Spacer(1, 35 * mm))
    story.append(Paragraph("CAREERCOMPASS", title_style))
    story.append(Paragraph(
        "YOUR PERSONAL CAREER & EDUCATION PROFILE",
        subtitle_style
    ))
    story.append(Paragraph(
        f"Prepared for <b>{escape(student_name)}</b>",
        subtitle_style
    ))
    story.append(Spacer(1, 15 * mm))

    cover_data = [
        ["YOUR STRONGEST INTEREST", "YOUR STRONGEST SUBJECT"],
        [top_interest, top_subject],
        ["YOUR STRONGEST CAPABILITY", "ASSESSMENT COMPLETED"],
        [top_skill, "5 Assessment Stages"]
    ]

    cover_table = Table(cover_data, colWidths=[80 * mm, 80 * mm], rowHeights=[10 * mm, 17 * mm, 10 * mm, 17 * mm])

    cover_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F0F2FC")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#26345D")),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#D7DDF5")),
        ("INNERGRID", (0, 0), (-1, -1), 0.6, colors.white),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9)
    ]))

    story.append(cover_table)
    story.append(Spacer(1, 20 * mm))
    story.append(Paragraph(
        "This report brings together your interests, academic confidence, "
        "self-reported capabilities, work preferences and career goals.",
        normal_style
    ))

    story.append(PageBreak())

    # INTERESTS
    story.append(Paragraph("01 | Your Interest Profile", heading_style))
    story.append(Paragraph(
        "Your RIASEC results describe the interest areas that appeared "
        "most strongly in your responses.",
        normal_style
    ))

    for name, score in interest_scores.items():
        story.append(ScoreBar(name, score))

    story.append(Spacer(1, 8 * mm))

    # ACADEMICS
    story.append(Paragraph("02 | Academic Profile", heading_style))
    story.append(Paragraph(
        "These ratings represent your own confidence in each subject.",
        normal_style
    ))

    for subject, score in academic_scores.items():
        story.append(ScoreBar(subject, score, 5))

    highest = max(academic_scores.values())
    lowest = min(academic_scores.values())

    strongest = [
        s for s, v in academic_scores.items() if v == highest
    ]

    improvement = [
        s for s, v in academic_scores.items() if v == lowest
    ]

    story.append(Paragraph(
        f"<b>Strongest subject area(s):</b> {', '.join(strongest)}",
        normal_style
    ))

    story.append(Paragraph(
        f"<b>Area(s) to improve:</b> {', '.join(improvement)}",
        normal_style
    ))

    # SKILLS
    story.append(Paragraph("03 | Skills & Capabilities", heading_style))
    story.append(Paragraph(
        "These ratings reflect your self-reported current abilities.",
        normal_style
    ))

    for skill, score in skill_scores.items():
        story.append(ScoreBar(skill, score, 5))

    story.append(Paragraph("<b>Suggested learning areas</b>", normal_style))

    for skill, score in sorted(skill_scores.items(), key=lambda x: x[1])[:2]:
        story.append(Paragraph(
            f"<b>{skill}:</b> {learning_roadmap[skill]}",
            normal_style
        ))

    story.append(PageBreak())

    # CAREER MATCHES
    career_matches = st.session_state.career_matches

    story.append(Paragraph("04 | Your Career Matches", heading_style))
    story.append(Paragraph(
        "These compatibility scores compare your interests, academic "
        "confidence and self-reported capabilities with career profiles "
        "in the O*NET-derived dataset.",
        normal_style
    ))

    for rank, career in career_matches.head(5).iterrows():
        story.append(Paragraph(
            f"<b>{rank + 1}. {escape(str(career['Title']))}</b> "
            f"({escape(str(career['Branch']))}) — "
            f"{career['Overall Match']:.2f}% overall match",
            normal_style
        ))
        story.append(Paragraph(
            f"Interest: {career['Interest Match']:.2f}% | "
            f"Academics: {career['Academic Match']:.2f}% | "
            f"Capabilities: {career['Capability Alignment']:.2f}%",
            normal_style
        ))
        story.append(Paragraph(
            "Closest interest areas: "
            + escape(str(career["Best Matching Interests"])),
            normal_style
        ))

    story.append(Paragraph(
        "Overall Match = 40% Interest Match + 30% Academic Match "
        "+ 30% Capability Alignment. Work preferences and career goals "
        "guide exploration but do not change the numerical score. "
        "These are compatibility indicators, not probabilities of career success.",
        normal_style
    ))

    # WORK STYLE
    story.append(Paragraph("05 | Your Work Style", heading_style))

    preference_data = [["WORK PREFERENCE", "YOUR RESPONSE"]]

    for question, answer in preferences.items():
        preference_data.append([question, answer])

    preference_table = Table(
        preference_data,
        colWidths=[85 * mm, 75 * mm]
    )

    preference_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#5267D8")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F0F2FC")),
        ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor("#26345D")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.white),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9)
    ]))

    story.append(preference_table)

    # GOALS
    story.append(Paragraph("06 | Your Career Goals", heading_style))

    goal_data = [["CAREER QUESTION", "YOUR RESPONSE"]]

    for question, answer in goals.items():
        goal_data.append([question, answer])

    goal_table = Table(
        goal_data,
        colWidths=[85 * mm, 75 * mm]
    )

    goal_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#5267D8")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F0F2FC")),
        ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor("#26345D")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.white),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9)
    ]))

    story.append(goal_table)

    story.append(Spacer(1, 12 * mm))

    story.append(Paragraph("A Note About Your Results", heading_style))

    story.append(Paragraph(
        "This report reflects your responses and self-reported confidence. "
        "It is an exploratory guide, not a prediction of career success, "
        "a professional assessment or a measure of university admission eligibility. "
        "Your interests and abilities can develop over time.",
        normal_style
    ))

    def add_page_number(canvas, document):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#7B849C"))
        canvas.drawString(20 * mm, 12 * mm, f"CAREERCOMPASS | {student_name} | PERSONAL REPORT")
        canvas.drawRightString(
            A4[0] - 20 * mm,
            12 * mm,
            f"Page {document.page}"
        )
        canvas.restoreState()

    doc.build(
        story,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number
    )

    buffer.seek(0)
    return buffer.getvalue()


# PAGE NAVIGATION

if "page" not in st.session_state:
    st.session_state.page = "home"


# HOME PAGE

if st.session_state.page == "home":

    st.markdown("""
    <div class="hero">
        <div class="logo">✧ CAREERCOMPASS ✧</div>
        <h1>Discover Your <span>Direction.</span></h1>
        <p class="subtitle">
            Your interests, strengths and ambitions deserve a career
            that fits. Explore personalised career paths and build
            a roadmap towards your future.
        </p>
    </div>
    """, unsafe_allow_html=True)

    left, center, right = st.columns([1, 2, 1])

    with center:
        if st.button("✦ START YOUR ASSESSMENT →", use_container_width=True):
            st.session_state.page = "intro"
            st.rerun()

    st.write("")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="feature">
            <h3>🎯 Career Matches</h3>
            <p>Discover career paths aligned with your interests,
            academic profile and capabilities.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature">
            <h3>📊 Personal Insights</h3>
            <p>Understand your academic strengths, preferences
            and areas you can develop.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature">
            <h3>🚀 Future Roadmap</h3>
            <p>Explore learning recommendations and possible
            directions for your future.</p>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.caption("CAREERCOMPASS • Explore. Understand. Grow.")


# INTRODUCTION

elif st.session_state.page == "intro":

    st.markdown("""
    <div class="hero">
        <div class="logo">YOUR JOURNEY STARTS HERE</div>
        <h1>Let's Discover Your <span>Future.</span></h1>
        <p class="subtitle">
            Answer questions about yourself to discover
            career paths that match your interests and goals.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.info("Your assessment has 5 stages and takes approximately 5–7 minutes.")

    st.markdown("### First, what should we call you?")
    st.text_input(
        "Enter your name",
        placeholder="Your full name",
        key="student_name_input",
        label_visibility="collapsed"
    )

    st.markdown("### What we'll explore")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**01 — Your Interests**")
        st.write("Discover what activities and subjects attract you.")
        st.markdown("**02 — Academic Profile**")
        st.write("Understand your confidence across academic subjects.")
        st.markdown("**03 — Skills & Capabilities**")
        st.write("Explore your current strengths and abilities.")

    with col2:
        st.markdown("**04 — Work Preferences**")
        st.write("Tell us about your preferred working environment.")
        st.markdown("**05 — Career Goals**")
        st.write("Share your ambitions and future priorities.")

    if st.button("Begin Stage 1 →", use_container_width=True):
        student_name = st.session_state.get("student_name_input", "").strip()

        if student_name:
            st.session_state.student_name = student_name
            st.session_state.page = "interests"
            st.rerun()
        else:
            st.warning("Please enter your name before starting the assessment.")


# STAGE 1 — INTERESTS

elif st.session_state.page == "interests":

    st.markdown("## Stage 1 of 5 — Discover Your Interests")
    show_progress(0.20)

    st.write("Rate each statement based on how much you enjoy or identify with it.")
    st.caption("1 = Strongly Disagree | 5 = Strongly Agree")

    with st.form("interest_form"):

        answers = []

        for i, item in enumerate(questions):

            st.markdown(
                f'<div class="question-card"><p style="font-size:21px; font-weight:600;">{item["question"]}</p></div>',
                unsafe_allow_html=True
            )

            answer = st.slider(
                "Your response",
                1, 5, 3,
                key=f"interest_{i}",
                label_visibility="collapsed"
            )

            answers.append(answer)

        submitted = st.form_submit_button(
            "Submit Interests →",
            use_container_width=True
        )

    if submitted:

        interest_totals = {
            "R": 0, "I": 0, "A": 0,
            "S": 0, "E": 0, "C": 0
        }

        for i, item in enumerate(questions):
            interest_totals[item["type"]] += answers[i]

        interest_scores = {}

        for code in interest_totals:
            name = interest_names[code]
            interest_scores[name] = interest_totals[code] / 15 * 100

        st.session_state.interest_scores = interest_scores
        st.session_state.page = "interests_result"
        st.rerun()


# INTEREST RESULTS

elif st.session_state.page == "interests_result":

    st.markdown("## Your Interest Profile")
    show_progress(0.20)

    interest_scores = st.session_state.interest_scores

    st.success("Your interest assessment has been completed!")

    col1, col2 = st.columns(2)

    for i, (name, score) in enumerate(interest_scores.items()):
        if i % 2 == 0:
            with col1:
                show_score_card(name, score)
        else:
            with col2:
                show_score_card(name, score)

    st.markdown("### Interest Comparison")
    st.plotly_chart(
        make_interest_chart(interest_scores),
        use_container_width=True
    )

    if st.button("Continue to Academic Profile →", use_container_width=True):
        st.session_state.page = "academic"
        st.rerun()


# STAGE 2 — ACADEMIC PROFILE

elif st.session_state.page == "academic":

    st.markdown("## Stage 2 of 5 — Academic Profile")
    show_progress(0.40)

    st.write("Rate your current confidence in each academic subject.")
    st.caption("1 = Very Low | 5 = Very High")

    with st.form("academic_form"):

        academic_scores = {}

        for subject in academic_questions:

            st.markdown(
                f'<div class="question-card"><p style="font-size:21px; font-weight:600;">{subject}</p></div>',
                unsafe_allow_html=True
            )

            academic_scores[subject] = st.slider(
                "Your confidence",
                1, 5, 3,
                key=f"academic_{subject}",
                label_visibility="collapsed"
            )

        submitted = st.form_submit_button(
            "Submit Academic Profile →",
            use_container_width=True
        )

    if submitted:
        st.session_state.academic_scores = academic_scores
        st.session_state.page = "academic_result"
        st.rerun()


# ACADEMIC RESULTS

elif st.session_state.page == "academic_result":

    st.markdown("## Your Academic Snapshot")
    show_progress(0.40)

    academic_scores = st.session_state.academic_scores

    st.success("Your academic profile has been saved.")

    col1, col2 = st.columns(2)

    for i, (subject, score) in enumerate(academic_scores.items()):
        if i % 2 == 0:
            with col1:
                show_score_card(subject, score, 5)
        else:
            with col2:
                show_score_card(subject, score, 5)

    highest = max(academic_scores.values())
    lowest = min(academic_scores.values())

    if highest == lowest:
        st.info("You rated all subjects equally.")
    else:
        strongest = [
            s for s, v in academic_scores.items() if v == highest
        ]
        improvement = [
            s for s, v in academic_scores.items() if v == lowest
        ]

        st.markdown("### Your Academic Insights")
        st.write("**Strongest subject area(s):** " + ", ".join(strongest))
        st.write("**Subject area(s) to improve:** " + ", ".join(improvement))

    if st.button("Continue to Skills & Capabilities →", use_container_width=True):
        st.session_state.page = "skills"
        st.rerun()


# STAGE 3 — SKILLS

elif st.session_state.page == "skills":

    st.markdown("## Stage 3 of 5 — Skills & Capabilities")
    show_progress(0.60)

    st.write("Rate your current ability in each area.")
    st.caption("1 = Beginner | 5 = Very Confident")

    with st.form("skills_form"):

        skill_scores = {}

        for skill in skill_questions:

            st.markdown(
                f'<div class="question-card"><p style="font-size:21px; font-weight:600;">{skill}</p></div>',
                unsafe_allow_html=True
            )

            skill_scores[skill] = st.slider(
                "Your current ability",
                1, 5, 3,
                key=f"skill_{skill}",
                label_visibility="collapsed"
            )

        submitted = st.form_submit_button(
            "Submit Skills →",
            use_container_width=True
        )

    if submitted:
        st.session_state.skill_scores = skill_scores
        st.session_state.page = "skills_result"
        st.rerun()


# SKILLS RESULTS

elif st.session_state.page == "skills_result":

    st.markdown("## Your Skills Snapshot")
    show_progress(0.60)

    skill_scores = st.session_state.skill_scores

    st.success("Your skills profile has been saved.")

    col1, col2 = st.columns(2)

    for i, (skill, score) in enumerate(skill_scores.items()):
        if i % 2 == 0:
            with col1:
                show_score_card(skill, score, 5)
        else:
            with col2:
                show_score_card(skill, score, 5)

    st.markdown("### Suggested Learning Areas")

    sorted_skills = sorted(
        skill_scores.items(),
        key=lambda x: x[1]
    )

    for skill, score in sorted_skills[:2]:
        st.markdown(f"**{skill}**")
        st.write(learning_roadmap[skill])

    if st.button("Continue to Work Preferences →", use_container_width=True):
        st.session_state.page = "preferences"
        st.rerun()


# STAGE 4 — WORK PREFERENCES

elif st.session_state.page == "preferences":

    st.markdown("## Stage 4 of 5 — Work Preferences")
    show_progress(0.80)

    st.write("Choose the options that best describe your preferred working style.")

    with st.form("preferences_form"):

        preferences = {}

        for question, options in preference_questions.items():

            st.markdown(
                f'<div class="question-card"><p style="font-size:21px; font-weight:600;">{question}</p></div>',
                unsafe_allow_html=True
            )

            preferences[question] = st.radio(
                "Select one",
                options,
                key=f"preference_{question}",
                label_visibility="collapsed"
            )

        submitted = st.form_submit_button(
            "Submit Work Preferences →",
            use_container_width=True
        )

    if submitted:
        st.session_state.preferences = preferences
        st.session_state.page = "preferences_result"
        st.rerun()


# WORK PREFERENCE RESULTS

elif st.session_state.page == "preferences_result":

    st.markdown("## Your Work Style")
    show_progress(0.80)

    st.success("Your work preferences have been saved.")

    for question, answer in st.session_state.preferences.items():
        st.markdown(f"**{question}**")
        st.write(answer)
        st.divider()

    if st.button("Continue to Career Goals →", use_container_width=True):
        st.session_state.page = "goals"
        st.rerun()


# STAGE 5 — CAREER GOALS

elif st.session_state.page == "goals":

    st.markdown("## Stage 5 of 5 — Career Goals")
    show_progress(1.0)

    st.write("Tell us what matters most to you when planning your future.")

    with st.form("goals_form"):

        goals = {}

        for question, options in goal_questions.items():

            st.markdown(
                f'<div class="question-card"><p style="font-size:21px; font-weight:600;">{question}</p></div>',
                unsafe_allow_html=True
            )

            goals[question] = st.radio(
                "Select one",
                options,
                key=f"goal_{question}",
                label_visibility="collapsed"
            )

        submitted = st.form_submit_button(
            "Complete Assessment →",
            use_container_width=True
        )

    if submitted:
        st.session_state.goals = goals
        st.session_state.page = "final_results"
        st.rerun()


# FINAL RESULTS DASHBOARD

elif st.session_state.page == "final_results":

    interest_scores = st.session_state.interest_scores
    academic_scores = st.session_state.academic_scores
    skill_scores = st.session_state.skill_scores
    preferences = st.session_state.preferences
    goals = st.session_state.goals
    student_name = st.session_state.get("student_name", "Student")
    safe_student_name = html.escape(student_name)

    top_interest = max(interest_scores, key=interest_scores.get)
    top_subject = max(academic_scores, key=academic_scores.get)
    top_skill = max(skill_scores, key=skill_scores.get)

    try:
        career_profiles = load_career_profiles()
        career_matches = calculate_career_matches(
            career_profiles,
            interest_scores,
            academic_scores,
            skill_scores
        )
        st.session_state.career_matches = career_matches
    except (FileNotFoundError, ValueError) as error:
        st.error(str(error))
        st.info(
            "Check that Data/Processed/career_profiles.csv is included "
            "in your project folder."
        )
        st.stop()

    top_career = career_matches.iloc[0]

    st.markdown(f"""
    <div class="hero" style="padding-top:35px;">
        <div class="logo">✧ CAREERCOMPASS ✧</div>
        <h1>Welcome, <span>{safe_student_name}.</span></h1>
        <p class="subtitle">
            Your personal CareerCompass dashboard is ready. Explore your
            assessment results, understand your strengths and discover
            the direction you may want to pursue.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="overview-banner">
        <h2 style="color:white;">Assessment Completed, {safe_student_name} ✨</h2>
        <p style="color:#d0d8f5;">
            You have completed all five stages. Your responses are
            organised below so you can explore each part of your profile.
        </p>
    </div>
    """, unsafe_allow_html=True)
        # OVERVIEW CARDS

    col1, col2, col3 = st.columns(3)

    with col1:
        show_summary_card("✦ Strongest Interest", top_interest)

    with col2:
        show_summary_card("✦ Strongest Subject", top_subject)

    with col3:
        show_summary_card("✦ Strongest Capability", top_skill)

    st.markdown("### Your Leading Career Match")
    show_summary_card(
        f"#{1} {top_career['Branch']}",
        f"{top_career['Title']} — {top_career['Overall Match']:.1f}%"
    )

    st.markdown("## Your Profile at a Glance")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Interest Profile")
        st.plotly_chart(
            make_interest_chart(interest_scores, 320),
            use_container_width=True
        )

    with col2:
        st.markdown("### Academic Confidence")

        academic_chart = pd.DataFrame({
            "Subject": list(academic_scores.keys()),
            "Confidence": [
                score * 20 for score in academic_scores.values()
            ]
        })

        fig = px.bar(
            academic_chart,
            x="Subject",
            y="Confidence",
            text="Confidence"
        )

        fig.update_traces(
            width=0.5,
            texttemplate="%{text:.0f}%",
            textposition="outside",
            marker_color="#8D72E8"
        )

        fig.update_layout(
            height=320,
            yaxis_range=[0, 110],
            showlegend=False,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="white",
            xaxis_title="Subject",
            yaxis_title="Confidence (%)"
        )

        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("## Explore Your Results")

    # SEVEN HORIZONTAL TABS
    tab_overview, tab_careers, tab_interest, tab_academic, tab_skills, tab_work, tab_goals, tab_pdf = st.tabs([
        "✦ Overview",
        "🏆 Career Matches",
        "🎯 Interests",
        "📚 Academics",
        "⚡ Skills",
        "🧩 Work Style",
        "🚀 Career Goals",
        "📄 PDF Report"
    ])

    # OVERVIEW TAB
    with tab_overview:

        st.markdown("### Your Personal Snapshot")

        col1, col2 = st.columns(2)

        with col1:
            show_summary_card("Top Interest Area", top_interest)
            show_summary_card("Top Academic Subject", top_subject)

        with col2:
            show_summary_card("Strongest Capability", top_skill)
            show_summary_card(
                "Career Path Preference",
                goals["Which career path are you considering?"]
            )

        st.markdown("### Your Current Development Priorities")

        weakest_skills = sorted(
            skill_scores.items(),
            key=lambda x: x[1]
        )[:2]

        for skill, score in weakest_skills:
            st.markdown(f"**{skill}** — {score}/5")
            st.write(learning_roadmap[skill])

        st.info(
            "These results are an exploratory snapshot based on your "
            "responses. They do not predict career success."
        )

    # CAREER MATCHES TAB
    with tab_careers:

        st.markdown("### Your Top Career Recommendations")
        st.write(
            "Your careers are ranked using your interest profile, "
            "academic confidence and self-reported capabilities."
        )

        top_career = career_matches.iloc[0]
        col1, col2, col3 = st.columns(3)

        with col1:
            show_summary_card("Top Career", top_career["Title"])

        with col2:
            show_summary_card(
                "Overall Compatibility",
                f"{top_career['Overall Match']:.1f}%"
            )

        with col3:
            show_summary_card("Career Branch", top_career["Branch"])

        st.markdown("### Top 10 Career Matches")

        career_table = career_matches.head(10)[[
            "Title", "Branch", "Interest Match",
            "Academic Match", "Capability Alignment", "Overall Match"
        ]].copy()

        career_table = career_table.rename(columns={
            "Title": "Career",
            "Interest Match": "Interest (%)",
            "Academic Match": "Academics (%)",
            "Capability Alignment": "Capabilities (%)",
            "Overall Match": "Overall Match (%)"
        })

        st.dataframe(
            career_table.round(2),
            use_container_width=True,
            hide_index=True
        )

        st.markdown("### Why These Careers Match")

        for rank, career in career_matches.head(10).iterrows():
            with st.expander(
                f"#{rank + 1} {career['Title']} — "
                f"{career['Overall Match']:.1f}%"
            ):
                st.write(f"**Branch:** {career['Branch']}")
                st.write(
                    f"**Interest Match:** {career['Interest Match']:.1f}%"
                )
                st.write(
                    f"**Academic Match:** {career['Academic Match']:.1f}%"
                )
                st.write(
                    f"**Capability Alignment:** "
                    f"{career['Capability Alignment']:.1f}%"
                )
                st.write(
                    "**Closest interest areas:** "
                    + career["Best Matching Interests"]
                )

        st.markdown("### How Your Match Score Works")
        st.write(
            "**Overall Match = 40% Interest Match + 30% Academic Match "
            "+ 30% Capability Alignment.**"
        )
        st.caption(
            "Work preferences and career goals guide your exploration, "
            "but do not change the numerical match score. These scores "
            "indicate compatibility with the dataset profiles; they do "
            "not predict career success."
        )

        st.markdown("### Keep Your Goals in Mind")
        for question, answer in goals.items():
            st.write(f"**{question}** {answer}")
        for question, answer in preferences.items():
            st.write(f"**{question}** {answer}")

    # INTERESTS TAB
    with tab_interest:

        st.markdown("### Your RIASEC Interest Profile")

        st.write(
            "RIASEC groups interests into six areas: Realistic, "
            "Investigative, Artistic, Social, Enterprising and Conventional."
        )

        st.plotly_chart(
            make_interest_chart(interest_scores, 420),
            use_container_width=True
        )

        st.markdown("### Individual Interest Scores")

        col1, col2 = st.columns(2)

        for i, (name, score) in enumerate(interest_scores.items()):
            if i % 2 == 0:
                with col1:
                    show_score_card(name, score)
            else:
                with col2:
                    show_score_card(name, score)

        st.markdown("### Your Leading Interest")
        st.markdown(f"## {top_interest}")
        st.write(
            f"This was the highest-scoring interest area in your "
            f"responses, at {interest_scores[top_interest]:.1f}%."
        )

    # ACADEMICS TAB
    with tab_academic:

        st.markdown("### Your Academic Snapshot")

        academic_chart_data = pd.DataFrame({
            "Subject": list(academic_scores.keys()),
            "Confidence": [
                score * 20 for score in academic_scores.values()
            ]
        })

        fig = px.bar(
            academic_chart_data,
            x="Subject",
            y="Confidence",
            text="Confidence"
        )

        fig.update_traces(
            width=0.5,
            texttemplate="%{text:.0f}%",
            textposition="outside",
            marker_color="#8D72E8"
        )

        fig.update_layout(
            height=400,
            yaxis_range=[0, 110],
            showlegend=False,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="white",
            xaxis_title="Subject",
            yaxis_title="Confidence (%)"
        )

        st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            show_summary_card("Strongest Subject", top_subject)

        with col2:
            show_summary_card(
                "Confidence Rating",
                f"{academic_scores[top_subject]}/5"
            )

        highest = max(academic_scores.values())
        lowest = min(academic_scores.values())

        strongest = [
            s for s, v in academic_scores.items() if v == highest
        ]

        improvement = [
            s for s, v in academic_scores.items() if v == lowest
        ]

        st.markdown("### Academic Insights")

        st.markdown("**Strongest subject area(s)**")
        st.write(", ".join(strongest))

        st.markdown("**Subject area(s) to improve**")
        st.write(", ".join(improvement))

        st.caption(
            "These are self-reported confidence ratings, not examination marks."
        )

    # SKILLS TAB
    with tab_skills:

        st.markdown("### Your Skills & Capabilities")

        col1, col2 = st.columns(2)

        for i, (skill, score) in enumerate(skill_scores.items()):
            if i % 2 == 0:
                with col1:
                    show_score_card(skill, score, 5)
            else:
                with col2:
                    show_score_card(skill, score, 5)

        st.markdown("### Your Learning Roadmap")

        for skill, score in sorted(
            skill_scores.items(),
            key=lambda x: x[1]
        ):

            st.markdown(f"**{skill} — {score}/5**")

            if score <= 2:
                st.write("Suggested first step: " + learning_roadmap[skill])
            elif score == 3:
                st.write("Suggested development: practise through small projects. " + learning_roadmap[skill])
            else:
                st.write("Suggested next step: apply this ability in more advanced projects. " + learning_roadmap[skill])

            st.divider()

        st.caption(
            "These capability ratings are self-reported and are not formal skill tests."
        )

    # WORK STYLE TAB
    with tab_work:

        st.markdown("### Your Preferred Working Style")

        preference_icons = ["👥", "🛠️", "🎨", "💻"]

        for i, (question, answer) in enumerate(preferences.items()):

            st.markdown(f"""
            <div class="summary-card">
                <div class="summary-title">{preference_icons[i]} {question}</div>
                <div class="summary-value">{answer}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("### What This Tells You")

        st.write(
            "Your preferences can help you compare different work "
            "environments and career paths. They are used to personalise "
            "exploration rather than calculate your numerical match score."
        )

    # CAREER GOALS TAB
    with tab_goals:

        st.markdown("### Your Future Priorities")

        goal_icons = ["💰", "🧭", "🎓", "⭐"]

        for i, (question, answer) in enumerate(goals.items()):

            st.markdown(f"""
            <div class="summary-card">
                <div class="summary-title">{goal_icons[i]} {question}</div>
                <div class="summary-value">{answer}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("### Reflect on Your Direction")

        st.write(
            "Your career goals help shape the type of opportunities "
            "you may want to explore, such as employment, further study "
            "or entrepreneurship."
        )

    # PDF REPORT TAB
    with tab_pdf:

        st.markdown("### Your Personal CareerCompass Report")

        st.markdown("""
        <div class="overview-banner">
            <h2 style="color:white;">Your results. One report.</h2>
            <p style="color:#d0d8f5;">
                A designed report containing your interest profile,
                academic confidence, skills, work preferences and career goals.
            </p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            show_summary_card("Sections Included", "6")

        with col2:
            show_summary_card("Interest Areas", "6")

        with col3:
            show_summary_card("Personal Report", "PDF")

        st.write("")
        st.markdown("**Your report includes:**")

        st.write("✓ Personal profile cover")
        st.write("✓ Top career recommendations and match breakdown")
        st.write("✓ RIASEC interest score bars")
        st.write("✓ Academic confidence profile")
        st.write("✓ Skills and learning recommendations")
        st.write("✓ Work preferences and career goals")
        st.write("✓ Guidance and assessment limitations")

        pdf_data = create_pdf()

        st.download_button(
            label="⬇ Download My CareerCompass Report",
            data=pdf_data,
            file_name=f"CareerCompass_{re.sub(r'[^A-Za-z0-9_-]+', '_', student_name).strip('_') or 'Student'}_Report.pdf",
            mime="application/pdf",
            use_container_width=True
        )

        st.caption(
            "Your PDF is generated from the responses saved in this assessment."
        )

    st.markdown("---")

    if st.button("Start Assessment Again", use_container_width=True):

        for key in [
            "interest_scores",
            "academic_scores",
            "skill_scores",
            "preferences",
            "goals",
            "student_name",
            "student_name_input"
        ]:
            if key in st.session_state:
                del st.session_state[key]

        st.session_state.page = "home"
        st.rerun()