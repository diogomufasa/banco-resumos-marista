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
    "Classifique se um arquivo pode ser partilhado dentro de uma plataforma de"
    " resumos escolares (ensino básico e secundário).\n"
    "Analise o nome e o conteúdo. Não aceites se tiver em branco\n"
    "Se o conteúdo for seguro responda apenas 'safe'.\n"
    "Se o conteúdo violar alguma categoria da taxonomy do Llama Guard, responda"
    " 'unsafe\\n<categoria>'."
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
        f"Arquivo: {uploaded_file.name}\n"
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

    return False, f"Arquivo marcado como inseguro: {message}"
