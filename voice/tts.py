# -*- coding: utf-8 -*-
"""Text-to-Speech : voix Windows locale (pas de Microsoft, pas de 403)."""

import os
import subprocess
import sys
from pathlib import Path

import pyttsx3


def synthesize(text, dest_path, lang="en"):
    """
    Génère un fichier WAV avec la voix Windows.
    Retourne le chemin du fichier créé, ou None si échec.
    """
    dest_path = Path(dest_path).with_suffix(".wav")
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        engine = pyttsx3.init()

        # Choisir une voix selon la langue
        wanted = "french" if lang != "en" else "english"
        for v in engine.getProperty("voices"):
            name = (v.name or "").lower()
            langs = str(getattr(v, "languages", "")).lower()
            if wanted in name or wanted[:2] in langs:
                engine.setProperty("voice", v.id)
                break

        # Un peu plus lent pour un ton "interviewer"
        engine.setProperty("rate", 165)

        engine.save_to_file(text, str(dest_path))
        engine.runAndWait()
        return dest_path
    except Exception as e:
        print(f"[tts] échec : {e}")
        return None


def play(path):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {path}")
    if sys.platform.startswith("win"):
        os.startfile(str(path))
    elif sys.platform == "darwin":
        subprocess.run(["afplay", str(path)])
    else:
        subprocess.run(["xdg-open", str(path)])


def speak(text, lang="en", dest_path="voice/output.wav"):
    path = synthesize(text, dest_path, lang=lang)
    if path:
        play(path)
    return path


if __name__ == "__main__":
    print("Test TTS...")
    result = speak("Hello, I am your interviewer.")
    print("Résultat :", result)