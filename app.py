import streamlit as st
import re
import time
import streamlit.components.v1 as components
from crew.finance_crew import run_finsense

st.set_page_config(
    page_title="FinSense AI",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background-color: #080C14; color: #E8EAF0; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 860px; margin: auto; }

/* Tabs */
div[data-testid="stTabs"] button {
    background: transparent !important;
    color: #6B7A99 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    border: none !important;
    padding: 8px 16px !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: #E8EAF0 !important;
    border-bottom: 2px solid #4F46E5 !important;
}
div[data-testid="stTabContent"] {
    padding-top: 16px !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #4F46E5, #7C3AED);
    color: white !important; border: none; border-radius: 10px;
    font-family: 'DM Sans', sans-serif; font-weight: 500; font-size: 13px;
    padding: 10px 16px; transition: all 0.2s ease;
    box-shadow: 0 4px 15px rgba(79,70,229,0.3);
}
.stButton > button:hover { transform: translateY(-1px); box-shadow: 0 6px 20px rgba(79,70,229,0.5); }
.stButton > button[kind="primary"] { font-size: 16px; padding: 14px 28px; font-weight: 600; }

/* Textarea */
.stTextArea textarea {
    background: #0F1623 !important; border: 1px solid #1E2A3A !important;
    border-radius: 12px !important; color: #E8EAF0 !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 15px !important;
}
.stTextArea textarea:focus {
    border-color: #4F46E5 !important;
    box-shadow: 0 0 0 2px rgba(79,70,229,0.2) !important;
}

/* Metrics */
div[data-testid="metric-container"] {
    background: #0F1623; border-radius: 14px; padding: 16px; border: 1px solid #1E2A3A;
}
div[data-testid="metric-container"] label {
    color: #6B7A99 !important; font-size: 12px !important; font-weight: 600 !important;
    text-transform: uppercase !important; letter-spacing: 0.8px !important;
}
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
    color: #E8EAF0 !important; font-family: 'Syne', sans-serif !important;
    font-size: 28px !important; font-weight: 700 !important;
}

