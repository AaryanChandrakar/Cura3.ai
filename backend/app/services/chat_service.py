"""
Cura3.ai — Follow-Up Chat Service
Provides context-aware follow-up chat about a diagnosis.
"""
from langchain_openai import ChatOpenAI
from app.config import settings
import os

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY

CHAT_SYSTEM_PROMPT = """
You are Cura3.ai, a medical AI assistant. You are helping a user understand
their medical diagnosis report.

CONTEXT - The following diagnosis was generated for the patient:
{diagnosis_context}

RULES:
1. Answer the user's questions based ONLY on the diagnosis and specialist reports provided above.
2. Use plain, easy-to-understand language. Avoid excessive medical jargon unless the user seems to be a medical professional.
3. Be helpful and empathetic. This is about someone's health.
4. Always remind users that this is AI-generated and they should consult a real doctor.
5. If the user asks something outside the scope of the diagnosis, politely redirect them.
6. Do NOT make up information not present in the reports.
7. Use plain ASCII text only, no markdown, no emojis, no special characters.
"""


async def generate_chat_response(
    diagnosis_context: str,
    chat_history: list[dict],
    user_message: str,
) -> str:
    """
    Generate a follow-up chat response based on diagnosis context.

    Args:
        diagnosis_context: The full diagnosis text (specialist reports + final)
        chat_history: Previous messages in the conversation
        user_message: The user's current question

    Returns:
        AI assistant's response text
    """
    system_prompt = CHAT_SYSTEM_PROMPT.format(diagnosis_context=diagnosis_context)

    # Build conversation messages
    messages = [{"role": "system", "content": system_prompt}]

    for msg in chat_history[-10:]:  # Keep last 10 messages for context window
        messages.append({
            "role": msg.get("role", "user"),
            "content": msg.get("content", ""),
        })

    messages.append({"role": "user", "content": user_message})

    model = ChatOpenAI(
        temperature=0.3,  # Slightly creative for conversational replies
        model="gpt-4.1",
    )

    try:
        # Build a single prompt from messages
        combined_prompt = system_prompt + "\n\n"
        for msg in messages[1:]:  # Skip system (already included)
            role_label = "Patient" if msg["role"] == "user" else "Cura3.ai"
            combined_prompt += f"{role_label}: {msg['content']}\n\n"
        combined_prompt += "Cura3.ai:"

        response = model.invoke(combined_prompt)
        content = response.content

        if isinstance(content, list):
            content = " ".join(
                item["text"] if isinstance(item, dict) and "text" in item else str(item)
                for item in content
            )

        return str(content).strip()

    except Exception as e:
        return f"I apologize, but I encountered an error processing your question. Please try again. (Error: {str(e)})"
