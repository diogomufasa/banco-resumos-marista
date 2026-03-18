import base64
import mimetypes
import os
from typing import Tuple

from django.conf import settings
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
    "You are a content moderator for a Catholic school platform (Colégio Marista) where students upload study notes.\n\n"
    "TASK: Decide if the uploaded file content is appropriate for a school environment.\n\n"
    "MARK AS SAFE only if the content is clearly:\n"
    "- Academic study notes, summaries, worksheets, exercises, formulas, diagrams\n"
    "- School-related documents (tests, exams, answer keys, presentations, essays)\n"
    "- Educational images or charts\n\n"
    "MARK AS UNSAFE if the content:\n"
    "- Is completely unrelated to school/academic work (e.g. random files, games, personal media)\n"
    "- Contains pornographic or sexually explicit material\n"
    "- Contains explicit instructions to build weapons or commit crimes\n"
    "- Contains severe threats or encouragement of self-harm\n"
    "- Contains hate speech or targeted harassment\n\n"
    "If the file appears to be binary/unreadable but its filename and type suggest it is a school document, mark as SAFE.\n"
    "If the file appears to be binary/unreadable and has no clear academic context, mark as UNSAFE.\n\n"
    "OUTPUT: Reply with ONLY 'safe' or 'unsafe'. No explanation."
)

TEXT_PROMPT = (
    "You are a strict content moderator for a Catholic school platform (Colégio Marista) where students share study notes.\n\n"
    "TASK: Decide if the following username, name, or description is appropriate for a school environment.\n\n"
    "MARK AS UNSAFE if the text contains or embeds (even concatenated without spaces):\n"
    "- Portuguese or English profanity, slurs, or vulgar words (e.g. puta, caralho, merda, foda, pila, punheta, cona, cu, buceta, viado, etc.)\n"
    "- Sexual references or innuendo\n"
    "- Hate speech, insults, or targeted harassment\n"
    "- Threats or encouragement of self-harm\n"
    "- Drug/weapon references used inappropriately\n\n"
    "IMPORTANT: Words can be concatenated. Always check for embedded profanity.\n\n"
    "MARK AS SAFE if the text is:\n"
    "- A normal name, username, or academic description\n"
    "OUTPUT: Reply with ONLY 'safe' or 'unsafe'. No explanation."
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
    api_key = getattr(settings, 'GROQ_API_KEY',
                      None) or os.getenv("GROQ_API_KEY")
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
            model="openai/gpt-oss-safeguard-20b",
            messages=[
                {"role": "system", "content": PROMPT},
                {"role": "user", "content": content},
            ],
            temperature=0,
            max_tokens=128,
        )
    except Exception as exc:
        return False, f"Failed to connect to Groq: {exc}"

    message = (response.choices[0].message.content or "").strip()

    if not message:
        return True, ""

    normalized = message.lower()
    if normalized.startswith("safe"):
        return True, ""

    educ_keywords = (
        "exerc", "ficha", "resumo", "apont", "correc",
        "correção", "prova", "exame", "tp", "trabalho", "correcao",
    )
    filename = getattr(uploaded_file, "name", "") or ""
    if sample_kind == "base64" and any(k in filename.lower() for k in educ_keywords):
        return True, ""

    return False, f"Ficheiro marcado como inseguro: {message}"


def verify_text_with_groq(text: str, label: str = "texto") -> Tuple[bool, str]:
    """Verify arbitrary text (username, name, description) with Groq."""
    api_key = getattr(settings, 'GROQ_API_KEY',
                      None) or os.getenv("GROQ_API_KEY")
    if not api_key:
        return False, "Chave da API do Groq não encontrada. Configure GROQ_API_KEY."

    client = Groq(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": TEXT_PROMPT},
                {"role": "user", "content": f"{label}: {text[:500]}"},
            ],
            temperature=0,
            max_tokens=10,
        )
    except Exception as exc:
        return False, f"Falha ao contactar o Groq: {exc}"

    message = (response.choices[0].message.content or "").strip().lower()

    # Empty response = safe
    if not message:
        return True, ""

    if message.startswith("safe"):
        return True, ""

    return False, "Conteúdo contém linguagem inapropriada."
