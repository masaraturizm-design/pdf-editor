import json, logging
from groq import Groq
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a PDF editing assistant. Return actions as a JSON array only.
Action types:
- {"type": "replace_text", "find": "old", "replace": "new"}
- {"type": "increase_prices", "percent": 10}
- {"type": "decrease_prices", "percent": 10}
- {"type": "add_text", "text": "text to add"}
Understand Turkish commands too."""

class AIInterpreter:
    def __init__(self, groq_key, openai_key=None):
        self.openai_key = openai_key
        self.client = Groq(api_key=groq_key) if groq_key else None

    def interpret_command(self, pdf_text, command, ocr_text=""):
        msg = f"PDF:\n{pdf_text[:3000]}\n\n{('OCR: '+ocr_text[:500]) if ocr_text else ''}\n\nCommand: {command}\n\nReturn JSON array."
        if self.client:
            try:
                r = self.client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":msg}],
                    temperature=0.1, max_tokens=500)
                c = r.choices[0].message.content.strip()
                s, e = c.find('['), c.rfind(']')+1
                if s>=0 and e>s: return json.loads(c[s:e])
            except Exception as ex: logger.error(f"Groq: {ex}")
        if self.openai_key:
            try:
                import openai
                r = openai.OpenAI(api_key=self.openai_key).chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":msg}],
                    temperature=0.1, max_tokens=500)
                c = r.choices[0].message.content.strip()
                s, e = c.find('['), c.rfind(']')+1
                if s>=0 and e>s: return json.loads(c[s:e])
            except Exception as ex: logger.error(f"OpenAI: {ex}")
        return self._simple_parse(command)

    def _simple_parse(self, command):
        import re
        cl = command.lower()
        m = re.search(r'(\d+)\s*%', command)
        if m:
            pct = int(m.group(1))
            if any(w in cl for w in ["artir","artır","zam","increase"]): return [{"type":"increase_prices","percent":pct}]
            if any(w in cl for w in ["indir","düşür","decrease"]): return [{"type":"decrease_prices","percent":pct}]
        return []

    def transcribe_audio(self, audio_path):
        if not self.client: return ""
        try:
            with open(audio_path,"rb") as f:
                return self.client.audio.transcriptions.create(model="whisper-large-v3-turbo",file=f,language="tr").text
        except Exception as ex: logger.error(f"Transcribe: {ex}"); return ""
