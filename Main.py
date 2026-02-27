# Importing the needed modules 
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from Utils.Agents import Cardiologist, Psychologist, Pulmonologist, MultidisciplinaryTeam
import json, os
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Loading API key from a dotenv file.
load_dotenv(dotenv_path='apikey.env')

# ── Report Selection ─────────────────────────────
reports_dir = "Medical Reports"
report_files = sorted(
    [f for f in os.listdir(reports_dir) if f.endswith(".txt")]
)

if not report_files:
    print("No medical reports found in the 'Medical Reports' folder.")
    exit(1)

print("\n" + "=" * 60)
print("       🏥  AI Medical Diagnostics – Report Selector")
print("=" * 60)
print("\nAvailable Medical Reports:\n")

for idx, report in enumerate(report_files, start=1):
    # Display a clean name (remove extension)
    display_name = os.path.splitext(report)[0]
    print(f"  [{idx}] {display_name}")

print()

# Prompt user until a valid choice is made
while True:
    try:
        choice = int(input(f"Select a report (1-{len(report_files)}): "))
        if 1 <= choice <= len(report_files):
            break
        else:
            print(f"  ⚠  Please enter a number between 1 and {len(report_files)}.")
    except ValueError:
        print("  ⚠  Invalid input. Please enter a number.")

selected_file = report_files[choice - 1]
selected_path = os.path.join(reports_dir, selected_file)

print(f"\n✅ Selected: {os.path.splitext(selected_file)[0]}\n")

# ── Read the selected medical report ─────────────
with open(selected_path, "r") as file:
    medical_report = file.read()

# ── Run AI Agents ────────────────────────────────
agents = {
    "Cardiologist": Cardiologist(medical_report),
    "Psychologist": Psychologist(medical_report),
    "Pulmonologist": Pulmonologist(medical_report)
}

# Function to run each agent and get their response
def get_response(agent_name, agent):
    response = agent.run()
    return agent_name, response

# Run the agents concurrently and collect responses
responses = {}
with ThreadPoolExecutor() as executor:
    futures = {executor.submit(get_response, name, agent): name for name, agent in agents.items()}
    
    for future in as_completed(futures):
        agent_name, response = future.result()
        responses[agent_name] = response

team_agent = MultidisciplinaryTeam(
    cardiologist_report=responses["Cardiologist"],
    psychologist_report=responses["Psychologist"],
    pulmonologist_report=responses["Pulmonologist"]
)

# ── Save Final Diagnosis ─────────────────────────
final_diagnosis = team_agent.run()

# Sanitize unicode characters to plain ASCII for readability
def sanitize_text(text):
    """Replace common unicode characters with ASCII equivalents."""
    replacements = {
        '\u2018': "'",   # left single quote
        '\u2019': "'",   # right single quote (apostrophe)
        '\u201c': '"',   # left double quote
        '\u201d': '"',   # right double quote
        '\u2013': '-',   # en dash
        '\u2014': '--',  # em dash
        '\u2026': '...', # ellipsis
        '\u2022': '-',   # bullet
        '\u00b7': '-',   # middle dot
        '\u2023': '-',   # triangular bullet
        '\u25cf': '-',   # black circle
        '\u25cb': '-',   # white circle
        '\u2192': '->',  # right arrow
    }
    for unicode_char, ascii_char in replacements.items():
        text = text.replace(unicode_char, ascii_char)
    return text

final_diagnosis_text = sanitize_text(final_diagnosis)

# Generate output filename based on the selected report
report_base_name = os.path.splitext(selected_file)[0]
txt_output_path = os.path.join("Results", f"diagnosis_{report_base_name}.txt")

# Ensure the directory exists
os.makedirs(os.path.dirname(txt_output_path), exist_ok=True)

# Write the final diagnosis to the text file (explicit UTF-8 encoding)
with open(txt_output_path, "w", encoding="utf-8") as txt_file:
    txt_file.write(final_diagnosis_text)

print(f"\n📄 Final diagnosis has been saved to: {txt_output_path}")

