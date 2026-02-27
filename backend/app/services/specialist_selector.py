"""
Cura3.ai — Smart Specialist Selector
Uses an LLM call to analyze the medical report and recommend
the most relevant specialists for the case.
"""
from langchain_openai import ChatOpenAI
from app.config import settings
from app.services.agent_engine import AVAILABLE_SPECIALISTS
import os, json

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY

SELECTOR_PROMPT = """
You are a medical triage AI. You will receive a patient's medical report.
Your task is to determine which medical specialists should review this report.

Available specialists:
{specialists_list}

Analyze the report carefully and select the TOP 3-5 most relevant specialists
based on the patient's symptoms, conditions, and test results mentioned.

IMPORTANT: Return ONLY a valid JSON array of specialist names, nothing else.
Example: ["Cardiologist", "Pulmonologist", "General Practitioner"]

Do NOT include any explanation, just the JSON array.

Medical Report:
{medical_report}
"""


async def auto_select_specialists(medical_report: str) -> list[str]:
    """
    Analyze a medical report and return recommended specialists.

    Args:
        medical_report: Raw text content of the medical report

    Returns:
        List of recommended specialist names (3-5)
    """
    specialists_list = "\n".join(f"- {s}" for s in AVAILABLE_SPECIALISTS)

    prompt = SELECTOR_PROMPT.format(
        specialists_list=specialists_list,
        medical_report=medical_report,
    )

    model = ChatOpenAI(
        temperature=0,
        model="gpt-4.1",
    )

    try:
        response = model.invoke(prompt)
        content = response.content

        if isinstance(content, list):
            content = " ".join(
                item["text"] if isinstance(item, dict) and "text" in item else str(item)
                for item in content
            )

        # Parse JSON array from response
        content = str(content).strip()
        # Remove markdown code fences if present
        if content.startswith("```"):
            content = content.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

        selected = json.loads(content)

        # Validate that all selected specialists exist
        valid = [s for s in selected if s in AVAILABLE_SPECIALISTS]

        # Ensure at least General Practitioner is included if list is too short
        if len(valid) < 2:
            if "General Practitioner" not in valid:
                valid.append("General Practitioner")

        return valid[:5]  # Cap at 5 specialists

    except Exception as e:
        print(f"[Specialist Selector] Error: {e}")
        # Fallback to default 3 specialists
        return ["Cardiologist", "Psychologist", "Pulmonologist"]
