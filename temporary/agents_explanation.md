# 🧠 Agents.py — Detailed Explanation

## 📁 File Location
```
Utils/Agents.py
```

---

## 📦 Imports

```python
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
```

| Import | Purpose |
|---|---|
| `PromptTemplate` | LangChain utility to create structured prompt templates with placeholders |
| `ChatGoogleGenerativeAI` | LangChain wrapper around Google Gemini API to invoke the LLM |

---

## 🏛️ Class Architecture

```
Agent  (Base Class)
├── Cardiologist
├── Psychologist
├── Pulmonologist
└── MultidisciplinaryTeam
```

All 4 specialist classes **inherit** from the base `Agent` class. This keeps the code clean and avoids repetition (DRY principle).

---

## 🔷 Base Class: `Agent`

```python
class Agent:
    def __init__(self, medical_report=None, role=None, extra_info=None):
        self.medical_report = medical_report
        self.role = role
        self.extra_info = extra_info
        self.prompt_template = self.create_prompt_template()
        self.model = ChatGoogleGenerativeAI(temperature=0, model="gemini-3-flash-preview")
```

### Constructor Parameters

| Parameter | Type | Description |
|---|---|---|
| `medical_report` | `str` | Raw text of the patient's medical report |
| `role` | `str` | The specialist role: `"Cardiologist"`, `"Psychologist"`, `"Pulmonologist"`, or `"MultidisciplinaryTeam"` |
| `extra_info` | `dict` | Used only by `MultidisciplinaryTeam` to receive the 3 specialist reports |

### Key Attributes

- **`self.prompt_template`** — Built by calling `create_prompt_template()` during init. Stores the role-specific prompt.
- **`self.model`** — The Gemini LLM instance shared by all agents.
  - `temperature=0` → Deterministic, factual responses (no creativity/randomness)
  - `model="gemini-3-flash-preview"` → Fast Gemini model

---

## 🔶 Method: `create_prompt_template()`

This method builds a **role-specific prompt** using LangChain's `PromptTemplate`.

### For `MultidisciplinaryTeam`:

```python
if self.role == "MultidisciplinaryTeam":
    cardiologist_report = str(self.extra_info.get('cardiologist_report', '')).replace('{', '{{').replace('}', '}}')
    psychologist_report  = str(self.extra_info.get('psychologist_report', '')).replace('{', '{{').replace('}', '}}')
    pulmonologist_report = str(self.extra_info.get('pulmonologist_report', '')).replace('{', '{{').replace('}', '}}')
    templates = f"""
        Act like a multidisciplinary team...
        Cardiologist Report: {cardiologist_report}
        Psychologist Report: {psychologist_report}
        Pulmonologist Report: {pulmonologist_report}
    """
```

> ⚠️ **Why `.replace('{', '{{')` ?**
> Gemini responses can contain curly braces `{}` in the text.
> LangChain's `PromptTemplate` interprets `{anything}` as a variable placeholder.
> Escaping `{` → `{{` and `}` → `}}` tells LangChain to treat them as **literal characters**, not variables.
> Without this, you'd get: `KeyError: "'type'"`.

### For Specialist Agents (Cardiologist / Psychologist / Pulmonologist):

Each role has a dedicated prompt string with a `{medical_report}` placeholder:

```python
templates = {
    "Cardiologist": """
        Act like a cardiologist...
        Medical Report: {medical_report}
    """,
    "Psychologist": """
        Act like a psychologist...
        Patient's Report: {medical_report}
    """,
    "Pulmonologist": """
        Act like a pulmonologist...
        Patient's Report: {medical_report}
    """
}
templates = templates[self.role]   # Pick the right one based on role
```

Finally, all templates are converted to a LangChain `PromptTemplate` object:

```python
return PromptTemplate.from_template(templates)
```

---

## 🔶 Method: `run()`

```python
def run(self):
    print(f"{self.role} is running...")
    prompt = self.prompt_template.format(medical_report=self.medical_report)
    try:
        response = self.model.invoke(prompt)
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
```

### Step-by-step:

1. **Format the prompt** → fills `{medical_report}` placeholder with the actual report text
2. **Invoke the model** → sends the prompt to Google Gemini API and waits for response
3. **Handle response content** → Gemini sometimes returns content as:
   - A plain `str` → use directly
   - A `list` of dicts like `[{'type': 'text', 'text': 'actual response'}]` → extract only the `"text"` value
4. **Return** the clean string response

---

## 🟢 Specialist Agent Classes

These are simple subclasses that just call the parent `__init__` with their specific role:

```python
class Cardiologist(Agent):
    def __init__(self, medical_report):
        super().__init__(medical_report, "Cardiologist")

class Psychologist(Agent):
    def __init__(self, medical_report):
        super().__init__(medical_report, "Psychologist")

class Pulmonologist(Agent):
    def __init__(self, medical_report):
        super().__init__(medical_report, "Pulmonologist")
```

Each one:
- Takes only the `medical_report` as input
- Passes its own role name as a string to the parent
- Inherits all logic (`create_prompt_template`, `run`, model) from `Agent`

---

## 🟣 `MultidisciplinaryTeam` Class

```python
class MultidisciplinaryTeam(Agent):
    def __init__(self, cardiologist_report, psychologist_report, pulmonologist_report):
        extra_info = {
            "cardiologist_report": cardiologist_report,
            "psychologist_report": psychologist_report,
            "pulmonologist_report": pulmonologist_report
        }
        super().__init__(role="MultidisciplinaryTeam", extra_info=extra_info)
```

- Takes the **3 specialist reports** as input (already generated)
- Packs them into an `extra_info` dictionary
- Does **not** take a `medical_report` (it uses the specialist summaries instead)
- Its prompt instructs Gemini to act as a **team** and produce a final combined diagnosis

---

## 🗂️ Summary Table

| Class | Input | Role String | Uses `extra_info`? |
|---|---|---|---|
| `Cardiologist` | `medical_report` | `"Cardiologist"` | ❌ |
| `Psychologist` | `medical_report` | `"Psychologist"` | ❌ |
| `Pulmonologist` | `medical_report` | `"Pulmonologist"` | ❌ |
| `MultidisciplinaryTeam` | 3 specialist reports | `"MultidisciplinaryTeam"` | ✅ |
