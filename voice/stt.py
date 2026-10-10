# -*- coding: utf-8 -*-
"""Speech-to-Text : transcrire ta voix en texte."""

from pathlib import Path

import sounddevice as sd
import soundfile as sf
from faster_whisper import WhisperModel

SAMPLE_RATE = 16000
_MODEL = None


def _get_model():
    global _MODEL
    if _MODEL is None:
        _MODEL = WhisperModel("base", device="cpu", compute_type="int8")
    return _MODEL


def record(duration=8, samplerate=SAMPLE_RATE):
    print(f"🎤 Enregistrement pendant {duration} secondes... parle maintenant.")
    audio = sd.rec(
        int(duration * samplerate),
        samplerate=samplerate,
        channels=1,
        dtype="float32",
    )
    sd.wait()
    print("✅ Enregistrement terminé.")
    return audio


def save_wav(audio, path, samplerate=SAMPLE_RATE):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), audio, samplerate)
    return path


def transcribe(path, language="en"):
    model = _get_model()
    segments, info = model.transcribe(str(path), language=language)
    text = " ".join(seg.text.strip() for seg in segments).strip()
    return text


def listen_and_transcribe(duration=8, language="en"):
    audio = record(duration=duration)
    path = save_wav(audio, "voice/last_answer.wav")
    print("🔄 Transcription en cours...")
    text = transcribe(path, language=language)
    return text


if __name__ == "__main__":
    print("Test STT (parle en anglais après le signal)")
    text = listen_and_transcribe(duration=6)
    print(f"📝 Tu as dit : {text}")