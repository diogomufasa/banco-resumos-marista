import base64
import mimetypes
import os
from typing import Tuple

from django.core.files.uploadedfile import UploadedFile
from groq import Groq

MAX_BYTES = 200_000
TEXT_TYPES = {
    "application/json",
    "application/javascript",
    "application/xml",
    "application/x-yaml",
    "application/x-sh",
    "application/x-python-code",
}
PROMPT = (
    "You are reviewing educational materials for a school platform. Students share study resources.\n\n"
    "ALWAYS mark as 'safe':\n"
    "- ALL educational content (math, science, history, literature, etc.)\n"
    "- Study guides, worksheets, practice problems, assignments\n"
    "- Academic texts with student names, dates, school information\n"
    "- Educational diagrams, formulas, graphs, tables\n"
    "- ANY content related to learning and school subjects\n"
    "- Educational health topics (first aid, wellbeing, safety)\n"
    "- Mentions of injury/illness in an academic or historical context\n"
    "- Historical descriptions of wars, conflicts, or injuries when presented as study material\n"
    "- References to weapons or attacks inside historical/academic exercises (these are SAFE)\n\n"
    "Mark as 'unsafe' ONLY if you find explicit, direct content such as:\n"
    "- Pornographic images or explicit sexual content\n"
    "- Instructions to build weapons or commit crimes\n"
    "- Severe threats or hate speech targeting individuals\n"
    "- Encouragement or instructions for self-harm or suicide\n\n"
    "Violence classification: Do NOT flag as unsafe if the mention is educational, historical, or academic.\n"
    "Only flag S4 if the text celebrates, encourages, or instructs violence in a non-educational way.\n\n"
    "Self-harm classification: Do NOT flag as unsafe if the context is educational, informative, or historical.\n"
    "Only flag S8 if the text encourages, instructs, or urges self-harm.\n\n"
    "NOTE: School assignments may contain personal information (student names, dates) - this is NORMAL and SAFE.\n"
    "Privacy concerns do NOT apply to educational materials.\n\n"
    "Respond 'safe' for any educational or neutral content."
)


def _rewind(uploaded_file: UploadedFile) -> None:
    for stream in (getattr(uploaded_file, "file", None), uploaded_file):
        if stream is None:
            continue
        try:
            stream.seek(0)
        except (AttributeError, OSError):
            continue


def _extract_sample(uploaded_file: UploadedFile) -> bytes:
    _rewind(uploaded_file)
    stream = getattr(uploaded_file, "file", uploaded_file)
    try:
        data = stream.read(MAX_BYTES)
    except AttributeError:
        data = uploaded_file.read(MAX_BYTES)
    _rewind(uploaded_file)
    return data or b""


def _guess_mime(uploaded_file: UploadedFile) -> str:
    if getattr(uploaded_file, "content_type", None):
        return uploaded_file.content_type
    guess, _ = mimetypes.guess_type(uploaded_file.name)
    return guess or "application/octet-stream"


def _sample_to_text(sample: bytes, mime_type: str) -> Tuple[str, str]:
    is_textual = mime_type.startswith("text/") or mime_type in TEXT_TYPES
    kind = "texto"
    if is_textual:
        decoded = sample.decode("utf-8", errors="ignore") if sample else ""
        return decoded[:4000], kind
    kind = "base64"
    encoded = base64.b64encode(sample[:MAX_BYTES]).decode("ascii")
    return encoded[:4000], kind


def verify_file_with_groq(uploaded_file: UploadedFile) -> Tuple[bool, str]:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return False, "Chave da API do Groq não encontrada. Configure GROQ_API_KEY."

    sample = _extract_sample(uploaded_file)
    mime_type = _guess_mime(uploaded_file)
    sample_text, sample_kind = _sample_to_text(sample, mime_type)

    content = (
        f"Ficheiro: {uploaded_file.name}\n"
        f"Tamanho: {getattr(uploaded_file, 'size', len(sample))} bytes\n"
        f"MIME: {mime_type}\n"
        f"Amostra ({sample_kind}):\n{sample_text}"
    )

    client = Groq(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model="meta-llama/Llama-Guard-4-12B",
            messages=[{"role": "user", "content": f"{PROMPT}\n\n{content}"}],
            temperature=0,
            max_tokens=64,
        )
    except Exception as exc:  # pragma: no cover - network failure
        return False, f"Falha ao contactar o Groq: {exc}"

    message = (response.choices[0].message.content or "").strip()
    if not message:
        return False, "Resposta vazia da API Groq."

    normalized = message.lower()
    if normalized.startswith("safe"):
        return True, ""

    return False, f"Ficheiro marcado como inseguro: {message}"
