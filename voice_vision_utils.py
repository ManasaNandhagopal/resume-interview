"""
Minimal voice and vision utilities.
This restores the interface used by the frontend but does not provide real
functionality.  Real implementations originally used pyttsx3, SpeechRecognition,
OpenCV, and DeepFace; here we stub out methods to avoid import errors.
"""

import os
import time

# ----------------------------
# Text-to-Speech Engine Stub
# ----------------------------
class _TTS:
    def __init__(self):
        self.engine = None
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
        except Exception as e:
            # if the import or init fails, leave engine None and log
            print(f"⚠️ TTS initialization failed: {e}")

    def speak(self, text: str):
        if self.engine:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"⚠️ TTS speak error: {e}")
        else:
            # fallback: print to console
            print(f"[TTS] {text}")

    def is_available(self) -> bool:
        """Return True if a real TTS engine is loaded."""
        return self.engine is not None

tts_engine = _TTS()

# ----------------------------
# Speech-to-Text Engine Stub
# ----------------------------
class _STT:
    def __init__(self):
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            self.sr = sr
        except Exception:
            self.recognizer = None
            self.sr = None

    def listen_from_microphone(self, timeout: int = 10) -> str:
        if not self.recognizer or not self.sr:
            return ""
        with self.sr.Microphone() as source:
            audio = self.recognizer.listen(source, timeout=timeout)
        try:
            return self.recognizer.recognize_google(audio)
        except Exception:
            return ""

stt_engine = _STT()

# ----------------------------
# Emotion Analyzer Stub
# ----------------------------
class _EmotionAnalyzer:
    def analyze_emotion(self, image_path: str) -> dict:
        # a real implementation would use DeepFace or similar
        return {"dominant_emotion": "neutral", "confidence": 0.0}

    def verify_face(self, stored_pic: str, new_pic: str) -> dict:
        # stub always returns unverified
        return {"verified": False}

emotion_analyzer = _EmotionAnalyzer()

# ----------------------------
# Webcam Tracker Stub
# ----------------------------
class _WebcamTracker:
    def capture_frame(self, dest_path: str) -> bool:
        # Attempt to grab a frame using OpenCV if available
        try:
            import cv2
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            cap.release()
            if ret:
                cv2.imwrite(dest_path, frame)
                return True
        except Exception:
            pass
        # fallback: create empty file
        with open(dest_path, "wb") as f:
            f.write(b"")
        return False

webcam_tracker = _WebcamTracker()
