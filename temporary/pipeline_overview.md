# 🏥 AI Medical Diagnostics — Full Pipeline Explanation

## 🔭 Overview

This project implements a **Multi-Agent AI System** for medical diagnostics. Multiple AI agents, each playing a specialist doctor role, independently analyze a patient's medical report. Their findings are then synthesized by a final "team" agent to produce a comprehensive diagnosis.

---

## 🗺️ Pipeline Diagram

```
📄 Medical Report (raw text)
        │
        ▼
┌───────────────────────────────────────────┐
│         Concurrent Specialist Agents       │
│                                           │
│  🫀 Cardiologist  🧠 Psychologist  🫁 Pulmonologist │
│       Agent           Agent            Agent     │
└───────────────┬────────────┬────────────┬────────┘
                │            │            │
                ▼            ▼            ▼
         Cardiac         Mental       Respiratory
         Report          Report        Report
                │            │            │
                └────────────┴────────────┘
                             │
                             ▼
                ┌─────────────────────────┐
                │  MultidisciplinaryTeam  │
                │        Agent            │
                └────────────┬────────────┘
                             │
                             ▼
                  📝 final_diagnosis.txt
```

---

## 📋 Step-by-Step Pipeline Breakdown

### Step 1 — Load Environment Variables (`Main.py`)

```python
from dotenv import load_dotenv
load_dotenv(dotenv_path='apikey.env')
```

- Reads `apikey.env` and loads `GOOGLE_API_KEY` into the environment
- The `ChatGoogleGenerativeAI` model automatically picks this up to authenticate with Google's API

---

### Step 2 — Read the Medical Report (`Main.py`)

```python
with open("Medical Reports\Medical Report - Michael Johnson - Panic Attack Disorder.txt", "r") as file:
    medical_report = file.read()
```

- Reads the full text of the patient's medical report as a single string
- This string is passed to each specialist agent

---

### Step 3 — Initialize the 3 Specialist Agents (`Main.py`)

```python
agents = {
    "Cardiologist":  Cardiologist(medical_report),
    "Psychologist":  Psychologist(medical_report),
    "Pulmonologist": Pulmonologist(medical_report)
}
```

- Each agent class is defined in `Utils/Agents.py`
- During `__init__`, each agent:
  1. Stores the `medical_report`
  2. Creates its role-specific **prompt template**
  3. Initializes the **Gemini LLM model**

---

### Step 4 — Run Agents Concurrently (`Main.py`)

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

responses = {}
with ThreadPoolExecutor() as executor:
    futures = {executor.submit(get_response, name, agent): name for name, agent in agents.items()}

    for future in as_completed(futures):
        agent_name, response = future.result()
        responses[agent_name] = response
```

#### Why concurrent / parallel execution?

- Each agent makes a **separate API call** to Gemini which takes time
- Running them **simultaneously** using `ThreadPoolExecutor` means all 3 API calls happen **at the same time**
- This saves time: instead of waiting 3× sequentially, it's ~1× (the slowest one)

#### What `get_response()` does:

```python
def get_response(agent_name, agent):
    response = agent.run()   # Calls Gemini API with the role prompt
    return agent_name, response
```

Inside `agent.run()`:
1. The `{medical_report}` placeholder in the prompt is filled with real report text
2. The formatted prompt is sent to Gemini
3. Gemini's response is cleaned and returned as a plain string

After this step, `responses` dict looks like:
```python
{
    "Cardiologist":  "Possible cardiac causes: ...",
    "Psychologist":  "Mental health assessment: ...",
    "Pulmonologist": "Respiratory concerns: ..."
}
```

---

### Step 5 — Initialize `MultidisciplinaryTeam` Agent (`Main.py`)

```python
team_agent = MultidisciplinaryTeam(
    cardiologist_report=responses["Cardiologist"],
    psychologist_report=responses["Psychologist"],
    pulmonologist_report=responses["Pulmonologist"]
)
```

- The 3 specialist reports are passed as input
- The team agent's prompt embeds all 3 reports and asks Gemini to:
  - Act as a **multidisciplinary healthcare team**
  - Review all 3 reports together
  - Produce a list of **3 most likely health issues** with reasons

---

### Step 6 — Generate Final Diagnosis (`Main.py`)

```python
final_diagnosis = team_agent.run()
```

- Same `run()` method is called as before
- Gemini now synthesizes all 3 reports and returns the combined diagnosis

---

### Step 7 — Save Output to File (`Main.py`)

```python
final_diagnosis_text = "### Final Diagnosis:\n\n" + final_diagnosis
txt_output_path = "results/final_diagnosis.txt"

os.makedirs(os.path.dirname(txt_output_path), exist_ok=True)

with open(txt_output_path, "w") as txt_file:
    txt_file.write(final_diagnosis_text)

print(f"Final diagnosis has been saved to {txt_output_path}")
```

- Prepends a markdown heading `### Final Diagnosis:`
- Creates the `results/` folder if it doesn't exist
- Writes the clean diagnosis text to `final_diagnosis.txt`

---

## 🧩 Key Design Concepts

### 1. Multi-Agent System
Each agent is a **separate AI instance** with a different "persona" (role). This mirrors real-world clinical practice where specialists give independent opinions.

### 2. Separation of Concerns
| File | Responsibility |
|---|---|
| `Main.py` | Orchestration — reads input, runs agents, saves output |
| `Utils/Agents.py` | Agent logic — prompts, LLM calls, response handling |
| `apikey.env` | Configuration — API keys |
| `Medical Reports/` | Input data |
| `Results/` | Output data |

### 3. Prompt Engineering
Each agent has a carefully crafted prompt that:
- Gives the LLM a **specific role** (`"Act like a cardiologist..."`)
- Defines the **task** clearly
- Specifies the **focus** areas
- Restricts the **output format** to only relevant findings

### 4. Inheritance Pattern
All agents share the same `run()` method and LLM via the base `Agent` class. Only the **prompt** differs per role. This makes it easy to add new specialist types in the future.

---

## 📂 Project File Structure

```
AI-Agents-for-Medical-Diagnostics/
│
├── Main.py                    ← Entry point / orchestrator
├── apikey.env                 ← API key (GOOGLE_API_KEY)
├── requirements.txt           ← Python dependencies
│
├── Utils/
│   └── Agents.py              ← All agent classes and LLM logic
│
├── Medical Reports/           ← Input: patient medical reports (.txt)
│
├── Results/
│   └── final_diagnosis.txt    ← Output: final AI diagnosis
│
└── temporary/                 ← Study/documentation folder
    ├── agents_explanation.md
    └── pipeline_overview.md
```

---

## ⚡ How to Run

```bash
# Activate virtual environment
.venv\Scripts\activate

# Run the pipeline
python main.py
```

Output will be saved to: `Results/final_diagnosis.txt`
