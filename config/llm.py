import os
from dotenv import load_dotenv
load_dotenv()

def get_llm():
    from crewai import LLM
    return LLM(
        model="openai/Qwen/Qwen2.5-72B-Instruct",
        base_url="http://165.245.132.55:8000/v1",
        api_key="dummy"
    )