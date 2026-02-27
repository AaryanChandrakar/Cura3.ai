"""
Cura3.ai — AI Agent Engine
Upgraded from the original Utils/Agents.py with expanded specialist list,
async execution, and structured output formatting.
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from app.config import settings
import os

# Ensure the OpenAI API key is available
os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY


# ── Specialist Definitions ───────────────────────────────

SPECIALISTS = {
    "Cardiologist": {
        "display_name": "Cardiologist",
        "icon": "heart",
        "prompt": """
            Act like a cardiologist. You will receive a medical report of a patient.
            Task: Review the patient's cardiac workup, including ECG, blood tests, Holter monitor results, and echocardiogram.
            Focus: Determine if there are any subtle signs of cardiac issues that could explain the patient's symptoms. Rule out any underlying heart conditions, such as arrhythmias or structural abnormalities, that might be missed on routine testing.
            Recommendation: Provide guidance on any further cardiac testing or monitoring needed to ensure there are no hidden heart-related concerns. Suggest potential management strategies if a cardiac issue is identified.
            Please only return the possible causes of the patient's symptoms and the recommended next steps.
            Medical Report: {medical_report}
        """,
    },
    "Psychologist": {
        "display_name": "Psychologist",
        "icon": "brain",
        "prompt": """
            Act like a psychologist. You will receive a patient's report.
            Task: Review the patient's report and provide a psychological assessment.
            Focus: Identify any potential mental health issues, such as anxiety, depression, or trauma, that may be affecting the patient's well-being.
            Recommendation: Offer guidance on how to address these mental health concerns, including therapy, counseling, or other interventions.
            Please only return the possible mental health issues and the recommended next steps.
            Patient's Report: {medical_report}
        """,
    },
    "Pulmonologist": {
        "display_name": "Pulmonologist",
        "icon": "lungs",
        "prompt": """
            Act like a pulmonologist. You will receive a patient's report.
            Task: Review the patient's report and provide a pulmonary assessment.
            Focus: Identify any potential respiratory issues, such as asthma, COPD, or lung infections, that may be affecting the patient's breathing.
            Recommendation: Offer guidance on how to address these respiratory concerns, including pulmonary function tests, imaging studies, or other interventions.
            Please only return the possible respiratory issues and the recommended next steps.
            Patient's Report: {medical_report}
        """,
    },
    "Neurologist": {
        "display_name": "Neurologist",
        "icon": "nerve",
        "prompt": """
            Act like a neurologist. You will receive a patient's medical report.
            Task: Review the patient's neurological symptoms, imaging results, and any relevant test findings.
            Focus: Identify potential neurological conditions such as neuropathy, seizure disorders, migraines, multiple sclerosis, or neurodegenerative diseases (e.g., Alzheimer's, Parkinson's).
            Recommendation: Suggest further neurological testing (EEG, MRI, nerve conduction studies) and management strategies.
            Please only return the possible neurological causes and the recommended next steps.
            Patient's Report: {medical_report}
        """,
    },
    "Endocrinologist": {
        "display_name": "Endocrinologist",
        "icon": "hormone",
        "prompt": """
            Act like an endocrinologist. You will receive a patient's medical report.
            Task: Review the patient's hormonal profiles, metabolic markers, and endocrine-related symptoms.
            Focus: Identify potential endocrine disorders such as diabetes, thyroid disorders (hypo/hyperthyroidism), adrenal insufficiency, PCOS, or hormonal imbalances.
            Recommendation: Suggest appropriate hormonal panels, imaging, and management strategies.
            Please only return the possible endocrine causes and the recommended next steps.
            Patient's Report: {medical_report}
        """,
    },
    "Oncologist": {
        "display_name": "Oncologist",
        "icon": "ribbon",
        "prompt": """
            Act like an oncologist. You will receive a patient's medical report.
            Task: Review the patient's lab results, imaging, biopsy reports, and symptom history for any signs of malignancy.
            Focus: Identify potential neoplastic conditions, assess risk factors, and evaluate any suspicious findings that warrant further investigation for cancer.
            Recommendation: Suggest appropriate screening, biopsy, imaging (CT, PET scan), tumor markers, and referral pathways.
            Please only return the possible oncological concerns and the recommended next steps.
            Patient's Report: {medical_report}
        """,
    },
    "Dermatologist": {
        "display_name": "Dermatologist",
        "icon": "skin",
        "prompt": """
            Act like a dermatologist. You will receive a patient's medical report.
            Task: Review the patient's skin-related symptoms, lesion descriptions, and any relevant history.
            Focus: Identify potential dermatological conditions such as eczema, psoriasis, skin infections, autoimmune skin disorders, or suspicious moles/lesions.
            Recommendation: Suggest further dermatological examination, biopsy if needed, and treatment approaches.
            Please only return the possible dermatological causes and the recommended next steps.
            Patient's Report: {medical_report}
        """,
    },
    "Gastroenterologist": {
        "display_name": "Gastroenterologist",
        "icon": "stomach",
        "prompt": """
            Act like a gastroenterologist. You will receive a patient's medical report.
            Task: Review the patient's gastrointestinal symptoms, lab results, and any imaging or endoscopy findings.
            Focus: Identify potential GI conditions such as IBS, IBD (Crohn's, ulcerative colitis), GERD, celiac disease, liver disorders, or GI malignancies.
            Recommendation: Suggest appropriate testing (endoscopy, colonoscopy, stool tests, imaging) and management strategies.
            Please only return the possible gastrointestinal causes and the recommended next steps.
            Patient's Report: {medical_report}
        """,
    },
    "Orthopedist": {
        "display_name": "Orthopedist",
        "icon": "bone",
        "prompt": """
            Act like an orthopedist. You will receive a patient's medical report.
            Task: Review the patient's musculoskeletal symptoms, imaging results (X-ray, MRI), and physical examination findings.
            Focus: Identify potential orthopedic conditions such as fractures, arthritis, tendon injuries, disc herniation, or degenerative joint diseases.
            Recommendation: Suggest appropriate imaging, physical therapy, surgical consultation if needed, and pain management strategies.
            Please only return the possible musculoskeletal causes and the recommended next steps.
            Patient's Report: {medical_report}
        """,
    },
    "General Practitioner": {
        "display_name": "General Practitioner",
        "icon": "stethoscope",
        "prompt": """
            Act like a general practitioner / family medicine physician. You will receive a patient's medical report.
            Task: Review the patient's overall health status, vital signs, symptoms, and medical history holistically.
            Focus: Identify common conditions, preventive care needs, and any red flags that require specialist referral. Consider the patient's complete picture including lifestyle factors.
            Recommendation: Suggest initial workup, lifestyle modifications, preventive measures, and appropriate specialist referrals.
            Please only return the possible health concerns and the recommended next steps.
            Patient's Report: {medical_report}
        """,
    },
}

# All available specialist names
AVAILABLE_SPECIALISTS = list(SPECIALISTS.keys())


# ── Multidisciplinary Team Prompt ────────────────────────

TEAM_PROMPT_TEMPLATE = """
Act as a multidisciplinary team of healthcare professionals.
You will receive specialist reports from multiple medical specialists
who each independently analyzed the same patient's medical report.

YOUR TASK:
Analyze all specialist reports and produce a comprehensive final diagnosis report.
Identify the TOP 3 most likely health issues for this patient.

IMPORTANT FORMATTING RULES - you MUST follow this exact structure:
- Use ONLY plain ASCII text. Do NOT use any special characters, unicode, or emojis.
- Do NOT use asterisks (*), bullet points, or markdown formatting.
- Use simple dashes (-) for any lists.
- Use the EXACT structure shown below.

OUTPUT FORMAT (follow this exactly):

============================================================
                  FINAL DIAGNOSIS REPORT
============================================================

PATIENT OVERVIEW:
[Brief 2-3 sentence summary of the patient's presenting complaints
and key findings across all specialist evaluations.]

------------------------------------------------------------
IDENTIFIED HEALTH ISSUES
------------------------------------------------------------

ISSUE 1: [Name of the condition]
Severity: [Low / Moderate / High / Critical]
Identified By: [Which specialist(s) flagged this]

Reasoning:
[Clear explanation of why this is suspected, referencing specific
findings from the specialist reports. 3-4 sentences.]

Recommended Next Steps:
- [Action item 1]
- [Action item 2]
- [Action item 3]

ISSUE 2: [Name of the condition]
Severity: [Low / Moderate / High / Critical]
Identified By: [Which specialist(s) flagged this]

Reasoning:
[Clear explanation. 3-4 sentences.]

Recommended Next Steps:
- [Action item 1]
- [Action item 2]
- [Action item 3]

ISSUE 3: [Name of the condition]
Severity: [Low / Moderate / High / Critical]
Identified By: [Which specialist(s) flagged this]

Reasoning:
[Clear explanation. 3-4 sentences.]

Recommended Next Steps:
- [Action item 1]
- [Action item 2]
- [Action item 3]

------------------------------------------------------------
PRIORITY RECOMMENDATION
------------------------------------------------------------
[1-2 sentences on which issue should be addressed first and why.]

------------------------------------------------------------
NOTE: This report is generated by AI for research and educational
purposes only. It is NOT a substitute for professional medical
advice, diagnosis, or treatment. Always consult a qualified
healthcare provider for medical decisions.
------------------------------------------------------------

{specialist_reports_section}
"""


def _sanitize_text(text: str) -> str:
    """Replace common unicode characters with ASCII equivalents."""
    replacements = {
        "\u2018": "'", "\u2019": "'",
        "\u201c": '"', "\u201d": '"',
        "\u2013": "-", "\u2014": "--",
        "\u2026": "...", "\u2022": "-",
        "\u00b7": "-", "\u2023": "-",
        "\u25cf": "-", "\u25cb": "-",
        "\u2192": "->",
    }
    for uc, ac in replacements.items():
        text = text.replace(uc, ac)
    return text


def _get_model():
    """Get the OpenAI GPT-4.1 model instance."""
    return ChatOpenAI(
        temperature=0,
        model="gpt-4.1",
    )


def _run_specialist(specialist_name: str, medical_report: str) -> dict:
    """Run a single specialist agent synchronously (used inside thread pool)."""
    spec = SPECIALISTS[specialist_name]
    prompt_template = PromptTemplate.from_template(spec["prompt"])
    prompt = prompt_template.format(medical_report=medical_report)
    model = _get_model()

    try:
        response = model.invoke(prompt)
        content = response.content
        if isinstance(content, list):
            content = " ".join(
                item["text"] if isinstance(item, dict) and "text" in item else str(item)
                for item in content
            )
        return {
            "specialist_name": specialist_name,
            "report_content": _sanitize_text(str(content)),
        }
    except Exception as e:
        return {
            "specialist_name": specialist_name,
            "report_content": f"Error: Could not generate report. {str(e)}",
        }


def _run_team_diagnosis(specialist_reports: list) -> str:
    """Run the multidisciplinary team agent to produce final diagnosis."""
    # Build the specialist reports section
    reports_section = ""
    for report in specialist_reports:
        name = report["specialist_name"]
        content = report["report_content"].replace("{", "{{").replace("}", "}}")
        reports_section += f"\n{name} Report:\n{content}\n"

    prompt_text = TEAM_PROMPT_TEMPLATE.replace(
        "{specialist_reports_section}", reports_section
    )
    model = _get_model()

    try:
        response = model.invoke(prompt_text)
        content = response.content
        if isinstance(content, list):
            content = " ".join(
                item["text"] if isinstance(item, dict) and "text" in item else str(item)
                for item in content
            )
        return _sanitize_text(str(content))
    except Exception as e:
        return f"Error generating final diagnosis: {str(e)}"


async def run_diagnosis(medical_report: str, specialists: list[str]) -> dict:
    """
    Run a full diagnosis pipeline:
    1. Run all selected specialists in parallel
    2. Combine results with the multidisciplinary team agent
    3. Return structured results

    Args:
        medical_report: The raw text of the medical report
        specialists: List of specialist names to run

    Returns:
        dict with specialist_reports and final_diagnosis
    """
    loop = asyncio.get_event_loop()

    # Run all specialists in parallel using a thread pool
    with ThreadPoolExecutor(max_workers=len(specialists)) as executor:
        futures = [
            loop.run_in_executor(executor, _run_specialist, name, medical_report)
            for name in specialists
        ]
        specialist_reports = await asyncio.gather(*futures)

    # Run the multidisciplinary team agent
    final_diagnosis = await loop.run_in_executor(
        None, _run_team_diagnosis, list(specialist_reports)
    )

    return {
        "specialist_reports": list(specialist_reports),
        "final_diagnosis": final_diagnosis,
    }
