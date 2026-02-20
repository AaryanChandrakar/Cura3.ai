from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

class Agent:
    def __init__(self, medical_report=None, role=None, extra_info=None):
        self.medical_report = medical_report
        self.role = role
        self.extra_info = extra_info
        # Initialize the prompt based on role and other info
        self.prompt_template = self.create_prompt_template()
        # Initialize the model
        self.model = ChatGoogleGenerativeAI(temperature=0, model="gemini-3-flash-preview")

    def create_prompt_template(self):
        if self.role == "MultidisciplinaryTeam":
            # Escape curly braces in reports to prevent LangChain PromptTemplate
            # from misinterpreting them as template variables (e.g., Gemini may
            # return JSON-like text containing { } which causes a KeyError).
            cardiologist_report = str(self.extra_info.get('cardiologist_report', '')).replace('{', '{{').replace('}', '}}')
            psychologist_report  = str(self.extra_info.get('psychologist_report', '')).replace('{', '{{').replace('}', '}}')
            pulmonologist_report = str(self.extra_info.get('pulmonologist_report', '')).replace('{', '{{').replace('}', '}}')
            templates = f"""
                Act like a multidisciplinary team of healthcare professionals.
                You will receive a medical report of a patient visited by a Cardiologist, Psychologist, and Pulmonologist.
                Task: Review the patient's medical report from the Cardiologist, Psychologist, and Pulmonologist, analyze them and come up with a list of 3 possible health issues of the patient.
                Just return a list of bullet points of 3 possible health issues of the patient and for each issue provide the reason.

                Cardiologist Report: {cardiologist_report}
                Psychologist Report: {psychologist_report}
                Pulmonologist Report: {pulmonologist_report}
            """
        else:
            templates = {
                "Cardiologist": """
                    Act like a cardiologist. You will receive a medical report of a patient.
                    Task: Review the patient's cardiac workup, including ECG, blood tests, Holter monitor results, and echocardiogram.
                    Focus: Determine if there are any subtle signs of cardiac issues that could explain the patient’s symptoms. Rule out any underlying heart conditions, such as arrhythmias or structural abnormalities, that might be missed on routine testing.
                    Recommendation: Provide guidance on any further cardiac testing or monitoring needed to ensure there are no hidden heart-related concerns. Suggest potential management strategies if a cardiac issue is identified.
                    Please only return the possible causes of the patient's symptoms and the recommended next steps.
                    Medical Report: {medical_report}
                """,
                "Psychologist": """
                    Act like a psychologist. You will receive a patient's report.
                    Task: Review the patient's report and provide a psychological assessment.
                    Focus: Identify any potential mental health issues, such as anxiety, depression, or trauma, that may be affecting the patient's well-being.
                    Recommendation: Offer guidance on how to address these mental health concerns, including therapy, counseling, or other interventions.
                    Please only return the possible mental health issues and the recommended next steps.
                    Patient's Report: {medical_report}
                """,
                "Pulmonologist": """
                    Act like a pulmonologist. You will receive a patient's report.
                    Task: Review the patient's report and provide a pulmonary assessment.
                    Focus: Identify any potential respiratory issues, such as asthma, COPD, or lung infections, that may be affecting the patient's breathing.
                    Recommendation: Offer guidance on how to address these respiratory concerns, including pulmonary function tests, imaging studies, or other interventions.
                    Please only return the possible respiratory issues and the recommended next steps.
                    Patient's Report: {medical_report}
                """
            }
            templates = templates[self.role]
        return PromptTemplate.from_template(templates)
    
    def run(self):
        print(f"{self.role} is running...")
        prompt = self.prompt_template.format(medical_report=self.medical_report)
        try:
            response = self.model.invoke(prompt)
            # Gemini can return content as a list of content block dicts e.g.
            # [{'type': 'text', 'text': 'actual response...'}]
            # Extract just the "text" field to get clean, readable output.
            content = response.content
            if isinstance(content, list):
                content = " ".join(
                    item["text"] if isinstance(item, dict) and "text" in item else str(item)
                    for item in content
                )
            return str(content)
        except Exception as e:
            print("Error occurred:", e)
            return None

# Define specialized agent classes
class Cardiologist(Agent):
    def __init__(self, medical_report):
        super().__init__(medical_report, "Cardiologist")

class Psychologist(Agent):
    def __init__(self, medical_report):
        super().__init__(medical_report, "Psychologist")

class Pulmonologist(Agent):
    def __init__(self, medical_report):
        super().__init__(medical_report, "Pulmonologist")

class MultidisciplinaryTeam(Agent):
    def __init__(self, cardiologist_report, psychologist_report, pulmonologist_report):
        extra_info = {
            "cardiologist_report": cardiologist_report,
            "psychologist_report": psychologist_report,
            "pulmonologist_report": pulmonologist_report
        }
        super().__init__(role="MultidisciplinaryTeam", extra_info=extra_info)
