"""
Cura3.ai — Chat Routes
Follow-up chat about a diagnosis.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from bson import ObjectId
from datetime import datetime, timezone
from app.core.database import get_database
from app.core.security import get_current_user
from app.services.chat_service import generate_chat_response

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/{diagnosis_id}")
async def send_message(
    diagnosis_id: str,
    message: str,
    current_user: dict = Depends(get_current_user),
):
    """Send a follow-up question about a diagnosis."""
    db = get_database()

    # Get the diagnosis for context
    try:
        diagnosis = await db.diagnoses.find_one({
            "_id": ObjectId(diagnosis_id),
            "user_id": current_user["_id"],
        })
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid diagnosis ID.")

    if not diagnosis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diagnosis not found.")

    # Build diagnosis context
    context_parts = []
    for sr in diagnosis.get("specialist_reports", []):
        context_parts.append(f"{sr['specialist_name']} Report:\n{sr['report_content']}")
    context_parts.append(f"\nFinal Diagnosis:\n{diagnosis.get('final_diagnosis', '')}")
    diagnosis_context = "\n\n".join(context_parts)

    # Get or create chat session
    chat_session = await db.chat_sessions.find_one({
        "diagnosis_id": diagnosis_id,
        "user_id": current_user["_id"],
    })

    if not chat_session:
        chat_session = {
            "user_id": current_user["_id"],
            "diagnosis_id": diagnosis_id,
            "messages": [],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        result = await db.chat_sessions.insert_one(chat_session)
        chat_session["_id"] = result.inserted_id

    chat_history = chat_session.get("messages", [])

    # Generate AI response
    ai_response = await generate_chat_response(
        diagnosis_context=diagnosis_context,
        chat_history=chat_history,
        user_message=message,
    )

    # Save messages to chat session
    now = datetime.now(timezone.utc)
    user_msg = {"role": "user", "content": message, "timestamp": now.isoformat()}
    assistant_msg = {"role": "assistant", "content": ai_response, "timestamp": now.isoformat()}

    await db.chat_sessions.update_one(
        {"_id": chat_session["_id"]},
        {
            "$push": {"messages": {"$each": [user_msg, assistant_msg]}},
            "$set": {"updated_at": now},
        },
    )

    return {
        "user_message": message,
        "ai_response": ai_response,
        "diagnosis_id": diagnosis_id,
    }


@router.get("/{diagnosis_id}")
async def get_chat_history(
    diagnosis_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get the chat history for a specific diagnosis."""
    db = get_database()

    chat_session = await db.chat_sessions.find_one({
        "diagnosis_id": diagnosis_id,
        "user_id": current_user["_id"],
    })

    if not chat_session:
        return {"diagnosis_id": diagnosis_id, "messages": [], "total": 0}

    return {
        "id": str(chat_session["_id"]),
        "diagnosis_id": diagnosis_id,
        "messages": chat_session.get("messages", []),
        "total": len(chat_session.get("messages", [])),
        "created_at": chat_session.get("created_at"),
        "updated_at": chat_session.get("updated_at"),
    }


@router.delete("/{diagnosis_id}")
async def delete_chat(
    diagnosis_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Delete the chat session for a specific diagnosis."""
    db = get_database()

    result = await db.chat_sessions.delete_one({
        "diagnosis_id": diagnosis_id,
        "user_id": current_user["_id"],
    })

    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found.")

    return {"message": "Chat session deleted successfully."}
