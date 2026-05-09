from crewai import Agent
from config.llm import get_llm

analyst = Agent(
    role="Personal Finance Analyst",
    goal="Analyze the user's financial situation and extract key metrics clearly",
    backstory="""You are a senior financial analyst specializing in 
    personal finance for young working professionals in India. 
    You break down numbers clearly, identify spending patterns, 
    and flag key financial metrics in simple language.""",
    llm=get_llm(),
    verbose=True
)