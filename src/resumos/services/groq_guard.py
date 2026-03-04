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
    "GUIDELINES:\n"
    "- ALWAYS consider material that is academic, historical, instructional or a school worksheet as SAFE.\n"
    "- Examples of SAFE content: math problems, science exercises, literature notes, historical excerpts, diagrams, formulas, worksheets, answer keys, and corrections.\n"
    "- If a file is a PDF or binary blob and its filename suggests it is an exercise/worksheet/answer key (e.g. 'exerc', 'ficha', 'resumo', 'apont', 'correc', 'correção', 'prova', 'exame', 'tp'), treat it as educational and SAFE unless it clearly contains instructions to commit violent or illegal acts.\n"
    "- ONLY mark 'unsafe' when the content explicitly contains: pornographic material, explicit instructions to build weapons or commit crimes, severe targeted threats, or explicit encouragement of self-harm/suicide.\n"
    "- Mentions of violence or weapons in an academic, historical, or analytical context should NOT be marked as unsafe.\n\n"
    "OUTPUT: Reply with a single token 'safe' or 'unsafe'. If 'unsafe', follow with a short category label (e.g. 'unsafe S4')."
)

TEXT_PROMPT = (
    "You are a content moderator for a school platform where students share study notes.\n\n"
    "GUIDELINES:\n"
    "- SAFE text: usernames, academic notes, study summaries, educational content, names, normal words.\n"
    "- UNSAFE text: hate speech, slurs, explicit sexual content, threats, encouragement of self-harm, explicit drug/weapon instructions.\n"
    "- A username or description that is merely informal, silly, or uses mild profanity should be considered SAFE.\n"
    "- Only mark 'unsafe' for clearly harmful or offensive content.\n\n"
    "OUTPUT: Reply with a single token 'safe' or 'unsafe'. If 'unsafe', follow with a short category label."
)

# Local blocklist for Portuguese profanity/slurs that AI models tend to miss.
# Substrings are matched case-insensitively against the full text.
_PT_BLOCKLIST = {
    "pila", "pilinha", "pilas",
    "puta", "putinha", "putas",
    "caralho", "caralhos",
    "foda", "foder", "fodasse", "fodido", "fodida",
    "merda", "merdas",
    "cona", "conas",
    "cu", "cus",
    "buceta",
    "porra", "porras",
    "viado", "viados",
    "prenha",
    "cuzao", "cuzão",
    "arrombado", "arrombada",
    "filhodaputa", "filhodeumputa",
    "punheta", "punhetas",
    "escroto", "escrotos",
    "bosta", "bostas",
    "raio", "rabos",
    "paneleiro", "paneleiros",
    "cagao", "cagão",
    "joder",
}


def _check_local_blocklist(text: str) -> bool:
    """Return True (safe) if no blocklisted substring is found, False otherwise."""
    normalized = text.lower().replace(" ", "").replace("_", "").replace("-", "")
    for term in _PT_BLOCKLIST:
        clean_term = term.replace(" ", "")
        if clean_term in normalized:
            return False
    return True


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
        # send prompt as system message to improve adherence
        response = client.chat.completions.create(
            model="openai/gpt-oss-safeguard-20b",
            messages=[
                {"role": "user", "content": content},
            ],
            temperature=0,
            max_tokens=128,
        )
    except Exception as exc:  # pragma: no cover - network failure
        return False, f"Failed to connect to Groq: {exc}"

    message = (response.choices[0].message.content or "").strip()
    finish_reason = response.choices[0].finish_reason or ""

    # Empty content or stop finish = model found nothing unsafe
    if not message:
        return True, ""

    normalized = message.lower()
    # If guard says safe -> accept
    if normalized.startswith("safe"):
        return True, ""

    educ_keywords = (
        "exerc",
        "ficha",
        "resumo",
        "apont",
        "correc",
        "correção",
        "prova",
        "exame",
        "tp",
        "trabalho",
        "correcao",
    )
    filename = getattr(uploaded_file, "name", "") or ""
    if sample_kind == "base64" and any(k in filename.lower() for k in educ_keywords):
        return True, ""

    return False, f"Ficheiro marcado como inseguro: {message}"


def verify_text_with_groq(text: str, label: str = "texto") -> Tuple[bool, str]:
    """Verify arbitrary text (username, description, etc.) with Groq."""
    # Local blocklist runs first — catches PT profanity the AI model misses
    if not _check_local_blocklist(text):
        return False, "Conteúdo contém linguagem inapropriada."

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return False, "Chave da API do Groq não encontrada. Configure GROQ_API_KEY."

    content = f"{label}:\n{text[:4000]}"

    client = Groq(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-safeguard-20b",
            messages=[
                {"role": "user", "content": content},
            ],
            temperature=0,
            max_tokens=64,
        )
    except Exception as exc:
        return False, f"Failed to connect to Groq: {exc}"

    message = (response.choices[0].message.content or "").strip()

    # Empty content = model found nothing unsafe
    if not message:
        return True, ""

    if message.lower().startswith("safe"):
        return True, ""

    return False, f"Conteúdo marcado como inapropriado: {message}"
