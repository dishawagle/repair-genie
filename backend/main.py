from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI(title="Repair Genie API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SYSTEM_PROMPT = """You are Repair Genie, an expert appliance repair AI. Diagnose home appliance problems.

CONVERSATION FLOW:
- Ask at most 2 follow-up questions to clarify the issue. Ask ONE at a time.
- After at most 2 rounds of follow-up, you MUST output REPAIR_RESULT.
- Never keep asking questions without eventually producing a diagnosis.

CRITICAL OUTPUT RULE:
When ready to diagnose, output REPAIR_RESULT IMMEDIATELY with absolutely NO preamble, NO intro sentence, NO "Here is my diagnosis", NO "Based on what you told me" — nothing before it. Jump straight to REPAIR_RESULT. The JSON must be on a single line.

REPAIR_RESULT:
{"causes":[{"label":"Root cause","probability":72},{"label":"Another cause","probability":20}],"safety":["Safety check 1","Safety check 2"],"diy_possible":true,"diy_steps":["Step 1","Step 2","Step 3"],"diy_note":"","needs_contractor":false,"contractor_reason":""}

JSON RULES:
- causes: 1-4 items, probabilities sum to ≤100
- safety: 2-5 checks the user MUST do before touching anything
- diy_steps: 3-8 clear steps written for a non-technical homeowner
- diy_possible: set false if fix involves gas lines, internal wiring, or sealed refrigerant; explain in diy_note
- needs_contractor: set true if a professional is required; explain in contractor_reason
- All fields must be present, use empty string "" if not applicable
- Do NOT wrap JSON in markdown code fences"""


class Message(BaseModel):
    role: str
    content: str


class DiagnoseRequest(BaseModel):
    messages: list[Message]


class DiagnoseResponse(BaseModel):
    reply: str
    is_result: bool
    result: Optional[dict] = None


import re as _re

def strip_html(text: str) -> str:
    """Remove any HTML tags Gemini may have accidentally included."""
    return _re.sub(r'<[^>]+>', '', text).strip()

def clean_result(result: dict) -> dict:
    """Strip HTML tags from all string fields in the result."""
    for item in result.get("causes", []):
        if isinstance(item.get("label"), str):
            item["label"] = strip_html(item["label"])
    for key in ("safety", "diy_steps"):
        result[key] = [strip_html(s) for s in result.get(key, [])]
    for key in ("diy_note", "contractor_reason"):
        if isinstance(result.get(key), str):
            result[key] = strip_html(result[key])
    return result


def extract_json_object(text: str) -> Optional[dict]:
    """Extract the first complete JSON object from a string."""
    start = text.find("{")
    if start == -1:
        return None
    brace_count, end_idx = 0, 0
    for i, ch in enumerate(text[start:], start):
        if ch == "{": brace_count += 1
        elif ch == "}": brace_count -= 1
        if brace_count == 0 and i > start:
            end_idx = i + 1
            break
    if not end_idx:
        return None
    try:
        return json.loads(text[start:end_idx])
    except json.JSONDecodeError:
        return None


def try_parse_result(reply: str) -> Optional[dict]:
    """
    Try multiple strategies to extract a REPAIR_RESULT JSON from Gemini's reply.
    Handles: REPAIR_RESULT: prefix, raw JSON, ```json fences, mixed preamble text.
    """
    required_keys = {"causes", "safety", "diy_steps", "diy_possible", "needs_contractor"}

    # Strategy 1: Look for REPAIR_RESULT: marker
    if "REPAIR_RESULT:" in reply:
        after = reply.split("REPAIR_RESULT:")[1].strip()
        after = after.strip("` \n")
        if after.startswith("json"):
            after = after[4:].strip()
        result = extract_json_object(after)
        if result and required_keys.issubset(result.keys()):
            return clean_result(result)

    # Strategy 2: Find any JSON object in the reply that has the required keys
    result = extract_json_object(reply)
    if result and required_keys.issubset(result.keys()):
        return clean_result(result)

    # Strategy 3: Strip markdown fences and try again
    clean = reply.replace("```json", "").replace("```", "").strip()
    result = extract_json_object(clean)
    if result and required_keys.issubset(result.keys()):
        return clean_result(result)

    return None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/diagnose", response_model=DiagnoseResponse)
async def diagnose(req: DiagnoseRequest):
    if not req.messages:
        raise HTTPException(status_code=400, detail="No messages provided")

    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=SYSTEM_PROMPT,
            generation_config=genai.GenerationConfig(max_output_tokens=8192),
        )

        # Convert messages to Gemini format (Gemini uses "model" not "assistant")
        history = []
        for m in req.messages[:-1]:
            history.append({
                "role": "user" if m.role == "user" else "model",
                "parts": [m.content]
            })

        chat = model.start_chat(history=history)
        response = chat.send_message(req.messages[-1].content)
        reply = response.text

        # Try to parse REPAIR_RESULT — handles multiple formats Gemini might output
        result = try_parse_result(reply)
        if result:
            return DiagnoseResponse(reply=reply, is_result=True, result=result)

        return DiagnoseResponse(reply=reply, is_result=False)

    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Gemini API error: {str(e)}")
