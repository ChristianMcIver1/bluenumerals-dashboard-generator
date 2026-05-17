import re
import random
from html import escape
from urllib.parse import urlparse

import requests
import pandas as pd
import plotly.express as px
import streamlit as st
from bs4 import BeautifulSoup

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="BlueNumerals Dashboard Generator",
    page_icon=":bar_chart:",
    layout="wide"
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;600;700&display=swap');

    :root {
        --bn-accent: #4A86E8;
        --bn-text: #1c1919;
        --bn-muted: #6f686a;
        --bn-border: #e7e3e4;
        --bn-bg: #fafafa;
        --bn-card: #ffffff;
    }

    html, body, [class*="css"] {
        font-family: "Open Sans", sans-serif;
    }

    html,
    body,
    .stApp {
        background: var(--bn-bg);
        color: var(--bn-text);
    }

    .block-container {
        max-width: 1180px;
        padding-top: 3rem;
        padding-bottom: 4rem;
    }

    h1 {
        font-size: 3rem !important;
        line-height: 1.08 !important;
        font-weight: 600 !important;
        letter-spacing: 0 !important;
        margin-bottom: .4rem !important;
    }

    h2 {
        font-size: 2rem !important;
        font-weight: 300 !important;
        letter-spacing: 0 !important;
        margin-top: 2.2rem !important;
    }

    h3 {
        font-size: 1rem !important;
        font-weight: 600 !important;
        letter-spacing: 0 !important;
    }

    p, label, span, div {
        letter-spacing: 0 !important;
    }

    [data-testid="stMetric"] {
        background: var(--bn-card);
        border: 1px solid var(--bn-border);
        border-radius: 8px;
        padding: 1rem 1rem .9rem;
        color: var(--bn-text);
    }

    [data-testid="stMetricLabel"] {
        color: var(--bn-muted) !important;
    }

    [data-testid="stMetricValue"] {
        color: var(--bn-text) !important;
        font-weight: 600;
    }

    [data-testid="stMetricDelta"] {
        color: #137333 !important;
    }

    [data-testid="stTextInput"] label,
    [data-testid="stTextInput"] p,
    [data-testid="stTextInput"] span {
        color: var(--bn-text) !important;
    }

    [data-testid="stTextInput"] div[data-baseweb="input"] {
        background: #ffffff !important;
        border-color: var(--bn-border) !important;
        border-radius: 8px;
    }

    [data-testid="stTextInput"] input {
        background: #ffffff !important;
        border-color: var(--bn-border);
        border-radius: 8px;
        color: var(--bn-text) !important;
    }

    [data-testid="stTextInput"] input::placeholder {
        color: #8b8587 !important;
        opacity: 1 !important;
    }

    [data-testid="stTextInput"] div:focus-within,
    [data-testid="stTextInput"] div[data-baseweb="input"]:focus-within {
        border-color: var(--bn-accent) !important;
        box-shadow: 0 0 0 1px var(--bn-accent) !important;
    }

    [data-testid="stTextInput"] input:focus {
        border-color: var(--bn-accent) !important;
        box-shadow: none !important;
        outline: none !important;
    }

    [data-testid="stTextInput"] input:focus-visible {
        outline: none !important;
    }

    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        min-height: 2.75rem;
    }

    .stButton > button[kind="primary"] {
        background: var(--bn-accent);
        border-color: var(--bn-accent);
        color: #ffffff;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: var(--bn-border);
        border-radius: 8px;
        background: var(--bn-card);
        color: var(--bn-text);
    }

    [data-testid="stMarkdownContainer"],
    [data-testid="stCaptionContainer"] {
        color: var(--bn-text);
    }

    .bn-subtitle {
        color: var(--bn-muted);
        font-size: 1.05rem;
        max-width: 760px;
        margin-bottom: 1.5rem;
    }

    .bn-pill-row {
        display: flex;
        gap: .5rem;
        flex-wrap: wrap;
        margin: .2rem 0 .8rem;
    }

    .bn-pill {
        background: #eef4ff;
        border: 1px solid #c9dcff;
        border-radius: 999px;
        color: #1f4f9f;
        display: inline-flex;
        font-size: .86rem;
        font-weight: 600;
        padding: .3rem .7rem;
    }

    .bn-muted {
        color: var(--bn-muted);
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("BlueNumerals Dashboard Generator")

st.markdown(
    """
    <p class="bn-subtitle">
    Generate a personalized business dashboard demo from a public website.
    </p>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------
# BUSINESS TYPE DATABASE
# ---------------------------------------------------

BUSINESS_TYPES = {

    "Agriculture / Farm": {

        "keywords": [
            "farm",
            "farms",
            "orchard",
            "produce",
            "berries",
            "blueberries",
            "u-pick",
            "pick your own",
            "harvest",
            "agriculture",
            "crop",
            "livestock",
            "farm market",
            "seasonal",
            "greenhouse"
        ],

        "customer_label": "Visitors",
        "revenue_label": "Farm Revenue",
        "appointment_label": "Visits",
        "service_label": "Products",

        "kpis": [
            "Weekly Visitors",
            "Revenue by Product",
            "Seasonal Sales",
            "Repeat Visitors"
        ]
    },

    "HVAC": {

        "keywords": [
            "hvac",
            "heating",
            "cooling",
            "air conditioning",
            "furnace",
            "boiler",
            "duct",
            "ventilation"
        ],

        "customer_label": "Customers",
        "revenue_label": "Service Revenue",
        "appointment_label": "Service Calls",
        "service_label": "Services",

        "kpis": [
            "Booked Service Calls",
            "Lead Conversion Rate",
            "Average Ticket Value",
            "Technician Utilization"
        ]
    },

    "Landscaping": {

        "keywords": [
            "landscaping",
            "lawn",
            "mulch",
            "hardscape",
            "snow removal",
            "yard",
            "landscape design",
            "grass",
            "property maintenance"
        ],

        "customer_label": "Clients",
        "revenue_label": "Project Revenue",
        "appointment_label": "Projects",
        "service_label": "Services",

        "kpis": [
            "Projects Completed",
            "Monthly Maintenance Revenue",
            "Quote Conversion Rate",
            "Seasonal Revenue"
        ]
    },

    "Restaurant / Cafe": {

        "keywords": [
            "restaurant",
            "cafe",
            "coffee",
            "menu",
            "dining",
            "food",
            "bar",
            "kitchen",
            "brunch",
            "lunch",
            "dinner"
        ],

        "customer_label": "Guests",
        "revenue_label": "Sales Revenue",
        "appointment_label": "Reservations",
        "service_label": "Menu Items",

        "kpis": [
            "Daily Guests",
            "Average Ticket Size",
            "Top Selling Items",
            "Weekly Revenue"
        ]
    },

    "Dental / Healthcare": {

        "keywords": [
            "dentist",
            "dental",
            "orthodontics",
            "patient",
            "clinic",
            "teeth",
            "oral",
            "healthcare"
        ],

        "customer_label": "Patients",
        "revenue_label": "Practice Revenue",
        "appointment_label": "Appointments",
        "service_label": "Treatments",

        "kpis": [
            "New Patients",
            "Appointment Completion Rate",
            "Treatment Revenue",
            "Patient Retention"
        ]
    },

    "Fitness / Gym": {

        "keywords": [
            "gym",
            "fitness",
            "workout",
            "crossfit",
            "training",
            "membership",
            "exercise",
            "personal trainer",
            "strength"
        ],

        "customer_label": "Members",
        "revenue_label": "Membership Revenue",
        "appointment_label": "Sessions",
        "service_label": "Programs",

        "kpis": [
            "Membership Growth",
            "Class Attendance",
            "Retention Rate",
            "Personal Training Revenue"
        ]
    },

    "Tutoring / Education": {

        "keywords": [
            "tutoring",
            "education",
            "students",
            "sat",
            "act",
            "college counseling",
            "learning",
            "academic",
            "test prep",
            "curriculum"
        ],

        "customer_label": "Students",
        "revenue_label": "Program Revenue",
        "appointment_label": "Sessions",
        "service_label": "Programs",

        "kpis": [
            "Student Enrollment",
            "Average Score Improvement",
            "Session Attendance",
            "Retention Rate"
        ]
    },

    "Contractor / Construction": {

        "keywords": [
            "contractor",
            "construction",
            "roofing",
            "remodel",
            "renovation",
            "builder",
            "concrete",
            "framing",
            "home improvement"
        ],

        "customer_label": "Clients",
        "revenue_label": "Project Revenue",
        "appointment_label": "Projects",
        "service_label": "Services",

        "kpis": [
            "Open Projects",
            "Quote Acceptance Rate",
            "Revenue Per Project",
            "Project Completion Time"
        ]
    },

    "Cleaning Services": {

        "keywords": [
            "cleaning",
            "maid",
            "housekeeping",
            "janitorial",
            "deep clean",
            "commercial cleaning"
        ],

        "customer_label": "Clients",
        "revenue_label": "Cleaning Revenue",
        "appointment_label": "Bookings",
        "service_label": "Cleaning Services",

        "kpis": [
            "Recurring Clients",
            "Monthly Bookings",
            "Revenue Per Cleaning",
            "Customer Retention"
        ]
    },

    "Professional Services": {

        "keywords": [
            "accounting",
            "law firm",
            "consulting",
            "insurance",
            "financial",
            "tax",
            "marketing agency",
            "advisor"
        ],

        "customer_label": "Clients",
        "revenue_label": "Firm Revenue",
        "appointment_label": "Consultations",
        "service_label": "Services",

        "kpis": [
            "Client Retention",
            "Consultations Booked",
            "Monthly Revenue",
            "Lead Conversion Rate"
        ]
    }
}

# ---------------------------------------------------
# URL NORMALIZATION
# ---------------------------------------------------

def normalize_url(url):

    url = url.strip()

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    return url

# ---------------------------------------------------
# WEBSITE SCRAPER
# ---------------------------------------------------

@st.cache_data(show_spinner=False)
def scrape_business_info(url):

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=10
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    title = (
        soup.title.string.strip()
        if soup.title and soup.title.string
        else "Unknown Business"
    )

    meta_description = soup.find(
        "meta",
        attrs={"name": "description"}
    )

    description = (
        meta_description["content"].strip()
        if meta_description and meta_description.get("content")
        else ""
    )

    headings = [
        h.get_text(" ", strip=True)
        for h in soup.find_all(["h1", "h2", "h3"])
    ]

    paragraphs = [
        p.get_text(" ", strip=True)
        for p in soup.find_all("p")[:30]
    ]

    buttons = [
        b.get_text(" ", strip=True)
        for b in soup.find_all(["button", "a"])[:50]
    ]

    page_text = " ".join(
        [title, description]
        + headings
        + paragraphs
        + buttons
    )

    page_text = re.sub(
        r"\s+",
        " ",
        page_text
    )

    domain = (
        urlparse(url)
        .netloc
        .replace("www.", "")
    )

    return {
        "url": url,
        "domain": domain,
        "title": title,
        "description": description,
        "headings": headings[:15],
        "text": page_text[:10000]
    }

# ---------------------------------------------------
# BUSINESS CLASSIFIER
# ---------------------------------------------------

def classify_business(text):

    text = text.lower()

    scores = {}

    for industry, data in BUSINESS_TYPES.items():

        score = 0

        for keyword in data["keywords"]:

            occurrences = text.count(
                keyword.lower()
            )

            score += occurrences

        scores[industry] = score

    best_match = max(
        scores,
        key=scores.get
    )

    return best_match, scores

# ---------------------------------------------------
# SERVICE EXTRACTION
# ---------------------------------------------------

def extract_services(info):

    services = []

    for heading in info["headings"]:

        heading = heading.strip()

        if (
            len(heading) > 4
            and len(heading) < 80
        ):
            services.append(heading)

    services = list(
        dict.fromkeys(services)
    )

    return services[:6]

# ---------------------------------------------------
# MOCK DATA
# ---------------------------------------------------

def generate_mock_data(rng):

    months = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun"
    ]

    leads = [
        rng.randint(25, 90)
        for _ in months
    ]

    conversions = [
        int(x * rng.uniform(0.22, 0.48))
        for x in leads
    ]

    revenue = [
        c * rng.randint(250, 1200)
        for c in conversions
    ]

    return pd.DataFrame({
        "Month": months,
        "Leads": leads,
        "Conversions": conversions,
        "Revenue": revenue
    })


def generate_kpi_metrics(rng):

    return {
        "customers": {
            "value": f"{rng.randint(85, 380):,}",
            "delta": f"+{rng.randint(4, 24)}%"
        },
        "appointments": {
            "value": f"{rng.randint(18, 140):,}",
            "delta": f"+{rng.randint(3, 18)}%"
        },
        "revenue": {
            "value": f"${rng.randint(9000, 78000):,}",
            "delta": f"+{rng.randint(4, 22)}%"
        }
    }


def generate_activity_mix(rng):

    activities = [
        "Sales",
        "Marketing",
        "Operations",
        "Customer Support",
        "Administration",
        "Fulfillment"
    ]

    return pd.DataFrame({
        "Category": activities,
        "Count": [
            rng.randint(8, 34)
            for _ in activities
        ]
    })

# ---------------------------------------------------
# PRESENTATION HELPERS
# ---------------------------------------------------

CHART_HEIGHT = 320


def render_pills(items):

    if not items:
        st.caption("No website headings were detected for this section.")
        return

    pill_html = "".join(
        f'<span class="bn-pill">{escape(item)}</span>'
        for item in items
    )

    st.markdown(
        f'<div class="bn-pill-row">{pill_html}</div>',
        unsafe_allow_html=True
    )


def style_plotly_chart(fig):

    chart_text = "#1c1919"

    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={
            "family": "Open Sans, sans-serif",
            "color": chart_text
        },
        margin={
            "l": 12,
            "r": 12,
            "t": 12,
            "b": 12
        },
        height=CHART_HEIGHT,
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": -0.28,
            "xanchor": "left",
            "x": 0,
            "font": {
                "color": chart_text
            }
        },
        hoverlabel={
            "bgcolor": "#ffffff",
            "bordercolor": "#e7e3e4",
            "font": {
                "color": chart_text
            }
        },
        hovermode="x unified"
    )

    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        title=None,
        tickfont={
            "color": chart_text
        },
        linecolor="#d8d2d4"
    )

    fig.update_yaxes(
        gridcolor="#f0ecee",
        zeroline=False,
        tickfont={
            "color": chart_text
        },
        titlefont={
            "color": chart_text
        },
        linecolor="#d8d2d4"
    )

    fig.update_traces(
        textfont={
            "color": chart_text
        }
    )

    return fig

# ---------------------------------------------------
# DASHBOARD
# ---------------------------------------------------

def generate_dashboard(info, profile):

    rng = random.Random()

    language = profile[
        "dashboard_language"
    ]

    customer_label = language[
        "customer_label"
    ]

    revenue_label = language[
        "revenue_label"
    ]

    appointment_label = language[
        "appointment_label"
    ]

    st.markdown(
        f"## Dashboard Demo - {info['title']}"
    )

    st.caption(
        f"Generated from public website information at {info['domain']}."
    )

    # KPI ROW

    kpis = generate_kpi_metrics(
        rng
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            customer_label,
            kpis["customers"]["value"],
            kpis["customers"]["delta"]
        )

    with col2:
        st.metric(
            appointment_label,
            kpis["appointments"]["value"],
            kpis["appointments"]["delta"]
        )

    with col3:
        st.metric(
            revenue_label,
            kpis["revenue"]["value"],
            kpis["revenue"]["delta"]
        )

    # CHARTS

    df = generate_mock_data(
        rng
    )

    activity_mix = generate_activity_mix(
        rng
    )

    chart_left, chart_right = st.columns(2, gap="medium")

    with chart_left.container(
        border=True
    ):

        st.markdown("### Lead & Conversion Trend")

        fig = px.line(
            df,
            x="Month",
            y=["Leads", "Conversions"],
            markers=True,
            color_discrete_sequence=[
                "#4A86E8",
                "#3399ff"
            ]
        )

        fig.update_traces(
            line={
                "width": 3
            },
            marker={
                "size": 7
            }
        )

        st.plotly_chart(
            style_plotly_chart(fig),
            use_container_width=True
        )

    with chart_right.container(
        border=True
    ):

        st.markdown(
            f"### Monthly {revenue_label}"
        )

        fig2 = px.bar(
            df,
            x="Month",
            y="Revenue",
            color_discrete_sequence=[
                "#4A86E8"
            ]
        )

        fig2.update_traces(
            marker_line_width=0,
            opacity=.92
        )

        st.plotly_chart(
            style_plotly_chart(fig2),
            use_container_width=True
        )

    chart_bottom_left, chart_bottom_right = st.columns(2, gap="medium")

    with chart_bottom_left.container(
        border=True
    ):

        st.markdown("### Activity Mix")

        fig3 = px.pie(
            activity_mix,
            names="Category",
            values="Count",
            hole=.42,
            color_discrete_sequence=[
                "#4A86E8",
                "#3399ff",
                "#ffb84d",
                "#ff6b7a",
                "#8a7cff",
                "#3fc5b7"
            ]
        )

        fig3.update_traces(
            textposition="inside",
            textinfo="percent"
        )

        st.plotly_chart(
            style_plotly_chart(fig3),
            use_container_width=True
        )

    with chart_bottom_right.container(
        border=True
    ):

        st.markdown("### Revenue Per Conversion")

        df["Revenue Per Conversion"] = (
            df["Revenue"] / df["Conversions"]
        ).round(0)

        fig4 = px.area(
            df,
            x="Month",
            y="Revenue Per Conversion",
            color_discrete_sequence=[
                "#3399ff"
            ]
        )

        fig4.update_traces(
            line={
                "width": 3
            },
            fillcolor="rgba(51, 153, 255, .22)"
        )

        st.plotly_chart(
            style_plotly_chart(fig4),
            use_container_width=True
        )

    # RECOMMENDATION

    with st.container(
        border=True
    ):

        st.markdown(
            "### BlueNumerals Recommendations"
        )

        st.markdown(
            """
            This business could benefit from a centralized dashboard for
            tracking operations, revenue, leads, and follow-ups using tools
            already in use like Google Sheets or Excel.
            """
        )

# ---------------------------------------------------
# MAIN APP
# ---------------------------------------------------

with st.container(
    border=True
):

    st.markdown("### Website Analysis")

    input_col, action_col = st.columns([4, 1], gap="medium")

    with input_col:

        url = st.text_input(
            "Enter Business URL",
            placeholder="https://examplebusiness.com",
            label_visibility="collapsed"
        )

    with action_col:

        generate_clicked = st.button(
            "Generate",
            type="primary",
            use_container_width=True
        )

if generate_clicked:

    if not url:

        st.warning(
            "Please enter a business URL."
        )

    else:

        try:

            clean_url = normalize_url(
                url
            )

            with st.spinner(
                "Analyzing website..."
            ):

                info = scrape_business_info(
                    clean_url
                )

                industry, scores = classify_business(
                    info["text"]
                )

                industry_data = BUSINESS_TYPES[
                    industry
                ]

                services = extract_services(
                    info
                )

                profile = {

                    "business_type": industry,

                    "industry": industry,

                    "customer_type": industry_data[
                        "customer_label"
                    ],

                    "services": services,

                    "recommended_kpis": industry_data[
                        "kpis"
                    ],

                    "dashboard_language": {

                        "customer_label": industry_data[
                            "customer_label"
                        ],

                        "revenue_label": industry_data[
                            "revenue_label"
                        ],

                        "appointment_label": industry_data[
                            "appointment_label"
                        ],

                        "service_label": industry_data[
                            "service_label"
                        ]
                    }
                }

            generate_dashboard(
                info,
                profile
            )

        except Exception as e:

            st.error(
                f"Error generating dashboard: {e}"
            )
