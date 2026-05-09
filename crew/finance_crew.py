from crewai import Crew, Process
from agents.analyst import analyst
from agents.risk_evaluator import risk_evaluator
from agents.advisor import advisor
from tasks.finance_tasks import create_tasks


def run_finsense(user_input: str) -> dict:
    """
    Run the 3-agent pipeline and return individual agent outputs.
    Returns a dict with keys: analyst_output, risk_output, advisor_output, raw
    """
    tasks = create_tasks(user_input)

    crew = Crew(
        agents=[analyst, risk_evaluator, advisor],
        tasks=tasks,
        process=Process.sequential,
        verbose=True
    )

    result = crew.kickoff()
    raw = str(result)

    # Extract individual task outputs
    analyst_out = ""
    risk_out    = ""
    advisor_out = ""

    try:
        analyst_out = str(tasks[0].output.raw) if tasks[0].output else ""
    except:
        pass
    try:
        risk_out = str(tasks[1].output.raw) if tasks[1].output else ""
    except:
        pass
    try:
        advisor_out = str(tasks[2].output.raw) if tasks[2].output else ""
    except:
        advisor_out = raw

    return {
        "analyst_output": analyst_out or raw,
        "risk_output":    risk_out    or raw,
        "advisor_output": advisor_out or raw,
        "raw":            raw,
    }