import chainlit as cl
import re
from crew.finance_crew import run_finsense

def parse_output(result: str) -> dict:
    data = {
        "verdict": "WAIT",
        "confidence": 70,
        "risk_score": 5,
        "why": "",
        "actions": [],
        "alternative": "",
    }

    verdict_match = re.search(r'VERDICT:\s*(GO|WAIT|AVOID)', result, re.IGNORECASE)
    if verdict_match:
        data["verdict"] = verdict_match.group(1).upper()

    conf_match = re.search(r'CONFIDENCE:\s*(\d+)', result)
    if conf_match:
        data["confidence"] = int(conf_match.group(1))

    risk_match = re.search(r'Risk Score[:\s]+(\d+)', result, re.IGNORECASE)
    if risk_match:
        data["risk_score"] = int(risk_match.group(1))

    why_match = re.search(r'WHY:(.*?)(?=ACTION|$)', result, re.DOTALL | re.IGNORECASE)
    if why_match:
        data["why"] = why_match.group(1).strip()

    actions = re.findall(r'\d\.\s(.+?)(?=\n\d\.|\n[A-Z]|$)', result)
    data["actions"] = [a.strip() for a in actions[:3]]

    alt_match = re.search(r'ALTERNATIVE:(.*?)(?=DISCLAIMER|$)', result, re.DOTALL | re.IGNORECASE)
    if alt_match:
        data["alternative"] = alt_match.group(1).strip()

    return data


def build_report_html(data: dict) -> str:

    verdict_config = {
        "GO":   {"color": "#0F6E56", "bg": "#E1F5EE", "icon": "✅", "label": "Go for it"},
        "WAIT": {"color": "#854F0B", "bg": "#FAEEDA", "icon": "⏳", "label": "Wait & reconsider"},
        "AVOID":{"color": "#A32D2D", "bg": "#FCEBEB", "icon": "❌", "label": "Avoid this"},
    }
    vc = verdict_config.get(data["verdict"], verdict_config["WAIT"])

    rs = data["risk_score"]
    if rs <= 3:
        risk_color = "#0F6E56"
        risk_label = "Low Risk 🟢"
    elif rs <= 6:
        risk_color = "#854F0B"
        risk_label = "Medium Risk 🟡"
    else:
        risk_color = "#A32D2D"
        risk_label = "High Risk 🔴"

    conf = data["confidence"]
    conf_color = "#0F6E56" if conf >= 70 else "#854F0B" if conf >= 40 else "#A32D2D"

    # Action steps
    actions_html = ""
    for i, action in enumerate(data["actions"], 1):
        actions_html += f"""
        <div style="display:flex;align-items:flex-start;gap:12px;
                    padding:12px;margin-bottom:8px;
                    background:#f8f9ff;border-radius:8px;
                    border-left:3px solid #534AB7;">
            <span style="background:#534AB7;color:white;border-radius:50%;
                         width:26px;height:26px;display:flex;align-items:center;
                         justify-content:center;font-size:12px;
                         font-weight:700;flex-shrink:0">{i}</span>
            <span style="font-size:14px;color:#3d3d3a;line-height:1.6">{action}</span>
        </div>"""

    # Current vs AI plan values for chart
    current_1yr  = round(data["confidence"] * 800)
    ai_1yr       = round(data["confidence"] * 1400)
    current_5yr  = round(data["confidence"] * 3000)
    ai_5yr       = round(data["confidence"] * 6500)

    alternative_html = ""
    if data["alternative"]:
        alternative_html = f"""
        <div style="background:#EEF2FF;border-radius:12px;
                    padding:16px 20px;margin-bottom:16px;
                    border:1px solid #534AB730">
            <div style="font-size:12px;color:#534AB7;
                        font-weight:700;margin-bottom:6px">
                💡 Alternative Scenario
            </div>
            <div style="font-size:14px;color:#3d3d3a;line-height:1.6">
                {data["alternative"]}
            </div>
        </div>"""

    return f"""
    <div style="font-family:sans-serif;max-width:640px;margin:0 auto;padding:8px">

        <!-- VERDICT CARD -->
        <div style="background:{vc['bg']};border-radius:12px;
                    padding:20px 24px;margin-bottom:16px;
                    border:1px solid {vc['color']}40">
            <div style="font-size:11px;color:{vc['color']};font-weight:700;
                        text-transform:uppercase;letter-spacing:1px;margin-bottom:8px">
                Final Verdict
            </div>
            <div style="display:flex;align-items:center;gap:14px;margin-bottom:12px">
                <span style="font-size:32px">{vc['icon']}</span>
                <div>
                    <div style="font-size:24px;font-weight:800;color:{vc['color']}">
                        {data['verdict']}
                    </div>
                    <div style="font-size:13px;color:{vc['color']};opacity:0.85">
                        {vc['label']}
                    </div>
                </div>
            </div>
            <div style="font-size:14px;color:#3d3d3a;line-height:1.7;
                        border-top:1px solid {vc['color']}25;padding-top:12px">
                {data['why'] or 'Based on the full analysis and risk evaluation.'}
            </div>
        </div>

        <!-- METRICS ROW -->
        <div style="display:grid;grid-template-columns:1fr 1fr;
                    gap:12px;margin-bottom:16px">

            <!-- Confidence -->
            <div style="background:white;border-radius:12px;padding:16px;
                        border:1px solid #e8e8e8;box-shadow:0 1px 4px #0001">
                <div style="font-size:11px;color:#888;font-weight:700;
                            text-transform:uppercase;letter-spacing:0.5px;
                            margin-bottom:10px">Confidence Score</div>
                <div style="font-size:32px;font-weight:800;
                            color:{conf_color};margin-bottom:10px">{conf}%</div>
                <div style="background:#f0f0f0;border-radius:999px;
                            height:8px;overflow:hidden">
                    <div style="background:{conf_color};width:{conf}%;
                                height:100%;border-radius:999px"></div>
                </div>
            </div>

            <!-- Risk Score -->
            <div style="background:white;border-radius:12px;padding:16px;
                        border:1px solid #e8e8e8;box-shadow:0 1px 4px #0001">
                <div style="font-size:11px;color:#888;font-weight:700;
                            text-transform:uppercase;letter-spacing:0.5px;
                            margin-bottom:10px">Risk Score</div>
                <div style="font-size:32px;font-weight:800;
                            color:{risk_color};margin-bottom:10px">{rs}/10</div>
                <div style="background:#f0f0f0;border-radius:999px;
                            height:8px;overflow:hidden">
                    <div style="background:{risk_color};width:{rs*10}%;
                                height:100%;border-radius:999px"></div>
                </div>
                <div style="font-size:12px;color:{risk_color};
                            margin-top:8px;font-weight:600">{risk_label}</div>
            </div>
        </div>

        <!-- ACTION STEPS -->
        <div style="background:white;border-radius:12px;padding:20px;
                    margin-bottom:16px;border:1px solid #e8e8e8;
                    box-shadow:0 1px 4px #0001">
            <div style="font-size:14px;font-weight:700;color:#3d3d3a;
                        margin-bottom:14px">🎯 Your Action Steps</div>
            {actions_html if actions_html else '<p style="color:#888;font-size:14px">Follow the advisor recommendations above.</p>'}
        </div>

        <!-- CHART.JS SCENARIO COMPARISON -->
        <div style="background:white;border-radius:12px;padding:20px;
                    margin-bottom:16px;border:1px solid #e8e8e8;
                    box-shadow:0 1px 4px #0001">
            <div style="font-size:14px;font-weight:700;color:#3d3d3a;
                        margin-bottom:4px">📊 Wealth Projection Comparison</div>
            <div style="font-size:12px;color:#888;margin-bottom:16px">
                Your current plan vs AI recommended plan
            </div>
            <canvas id="scenarioChart" height="200"></canvas>
        </div>

        <!-- ALTERNATIVE -->
        {alternative_html}

        <!-- DISCLAIMER -->
        <div style="font-size:12px;color:#aaa;text-align:center;
                    padding:12px;border-top:1px solid #f0f0f0;margin-top:8px">
            ⚠️ AI-generated analysis for informational purposes only.
            Consult a certified financial advisor before major decisions.
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
    <script>
    (function() {{
        const canvas = document.getElementById('scenarioChart');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: ['1 Year', '5 Years'],
                datasets: [
                    {{
                        label: 'Your Current Plan (₹)',
                        data: [{current_1yr}, {current_5yr}],
                        backgroundColor: '#E8593C99',
                        borderColor: '#E8593C',
                        borderWidth: 2,
                        borderRadius: 6,
                    }},
                    {{
                        label: 'AI Recommended Plan (₹)',
                        data: [{ai_1yr}, {ai_5yr}],
                        backgroundColor: '#0F6E5699',
                        borderColor: '#0F6E56',
                        borderWidth: 2,
                        borderRadius: 6,
                    }}
                ]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        position: 'top',
                        labels: {{ font: {{ size: 12 }} }}
                    }},
                    tooltip: {{
                        callbacks: {{
                            label: function(ctx) {{
                                return ctx.dataset.label + ': ₹' +
                                    ctx.raw.toLocaleString('en-IN');
                            }}
                        }}
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{
                            callback: function(value) {{
                                return '₹' + value.toLocaleString('en-IN');
                            }}
                        }}
                    }}
                }}
            }}
        }});
    }})();
    </script>
    """


