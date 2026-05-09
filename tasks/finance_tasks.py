from crewai import Task
from agents.analyst import analyst
from agents.risk_evaluator import risk_evaluator
from agents.advisor import advisor

def create_tasks(user_input: str):

    analysis_task = Task(
        description=f"""
        The user has shared this financial decision:
        "{user_input}"

        Your job:
        1. Extract all key financial figures (amounts, income, timeframes)
        2. Identify the type of decision (spending / saving / investing / loan)
        3. Calculate relevant ratios (EMI-to-income ratio, savings rate, etc.)
        4. Summarize your findings in 4-5 clear bullet points
        5. End with: "Key concern: [one sentence]"
        """,
        agent=analyst,
        expected_output="Bullet-point financial analysis with key metrics and one key concern"
    )

    risk_task = Task(
        description=f"""
        Based on the analyst's findings about this decision:
        "{user_input}"

        Your job:
        1. Assign a Risk Score from 1 (very safe) to 10 (very risky)
        2. Write the worst-case scenario in 2 sentences
        3. List the top 2 risk factors
        4. Suggest one specific way to reduce the biggest risk
        
        Format your response clearly with these 4 sections labeled.
        """,
        agent=risk_evaluator,
        expected_output="Risk score, worst-case scenario, top 2 risk factors, one mitigation tip"
    )

    advice_task = Task(
        description=f"""
        Based on the full analysis and risk evaluation for:
        "{user_input}"

        Your job — respond in this EXACT format:

        VERDICT: [GO / WAIT / AVOID]
        CONFIDENCE: [0-100]%

        WHY: [2-3 sentences explaining your recommendation]

        ACTION STEPS:
        1. [Specific action step]
        2. [Specific action step]  
        3. [Specific action step]

        ALTERNATIVE: If instead you [did X], you could [outcome Y].

        DISCLAIMER: This is AI-generated analysis for informational 
        purposes only. Consult a certified financial advisor before 
        making major decisions.
        """,
        agent=advisor,
        expected_output="Structured verdict with confidence score, reasoning, 3 action steps, alternative scenario"
    )

    return [analysis_task, risk_task, advice_task]