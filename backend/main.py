from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI(title="Repair Genie API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten this in production
    allow_methods=["*"],
    allow_headers=["*"],
)

SYSTEM_PROMPT = """You are Repair Genie, a warm and expert appliance repair AI. Diagnose home appliance problems.

RULES:
- If you need more info to reach 90% confidence, ask ONE concise follow-up question at a time.
- Only output the final REPAIR_RESULT when you are at least 90% confident about root causes.
- When confident, output EXACTLY this block (nothing after it):

REPAIR_RESULT:
{"causes":[{"label":"Root cause description","probability":72},{"label":"Another cause","probability":18}],"safety":["Safety check 1","Safety check 2"],"steps":["Step 1: do this","Step 2: then this","Step 3: continue"]}

Probabilities must sum to ≤100. Include 1-4 causes, 2-4 safety items, 3-8 steps. Be warm, clear, and practical."""


class Message(BaseModel):
    role: str
    content: str


class DiagnoseRequest(BaseModel):
    messages: list[Message]


class DiagnoseResponse(BaseModel):
    reply: str
    is_result: bool
    result: Optional[dict] = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/diagnose", response_model=DiagnoseResponse)
async def diagnose(req: DiagnoseRequest):
    if not req.messages:
        raise HTTPException(status_code=400, detail="No messages provided")

    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SYSTEM_PROMPT,
        )

        # Convert messages to Gemini format
        # Gemini uses "user" and "model" roles (not "assistant")
        history = []
        for m in req.messages[:-1]:
            history.append({
                "role": "user" if m.role == "user" else "model",
                "parts": [m.content]
            })

        chat = model.start_chat(history=history)
        response = chat.send_message(req.messages[-1].content)
        reply = response.text

        # Check if it's a final diagnosis
        if "REPAIR_RESULT:" in reply:
            try:
                json_str = reply.split("REPAIR_RESULT:")[1].strip()
                result = json.loads(json_str)
                return DiagnoseResponse(reply=reply, is_result=True, result=result)
            except json.JSONDecodeError:
                pass

        return DiagnoseResponse(reply=reply, is_result=False)

    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Gemini API error: {str(e)}")