/* Expanders */
div[data-testid="stExpander"] {
    background: #0F1623 !important; border: 1px solid #1E2A3A !important;
    border-radius: 10px !important; margin-bottom: 8px !important;
}
div[data-testid="stExpander"] summary {
    color: #A0ABCB !important; font-weight: 600 !important; font-size: 13px !important;
    padding: 10px 14px !important;
}
div[data-testid="stExpander"] p { color: #C8D0E0 !important; font-size: 13px !important; line-height: 1.7 !important; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0A0F1A !important; border-right: 1px solid #1E2A3A !important;
    min-width: 240px !important;
}
section[data-testid="stSidebar"] * { color: #A0ABCB !important; }

hr { border-color: #1E2A3A !important; }
.stCaption { color: #3D4F6B !important; }
label[data-testid="stWidgetLabel"] { color: #6B7A99 !important; font-weight: 500 !important; }
</style>
""", unsafe_allow_html=True)


# ── HELPERS ───────────────────────────────────────────────────────────────────

def parse_number(text: str) -> int:
    """Handle all Indian number formats: 2k, 2.5k, 5L, 2 lakh, 50,000"""
    text = str(text).replace(',', '').strip().lower()
    # "2.5 lakh" or "2 lakhs"
    m = re.match(r'([\d.]+)\s*lakh', text)
    if m: return int(float(m.group(1)) * 100000)
    # "2.5L" or "5l"
    m = re.match(r'([\d.]+)l$', text)
    if m: return int(float(m.group(1)) * 100000)
    # "2.5 k" or "2.5k"
    m = re.match(r'([\d.]+)\s*k$', text)
    if m: return int(float(m.group(1)) * 1000)
    # "2 thousand"
    m = re.match(r'([\d.]+)\s*thousand', text)
    if m: return int(float(m.group(1)) * 1000)
    # crore
    m = re.match(r'([\d.]+)\s*cr', text)
    if m: return int(float(m.group(1)) * 10000000)
    try: return int(float(text))
    except: return 0


def parse_output(result: str) -> dict:
    data = {"verdict": "WAIT", "confidence": 70, "risk_score": 5,
            "why": "", "actions": [], "alternative": ""}
    m = re.search(r'VERDICT:\s*(GO|WAIT|AVOID)', result, re.IGNORECASE)
    if m: data["verdict"] = m.group(1).upper()
    m = re.search(r'CONFIDENCE:\s*(\d+)', result)
    if m: data["confidence"] = int(m.group(1))
    m = re.search(r'Risk Score[:\s]+(\d+)', result, re.IGNORECASE)
    if m: data["risk_score"] = int(m.group(1))
    m = re.search(r'WHY:(.*?)(?=ACTION|$)', result, re.DOTALL | re.IGNORECASE)
    if m: data["why"] = m.group(1).strip()
    actions = re.findall(r'\d\.\s(.+?)(?=\n\d\.|\n[A-Z]|$)', result)
    data["actions"] = [a.strip() for a in actions[:3]]
    m = re.search(r'ALTERNATIVE:(.*?)(?=DISCLAIMER|$)', result, re.DOTALL | re.IGNORECASE)
    if m: data["alternative"] = m.group(1).strip()
    return data


def clean_markdown(text: str) -> str:
    """Clean up raw LLM markdown for display"""
    # Convert ## headings to bold
    text = re.sub(r'##\s+(.+)', r'**\1**', text)
    text = re.sub(r'#\s+(.+)', r'**\1**', text)
    # Remove excessive blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def calculate_wealth_projection(user_input: str) -> dict:
    text = user_input.lower()

    # Income
    income = 0
    for p in [
        r'earn\s*[₹rs\.]*\s*([\d.,]+\s*(?:lakh|l|k|thousand)?)\s*(?:/month|per month|monthly|month|pm)',
        r'salary\s*(?:is|of)?\s*[₹rs\.]*\s*([\d.,]+\s*(?:lakh|l|k|thousand)?)',
        r'income\s*(?:is|of)?\s*[₹rs\.]*\s*([\d.,]+\s*(?:lakh|l|k|thousand)?)',
    ]:
        m = re.search(p, text)
        if m: income = parse_number(m.group(1).replace(',', '')); break

    # Loan
    loan_amt = 0
    for p in [
        r'(?:loan|borrow)\s*(?:of)?\s*[₹rs\.]*\s*([\d.,]+\s*(?:lakh|l|k|thousand)?)',
        r'[₹rs\.]*\s*([\d.,]+\s*(?:lakh|l|k|thousand)?)\s*(?:loan|personal loan)',
    ]:
        m = re.search(p, text)
        if m: loan_amt = parse_number(m.group(1).replace(',', '')); break

    # Rate
    rate = 0.12
    m = re.search(r'(\d+(?:\.\d+)?)\s*(?:%|percent)', text)
    if m: rate = float(m.group(1)) / 100

    # Tenure
    tenure = 2
    m = re.search(r'(\d+)\s*year', text)
    if m: tenure = int(m.group(1))

    # Investment amount
    invest_amt = 0
    for p in [
        r'contribute\s*[₹rs\.]*\s*([\d.,]+\s*(?:lakh|l|k|thousand)?)',
        r'invest\s*[₹rs\.]*\s*([\d.,]+\s*(?:lakh|l|k|thousand)?)',
        r'sip\s*(?:of)?\s*[₹rs\.]*\s*([\d.,]+\s*(?:lakh|l|k|thousand)?)',
        r'sav(?:e|ing|ings)?\s*[₹rs\.]*\s*([\d.,]+\s*(?:lakh|l|k|thousand)?)',
        r'put\s*[₹rs\.]*\s*([\d.,]+\s*(?:lakh|l|k|thousand)?)',
        r'([\d.,]+\s*(?:lakh|l|k|thousand)?)\s*(?:each|every|per)\s*month',
        r'([\d.,]+\s*(?:lakh|l|k|thousand)?)\s*(?:monthly|in sip|in mutual)',
    ]:
        m = re.search(p, text)
        if m:
            val = parse_number(m.group(1).replace(',', ''))
            if val > 0: invest_amt = val; break

    is_monthly = bool(re.search(r'/month|per month|monthly|sip|pm\b|each month|every month|contribute', text))

    monthly = 5000
    if invest_amt > 0: monthly = invest_amt
    elif income > 0: monthly = round(income * 0.20)

    # LOAN SCENARIO
    if loan_amt > 0:
        total_interest = loan_amt * rate * tenure
        emi = (loan_amt + total_interest) / (tenure * 12)
        return {
            "current_1yr": -round(total_interest / tenure),
            "current_5yr": -round(total_interest + emi * 12 * max(0, 5 - tenure)),
            "ai_1yr": round(emi * 12 * 1.12), "ai_5yr": round(emi * 12 * 5 * 1.28),
            "monthly": round(emi), "label_current": "Cost of Loan Plan (₹)",
            "label_ai": "Invest EMI Instead (₹)", "is_loan": True,
        }

    # SIP / MONTHLY INVESTMENT
    def sip(p, r, n): return round(p * (((1 + r) ** n - 1) / r) * (1 + r))
    if is_monthly and monthly > 0:
        return {
            "current_1yr": sip(monthly, 0.04/12, 12),
            "current_5yr": sip(monthly, 0.04/12, 60),
            "ai_1yr":      sip(monthly, 0.12/12, 12),
            "ai_5yr":      sip(monthly, 0.12/12, 60),
            "monthly": monthly,
            "label_current": "Conservative — FD 4% (₹)",
            "label_ai":      "AI Plan — Mutual Fund 12% (₹)",
            "is_loan": False,
        }

    # LUMP SUM
    lump = monthly if monthly > 0 else 50000
    return {
        "current_1yr": round(lump * 1.04), "current_5yr": round(lump * (1.04 ** 5)),
        "ai_1yr":      round(lump * 1.12), "ai_5yr":      round(lump * (1.12 ** 5)),
        "monthly": lump,
        "label_current": "Conservative — FD 4% (₹)",
        "label_ai":      "AI Plan — Mutual Fund 12% (₹)",
        "is_loan": False,
    }


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:8px 0 20px">
        <div style="font-family:'Syne',sans-serif;font-size:20px;font-weight:800;
                    color:#E8EAF0;margin-bottom:4px">💰 FinSense AI</div>
        <div style="font-size:12px;color:#3D4F6B">Multi-Agent Finance Advisor</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:11px;font-weight:700;color:#3D4F6B;
                text-transform:uppercase;letter-spacing:1px;margin-bottom:10px">
        Try an example
    </div>
    """, unsafe_allow_html=True)

    examples = [
        "I earn ₹50,000/month. Should I take a ₹3L loan at 14% for 2 years?",
        "Should I invest ₹10,000/month in mutual funds or FD?",
        "I spend ₹35,000/month on ₹50,000 salary. Am I overspending?",
        "Should I buy a ₹80,000 laptop or save the money?",
        "I earn ₹50k/month and want to contribute 2.5k each month to SIP. Good idea?",
    ]
    for i, ex in enumerate(examples):
        if st.button(ex, use_container_width=True, key=f"ex_{i}"):
            st.session_state["input"] = ex

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:11px;font-weight:700;color:#3D4F6B;
                text-transform:uppercase;letter-spacing:1px;margin-bottom:10px">
        How it works
    </div>
    <div style="font-size:12px;color:#3D4F6B;line-height:2">
        1. 📊 <b style="color:#6B7A99">Analyst</b> reads your numbers<br>
        2. ⚠️ <b style="color:#6B7A99">Risk Evaluator</b> scores risk<br>
        3. 💡 <b style="color:#6B7A99">Advisor</b> gives final call
    </div>
    <div style="margin-top:20px;font-size:11px;color:#2A3A52;line-height:1.8">
        Powered by AMD Developer Cloud<br>
        CrewAI · Qwen2.5-72B · ROCm
    </div>
    """, unsafe_allow_html=True)


# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:24px 0 20px">
    <div style="display:inline-block;background:linear-gradient(135deg,#4F46E5,#7C3AED);
                border-radius:18px;padding:12px 16px;margin-bottom:14px;
                box-shadow:0 8px 32px rgba(79,70,229,0.4)">
        <span style="font-size:26px">💰</span>
    </div>
    <h1 style="font-family:'Syne',sans-serif;font-size:2.4rem;font-weight:800;
               background:linear-gradient(135deg,#E8EAF0,#A0ABCB);
               -webkit-background-clip:text;-webkit-text-fill-color:transparent;
               margin:0 0 6px;letter-spacing:-1px">FinSense AI</h1>
    <p style="color:#6B7A99;font-size:14px;margin:0 0 10px">
        Describe your financial decision — 3 AI agents analyze it instantly
    </p>
    <div style="display:inline-flex;align-items:center;gap:8px;background:#0F1623;
                border:1px solid #1E2A3A;border-radius:999px;padding:5px 14px">
        <span style="width:6px;height:6px;background:#22C55E;border-radius:50%;
                     display:inline-block;box-shadow:0 0 8px #22C55E"></span>
        <span style="color:#6B7A99;font-size:11px;font-weight:500">
            AMD Developer Cloud · CrewAI · Qwen2.5-72B
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── AGENT CARDS ROW ───────────────────────────────────────────────────────────
st.markdown("""
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:20px">
    <div style="background:#0F1623;border:1px solid #1E2A3A;border-radius:12px;padding:12px;text-align:center">
        <div style="font-size:18px;margin-bottom:4px">📊</div>
        <div style="font-family:'Syne',sans-serif;font-size:12px;font-weight:700;color:#E8EAF0;margin-bottom:2px">Analyst</div>
        <div style="font-size:10px;color:#3D4F6B">Numbers & patterns</div>
    </div>
    <div style="background:#0F1623;border:1px solid #1E2A3A;border-radius:12px;padding:12px;text-align:center">
        <div style="font-size:18px;margin-bottom:4px">⚠️</div>
        <div style="font-family:'Syne',sans-serif;font-size:12px;font-weight:700;color:#E8EAF0;margin-bottom:2px">Risk Evaluator</div>
        <div style="font-size:10px;color:#3D4F6B">Risk scoring</div>
    </div>
    <div style="background:#0F1623;border:1px solid #1E2A3A;border-radius:12px;padding:12px;text-align:center">
        <div style="font-size:18px;margin-bottom:4px">💡</div>
        <div style="font-family:'Syne',sans-serif;font-size:12px;font-weight:700;color:#E8EAF0;margin-bottom:2px">Advisor</div>
        <div style="font-size:10px;color:#3D4F6B">Final recommendation</div>
    </div>
</div>
""", unsafe_allow_html=True)
# ── EXAMPLE PILLS ──
st.markdown("""
<div style="font-size:11px;font-weight:700;color:#3D4F6B;
            text-transform:uppercase;letter-spacing:1px;margin-bottom:10px">
    Quick examples — click to use
</div>
""", unsafe_allow_html=True)

examples_main = [
    "I earn ₹50,000/month. Should I take a ₹3L loan at 14% for 2 years?",
    "Should I invest ₹10,000/month in mutual funds or FD?",
    "I earn ₹50k/month and contribute ₹2.5k each month to SIP. Good idea?",
    "Should I buy a ₹80,000 laptop or save the money?",
]
cols = st.columns(2)
for i, ex in enumerate(examples_main):
    if cols[i % 2].button(ex, use_container_width=True, key=f"main_ex_{i}"):
        st.session_state["input"] = ex
        st.rerun()

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
# ── INPUT ─────────────────────────────────────────────────────────────────────
user_input = st.text_area(
    "Your financial decision:",
    value=st.session_state.get("input", ""),
    height=90,
    placeholder="e.g. I earn ₹50k/month and want to contribute ₹2.5k each month to SIP. Good idea?",
)

run = st.button("🔍 Analyze My Decision", type="primary", use_container_width=True)

# ── RUN ───────────────────────────────────────────────────────────────────────
if run:
    if not user_input.strip():
        st.warning("Please enter a financial decision to analyze.")
    else:
        # Sequential loading
        progress = st.empty()
        progress.markdown("""
        <div style="background:#0F1623;border:1px solid #1E2A3A;border-radius:12px;padding:16px 20px;margin-bottom:8px">
            <div style="display:flex;flex-direction:column;gap:10px">
                <div style="display:flex;align-items:center;gap:10px">
                    <span>📊</span>
                    <span style="color:#4F46E5;font-weight:600;font-size:13px">Analyst Agent</span>
                    <span style="color:#6B7A99;font-size:12px">— Reading your financial data...</span>
                    <span style="margin-left:auto;color:#F59E0B;font-size:11px">⏳ Processing</span>
                </div>
                <div style="display:flex;align-items:center;gap:10px">
                    <span>⚠️</span>
                    <span style="color:#F59E0B;font-weight:600;font-size:13px">Risk Evaluator</span>
                    <span style="color:#6B7A99;font-size:12px">— Running risk simulation...</span>
                    <span style="margin-left:auto;color:#F59E0B;font-size:11px">⏳ Processing</span>
                </div>
                <div style="display:flex;align-items:center;gap:10px">
                    <span>💡</span>
                    <span style="color:#22C55E;font-weight:600;font-size:13px">Advisor Agent</span>
                    <span style="color:#6B7A99;font-size:12px">— Generating recommendation...</span>
                    <span style="margin-left:auto;color:#F59E0B;font-size:11px">⏳ Processing</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Run agents
        result = run_finsense(user_input)

        # ✅ Update status to DONE
        progress.markdown("""
        <div style="background:#051A0F;border:1px solid #14532D;border-radius:12px;
                    padding:14px 20px;margin-bottom:8px">
            <div style="display:flex;flex-direction:column;gap:8px">
                <div style="display:flex;align-items:center;gap:8px">
                    <span style="color:#22C55E;font-weight:700;font-size:14px">✅ All 3 agents completed analysis</span>
                </div>
                <div style="display:flex;gap:24px;margin-top:2px">
                    <span style="font-size:12px;color:#166534">📊 Analyst ✓</span>
                    <span style="font-size:12px;color:#166534">⚠️ Risk Evaluator ✓</span>
                    <span style="font-size:12px;color:#166534">💡 Advisor ✓</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        parsed = parse_output(result["advisor_output"])
        wealth = calculate_wealth_projection(user_input)

        # ── TABS ──────────────────────────────────────────────────────────────
        tab1, tab2, tab3, tab4 = st.tabs([
            "📋  Verdict & Score",
            "🤖  Agent Reasoning",
            "📊  Wealth Projection",
            "🎯  Action Steps",
        ])

        # ── TAB 1: VERDICT ────────────────────────────────────────────────────
        with tab1:
            vc_map = {
                "GO":    {"icon":"✅","color":"#22C55E","bg":"#051A0F","border":"#14532D","label":"Go for it"},
                "WAIT":  {"icon":"⏳","color":"#F59E0B","bg":"#1A130A","border":"#78350F","label":"Wait & reconsider"},
                "AVOID": {"icon":"❌","color":"#EF4444","bg":"#1A0A0A","border":"#7F1D1D","label":"Avoid this decision"},
            }
            vc = vc_map.get(parsed["verdict"], vc_map["WAIT"])

            st.markdown(f"""
            <div style="background:{vc['bg']};border:1px solid {vc['border']};
                        border-radius:16px;padding:22px 26px;margin-bottom:16px">
                <div style="font-size:11px;font-weight:700;color:{vc['color']};
                            text-transform:uppercase;letter-spacing:1.5px;margin-bottom:10px">
                    Final Verdict
                </div>
                <div style="display:flex;align-items:center;gap:14px;margin-bottom:12px">
                    <span style="font-size:34px">{vc['icon']}</span>
                    <div>
                        <div style="font-family:'Syne',sans-serif;font-size:26px;
                                    font-weight:800;color:{vc['color']};line-height:1">
                            {parsed['verdict']}
                        </div>
                        <div style="font-size:13px;color:{vc['color']};opacity:0.8;margin-top:3px">
                            {vc['label']}
                        </div>
                    </div>
                </div>
                <div style="font-size:14px;line-height:1.8;color:#A0ABCB;
                            border-top:1px solid {vc['border']};padding-top:12px">
                    {parsed['why'] or 'Based on comprehensive multi-agent financial analysis.'}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Metrics
            conf = parsed["confidence"]
            rs   = parsed["risk_score"]
            cc   = "#22C55E" if conf >= 70 else "#F59E0B" if conf >= 40 else "#EF4444"
            rc   = "#22C55E" if rs <= 3 else "#F59E0B" if rs <= 6 else "#EF4444"
            rl   = "Low Risk" if rs <= 3 else "Medium Risk" if rs <= 6 else "High Risk"

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Confidence Score", f"{conf}%")
                st.markdown(f"""
                <div style="background:#1E2A3A;border-radius:999px;height:6px;
                            overflow:hidden;margin-top:-12px;margin-bottom:8px">
                    <div style="background:{cc};width:{conf}%;height:100%;
                                border-radius:999px;box-shadow:0 0 8px {cc}66"></div>
                </div>""", unsafe_allow_html=True)
            with col2:
                st.metric("Risk Score", f"{rs}/10", delta=rl, delta_color="off")
                st.markdown(f"""
                <div style="background:#1E2A3A;border-radius:999px;height:6px;
                            overflow:hidden;margin-top:-12px;margin-bottom:8px">
                    <div style="background:{rc};width:{rs*10}%;height:100%;
                                border-radius:999px;box-shadow:0 0 8px {rc}66"></div>
                </div>""", unsafe_allow_html=True)

            # Alternative
            if parsed["alternative"]:
                st.markdown(f"""
                <div style="background:#0A1020;border:1px solid #1E3055;
                            border-radius:14px;padding:16px 20px;margin-top:12px">
                    <div style="font-size:11px;font-weight:700;color:#4F46E5;
                                text-transform:uppercase;letter-spacing:1px;margin-bottom:6px">
                        💡 Alternative Scenario
                    </div>
                    <div style="font-size:14px;line-height:1.7;color:#A0ABCB">
                        {parsed['alternative']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # ── TAB 2: AGENT REASONING ────────────────────────────────────────────
        with tab2:
            st.markdown("""
            <div style="font-size:13px;color:#3D4F6B;margin-bottom:12px">
                Click each card to see the agent's full reasoning
            </div>
            """, unsafe_allow_html=True)

            for icon, title, subtitle, content, color in [
                ("📊", "Analyst Agent",    "Financial Analysis",    result["analyst_output"], "#4F46E5"),
                ("⚠️", "Risk Evaluator",   "Risk Assessment",       result["risk_output"],    "#F59E0B"),
                ("💡", "Advisor Agent",    "Final Recommendation",  result["advisor_output"], "#22C55E"),
            ]:
                cleaned = clean_markdown(content or "Analysis complete.")
                with st.expander(f"{icon} {title} — {subtitle}", expanded=False):
                    st.markdown(cleaned)

            with st.expander("🔍 Raw Full Output", expanded=False):
                st.markdown(f"""
                <div style="background:#080C14;border-radius:8px;padding:16px;
                            font-size:12px;line-height:1.8;color:#6B7A99;
                            white-space:pre-wrap;word-wrap:break-word;
                            overflow-wrap:break-word;font-family:monospace;
                            max-width:100%;overflow-x:hidden">
    {result["raw"]}
                </div>
                """, unsafe_allow_html=True)

        # ── TAB 3: WEALTH CHART ───────────────────────────────────────────────
        with tab3:
            c1 = wealth["current_1yr"]; c5 = wealth["current_5yr"]
            a1 = wealth["ai_1yr"];      a5 = wealth["ai_5yr"]
            lc = wealth["label_current"]; la = wealth["label_ai"]
            bc = "rgba(239,68,68,0.3)" if wealth["is_loan"] else "rgba(107,122,153,0.3)"
            ec = "#EF4444" if wealth["is_loan"] else "#6B7A99"
            mn = f"₹{wealth['monthly']:,}/month" if wealth['monthly'] else ""

            st.markdown(f"""
            <div style="margin-bottom:16px">
                <div style="font-family:'Syne',sans-serif;font-size:16px;font-weight:700;
                            color:#E8EAF0;margin-bottom:4px">📊 Wealth Projection</div>
                <div style="font-size:13px;color:#6B7A99">
                    {lc} vs {la}
                    {"&nbsp;·&nbsp; SIP amount: <b style='color:#A0ABCB'>" + mn + "</b>" if mn else ""}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Explanation cards
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"""
                <div style="background:#0F1623;border:1px solid #1E2A3A;border-radius:12px;padding:14px;margin-bottom:12px">
                    <div style="font-size:11px;color:#6B7A99;font-weight:600;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:6px">
                        Conservative Plan
                    </div>
                    <div style="font-size:13px;color:#A0ABCB;line-height:1.6">
                        {'Interest cost of taking loan' if wealth['is_loan'] else 'Fixed Deposit / Savings at 4% annual return'}
                    </div>
                    <div style="margin-top:10px;display:flex;gap:16px">
                        <div>
                            <div style="font-size:10px;color:#3D4F6B">1 Year</div>
                            <div style="font-size:15px;font-weight:700;color:#6B7A99">
                                {'−' if c1 < 0 else ''}₹{abs(c1):,}
                            </div>
                        </div>
                        <div>
                            <div style="font-size:10px;color:#3D4F6B">5 Years</div>
                            <div style="font-size:15px;font-weight:700;color:#6B7A99">
                                {'−' if c5 < 0 else ''}₹{abs(c5):,}
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col_b:
                st.markdown(f"""
                <div style="background:#051A0F;border:1px solid #14532D;border-radius:12px;padding:14px;margin-bottom:12px">
                    <div style="font-size:11px;color:#22C55E;font-weight:600;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:6px">
                        AI Recommended Plan
                    </div>
                    <div style="font-size:13px;color:#A0ABCB;line-height:1.6">
                        {'Invest EMI in Mutual Fund SIP at 12% return' if wealth['is_loan'] else 'Equity Mutual Fund SIP at 12% annual return'}
                    </div>
                    <div style="margin-top:10px;display:flex;gap:16px">
                        <div>
                            <div style="font-size:10px;color:#3D4F6B">1 Year</div>
                            <div style="font-size:15px;font-weight:700;color:#22C55E">₹{a1:,}</div>
                        </div>
                        <div>
                            <div style="font-size:10px;color:#3D4F6B">5 Years</div>
                            <div style="font-size:15px;font-weight:700;color:#22C55E">₹{a5:,}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            components.html(f"""
            <div style="background:#0F1623;border:1px solid #1E2A3A;border-radius:16px;padding:20px">
                <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
                <canvas id="wc" height="140"></canvas>
                <script>
                new Chart(document.getElementById('wc'),{{
                    type:'bar',
                    data:{{
                        labels:['1 Year','5 Years'],
                        datasets:[
                            {{label:'{lc}',data:[{c1},{c5}],backgroundColor:'{bc}',
                              borderColor:'{ec}',borderWidth:2,borderRadius:8}},
                            {{label:'{la}',data:[{a1},{a5}],
                              backgroundColor:'rgba(34,197,94,0.25)',
                              borderColor:'#22C55E',borderWidth:2,borderRadius:8}}
                        ]
                    }},
                    options:{{
                        responsive:true,
                        plugins:{{
                            legend:{{position:'top',labels:{{color:'#A0ABCB',
                                font:{{size:12,family:'DM Sans'}},padding:16,usePointStyle:true}}}},
                            tooltip:{{backgroundColor:'#0F1623',borderColor:'#1E2A3A',
                                borderWidth:1,titleColor:'#E8EAF0',bodyColor:'#A0ABCB',padding:12,
                                callbacks:{{label:function(ctx){{
                                    let v=ctx.raw,p=v<0?'-₹':'₹';
                                    return ' '+ctx.dataset.label+': '+p+Math.abs(v).toLocaleString('en-IN');
                                }}}}
                            }}
                        }},
                        scales:{{
                            x:{{grid:{{color:'#1E2A3A'}},ticks:{{color:'#6B7A99',font:{{family:'DM Sans'}}}}}},
                            y:{{beginAtZero:false,grid:{{color:'#1E2A3A'}},
                                ticks:{{color:'#6B7A99',font:{{family:'DM Sans'}},
                                    callback:function(v){{
                                        let p=v<0?'-₹':'₹';
                                        return p+Math.abs(v).toLocaleString('en-IN');
                                    }}
                                }}
                            }}
                        }}
                    }}
                }});
                </script>
            </div>""", height=320)

            st.markdown("""
            <div style="font-size:12px;color:#2A3A52;margin-top:12px;line-height:1.7">
                📌 <b style="color:#3D4F6B">How this is calculated:</b>
                Conservative plan uses 4% FD return.
                AI plan uses 12% mutual fund SIP compounding formula.
                Loan scenarios show interest cost vs investing the EMI amount.
            </div>
            """, unsafe_allow_html=True)

        # ── TAB 4: ACTION STEPS ───────────────────────────────────────────────
        with tab4:
            if parsed["actions"]:
                accents = ["#4F46E5", "#7C3AED", "#2563EB"]
                for i, action in enumerate(parsed["actions"], 1):
                    c = accents[(i-1) % len(accents)]
                    st.markdown(f"""
                    <div style="display:flex;align-items:flex-start;gap:14px;
                                padding:14px 16px;margin-bottom:10px;background:#0F1623;
                                border-radius:12px;border:1px solid #1E2A3A;border-left:3px solid {c}">
                        <span style="background:{c};color:white;border-radius:8px;
                                     width:28px;height:28px;display:flex;align-items:center;
                                     justify-content:center;font-size:13px;font-weight:700;
                                     flex-shrink:0">{i}</span>
                        <span style="font-size:14px;line-height:1.7;color:#C8D0E0;padding-top:4px">
                            {action}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="color:#6B7A99;font-size:14px;padding:20px;text-align:center">
                    Action steps will appear here after analysis.
                </div>
                """, unsafe_allow_html=True)

            st.markdown("""
            <div style="text-align:center;font-size:12px;color:#2A3A52;padding:16px;
                        border-top:1px solid #1E2A3A;margin-top:16px">
                ⚠️ AI-generated analysis for informational purposes only.<br>
                Consult a certified financial advisor before making major decisions.
            </div>
            """, unsafe_allow_html=True)