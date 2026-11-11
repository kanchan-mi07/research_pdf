
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.vector_service import search_document
from app.services.llm_service import generate_answer, LLMUnavailableError
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session


from app.database.connection import get_db
from app.database.models import User, Document, ChatMessage
from app.utils.security import get_current_user

router = APIRouter()


class ChatRequest(BaseModel):
    document_id: str
    question: str = Field(min_length=1, max_length=4000)


@router.post("/ask")
def ask_question(request: ChatRequest):

    try:
        question = request.question.strip()

        if not question:
            raise HTTPException(
                status_code=400,
                detail="Question cannot be empty"
            )

        # Step 1: Retrieve relevant PDF chunks from FAISS.
        retrieved_chunks = search_document(
            request.document_id,
            question,
            top_k=4
        )

        if not retrieved_chunks:
            return {
                "answer": "I could not find relevant information in this document.",
                "sources": []
            }

        # Step 2: Generate answer using Gemini.
        answer = generate_answer(
            question,
            retrieved_chunks
        )

        # Step 3: Prepare page references.
        sources = [
            {"page": chunk["page"]}
            for chunk in retrieved_chunks
        ]

        # Remove duplicate page references.
        sources = list({
            source["page"]: source
            for source in sources
        }.values())

        return {
            "answer": answer,
            "sources": sources
        }

    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    except LLMUnavailableError as error:
        raise HTTPException(status_code=503, detail=str(error))

    except Exception as error:
        print("Chat error:", str(error))
        raise HTTPException(
            status_code=500,
            detail="Unable to generate an answer. Check the backend logs."
        )
def get_user_document(db, document_id, user):
    doc = db.query(Document).filter(
        Document.id == document_id, Document.user_id == user.id
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.post("/ask")
def ask_question(
    request: ChatRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    get_user_document(db, request.document_id, user)   # ownership check
    question = request.question.strip()

    try:
        retrieved_chunks = search_document(request.document_id, question, top_k=4)

        if not retrieved_chunks:
            answer, sources = "I could not find relevant information in this document.", []
        else:
            answer = generate_answer(question, retrieved_chunks)
            sources = list({c["page"]: {"page": c["page"]} for c in retrieved_chunks}.values())

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except LLMUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        print("Chat error:", str(e))
        raise HTTPException(status_code=500, detail="Unable to generate an answer.")

    # Save both messages only after the answer succeeded
    db.add_all([
        ChatMessage(document_id=request.document_id, user_id=user.id,
                    role="user", content=question),
        ChatMessage(document_id=request.document_id, user_id=user.id,
                    role="assistant", content=answer, sources=sources),
    ])
    db.commit()

    return {"answer": answer, "sources": sources}


@router.get("/history/{document_id}")
def get_history(
    document_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    get_user_document(db, document_id, user)

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.document_id == document_id)
        .order_by(ChatMessage.created_at)
        .all()
    )
    return [
        {"role": m.role, "content": m.content, "sources": m.sources or []}
        for m in messages
    ]