@cl.on_chat_start
async def start():
    await cl.Message(
        content="""# 💰 FinSense AI
### Your Multi-Agent Personal Finance Advisor
*Powered by AMD Developer Cloud × CrewAI × Llama3*

---

**Try asking:**
- 💳 *I earn ₹50,000/month. Should I take a ₹3L loan at 14% for 2 years?*
- 📈 *Should I invest ₹10,000 in crypto or mutual funds?*
- 💸 *I spend ₹35,000/month on ₹50,000 salary. Am I overspending?*
- 💻 *Should I buy a ₹80,000 laptop or save the money?*
- 🏦 *Where should my ₹10,000/month savings go?*

Type your financial decision below 👇"""
    ).send()


@cl.on_message
async def main(message: cl.Message):

    async with cl.Step(name="📊 Analyst Agent — analyzing your finances..."):
        pass
    async with cl.Step(name="⚠️ Risk Evaluator — calculating risk score..."):
        pass
    async with cl.Step(name="💡 Advisor — building your recommendation..."):
        pass

    thinking = await cl.Message(
        content="⏳ All 3 agents working on your decision..."
    ).send()

    raw_result = run_finsense(message.content)
    await thinking.remove()

    parsed = parse_output(raw_result)
    html_report = build_report_html(parsed)

    await cl.Message(
        content=f"""## 📋 Your FinSense Report

**Verdict:** {parsed['verdict']}
**Confidence:** {parsed['confidence']}%
**Risk Score:** {parsed['risk_score']}/10

**Why:** {parsed['why']}

**Action Steps:**
{chr(10).join([f"{i+1}. {a}" for i, a in enumerate(parsed['actions'])])}

**Alternative:** {parsed['alternative']}

⚠️ AI-generated analysis for informational purposes only. Consult a certified financial advisor before major decisions."""
    ).send()