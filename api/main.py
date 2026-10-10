# -*- coding: utf-8 -*-
"""API FastAPI : serveur pour l'interface d'entretien."""

import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from interview.engine import RHInterviewEngine
from voice.tts import synthesize
from voice.stt import transcribe

app = FastAPI()

# Sessions en mémoire : {session_id: engine}
SESSIONS = {}

# Dossier pour les audios générés
AUDIO_DIR = ROOT / "api" / "audio"
AUDIO_DIR.mkdir(exist_ok=True)


# ---------- Modèles de requête ----------

class StartRequest(BaseModel):
    profile: str = "Software Engineer"
    n_standard: int = 5
    n_random: int = 0


class AnswerRequest(BaseModel):
    text: str


# ---------- Helpers ----------

def _make_audio(session_id, q_num, text, lang="en"):
    """
    Génère l'audio d'une question.
    Retourne (nom_fichier, media_type) ou (None, None) si échec.
    """
    base = f"{session_id}_q{q_num}"
    # On demande d'abord un .wav (pyttsx3)
    audio_path = AUDIO_DIR / f"{base}.wav"
    result = synthesize(text, audio_path, lang=lang)

    if result is None:
        return None, None

    result = Path(result)
    media = "audio/wav" if result.suffix.lower() == ".wav" else "audio/mpeg"
    return result.name, media


# ---------- Routes ----------

@app.post("/sessions")
def start_session(req: StartRequest):
    session_id = str(uuid.uuid4())
    engine = RHInterviewEngine(
        profile=req.profile,
        n_standard=req.n_standard,
        n_random=req.n_random,
    )
    SESSIONS[session_id] = engine

    question = engine.get_next_question()
    if question is None:
        raise HTTPException(500, "Aucune question disponible")

    audio_name, _ = _make_audio(session_id, 1, question["question"], lang="en")

    return {
        "session_id": session_id,
        "question_id": question["id"],
        "question": question["question"],
        "audio_url": f"/audio/{audio_name}" if audio_name else None,
    }


@app.post("/sessions/{session_id}/answers")
def submit_answer(session_id: str, req: AnswerRequest):
    if session_id not in SESSIONS:
        raise HTTPException(404, "Session inconnue")

    eng = SESSIONS[session_id]
    current = eng.get_next_question()
    if current is None:
        raise HTTPException(400, "Entretien terminé")

    evaluation = eng.submit_answer(current, req.text)

    next_question = eng.get_next_question()
    if next_question is None:
        return {
            "finished": True,
            "evaluation": evaluation,
            "next_question": None,
            "audio_url": None,
        }

    q_num = len(eng.history) + 1
    audio_name, _ = _make_audio(session_id, q_num, next_question["question"], lang="en")

    return {
        "finished": False,
        "evaluation": evaluation,
        "next_question": {
            "id": next_question["id"],
            "question": next_question["question"],
        },
        "audio_url": f"/audio/{audio_name}" if audio_name else None,
    }


@app.post("/sessions/{session_id}/audio")
async def submit_audio(session_id: str, file: UploadFile = File(...)):
    if session_id not in SESSIONS:
        raise HTTPException(404, "Session inconnue")

    suffix = Path(file.filename or "audio.webm").suffix or ".webm"
    tmp = ROOT / "voice" / f"uploaded{suffix}"
    tmp.parent.mkdir(parents=True, exist_ok=True)

    content = await file.read()
    with open(tmp, "wb") as f:
        f.write(content)

    try:
        text = transcribe(tmp, language="en")
    except Exception as e:
        raise HTTPException(500, f"Erreur de transcription : {e}")

    if not text:
        raise HTTPException(400, "Transcription vide")

    eng = SESSIONS[session_id]
    current = eng.get_next_question()
    if current is None:
        raise HTTPException(400, "Entretien terminé")

    evaluation = eng.submit_answer(current, text)

    next_question = eng.get_next_question()
    if next_question is None:
        return {
            "finished": True,
            "evaluation": evaluation,
            "next_question": None,
            "audio_url": None,
            "transcript": text,
        }

    q_num = len(eng.history) + 1
    audio_name, _ = _make_audio(session_id, q_num, next_question["question"], lang="en")

    return {
        "finished": False,
        "evaluation": evaluation,
        "next_question": {
            "id": next_question["id"],
            "question": next_question["question"],
        },
        "audio_url": f"/audio/{audio_name}" if audio_name else None,
        "transcript": text,
    }


@app.get("/sessions/{session_id}/report")
def get_report(session_id: str):
    if session_id not in SESSIONS:
        raise HTTPException(404, "Session inconnue")
    return SESSIONS[session_id].get_report()


@app.get("/audio/{name}")
def get_audio(name: str):
    path = AUDIO_DIR / name
    if not path.exists():
        raise HTTPException(404, "Audio introuvable")
    media = "audio/wav" if path.suffix.lower() == ".wav" else "audio/mpeg"
    return FileResponse(path, media_type=media)


# Sert la page HTML statique (DOIT être en dernier)
app.mount("/", StaticFiles(directory=ROOT / "api" / "static", html=True), name="static")