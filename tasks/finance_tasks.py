from crewai import Task
from agents.analyst import analyst
from agents.risk_evaluator import risk_evaluator
from agents.advisor import advisor

def create_tasks(user_input: str):

    analysis_task = Task(
        description=f"""Analyze this financial decision: "{user_input}"
        
        Extract key figures, identify decision type, calculate ratios.
        Summarize in 3 bullet points. End with: "Key concern: [one sentence]"
        """,
        agent=analyst,
        expected_output="3 bullet financial analysis with key concern"
    )

    risk_task = Task(
        description=f"""Evaluate risk for: "{user_input}"
        
        1. Risk Score: [1-10]
        2. Worst case: [1 sentence]
        3. Top risk: [1 sentence]
        4. Mitigation: [1 sentence]
        """,
        agent=risk_evaluator,
        expected_output="Risk score, worst case, top risk, mitigation"
    )

    advice_task = Task(
        description=f"""Give final recommendation for: "{user_input}"

        Respond in EXACTLY this format:
        VERDICT: [GO/WAIT/AVOID]
        CONFIDENCE: [0-100]%
        Risk Score: [1-10]
        
        WHY: [2 sentences max]
        
        ACTION STEPS:
        1. [action]
        2. [action]
        3. [action]
        
        ALTERNATIVE: [1 sentence]
        
        DISCLAIMER: AI analysis only. Consult a certified advisor.
        """,
        agent=advisor,
        expected_output="Structured verdict with confidence, risk, actions"
    )

    return [analysis_task, risk_task, advice_task]