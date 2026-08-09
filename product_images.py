"""Allow-listed, size-bounded marketplace thumbnail proxy and disk cache."""

from __future__ import annotations

import hashlib
import io
import os
from pathlib import Path
import threading
from urllib.parse import quote, unquote, urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from PIL import Image, UnidentifiedImageError


MAX_SOURCE_BYTES = 12 * 1024 * 1024
MAX_SOURCE_PIXELS = 40_000_000
THUMBNAIL_EDGE = 640
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
_locks: dict[str, threading.Lock] = {}
_locks_guard = threading.Lock()
Image.MAX_IMAGE_PIXELS = MAX_SOURCE_PIXELS


class ProductImageError(ValueError):
    pass


def _allowed_host(hostname: str) -> bool:
    hostname = hostname.casefold().rstrip(".")
    return hostname in {"ir.ozone.ru", "cdn1.ozone.ru"} or hostname.endswith(".wbbasket.ru")


def validate_source_url(source_url: str) -> str:
    source = str(source_url or "").strip()
    parsed = urlsplit(source)
    try:
        port = parsed.port
    except ValueError as error:
        raise ProductImageError("Источник изображения не разрешён.") from error
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or not _allowed_host(parsed.hostname)
        or parsed.username
        or parsed.password
        or port not in {None, 443}
    ):
        raise ProductImageError("Источник изображения не разрешён.")
    return source


def source_digest(source_url: str) -> str:
    return hashlib.sha256(validate_source_url(source_url).encode("utf-8")).hexdigest()


def thumbnail_url(source_url: str) -> str:
    source = validate_source_url(source_url)
    digest = source_digest(source)
    return f"/assets/product-thumbnails/{digest}.webp?source={quote(source, safe='')}"


def source_from_request(path: str, query: dict[str, list[str]]) -> str:
    filename = str(path or "").rsplit("/", 1)[-1]
    if not filename.endswith(".webp"):
        raise ProductImageError("Некорректный адрес миниатюры.")
    requested_digest = filename[:-5]
    source = unquote((query.get("source") or [""])[0])
    if len(requested_digest) != 64 or requested_digest != source_digest(source):
        raise ProductImageError("Подпись миниатюры не совпадает.")
    return source


class _SafeRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        target = urljoin(req.full_url, newurl)
        validate_source_url(target)
        return super().redirect_request(req, fp, code, msg, headers, target)


def _default_fetch(source_url: str) -> tuple[str, bytes]:
    request = Request(
        source_url,
        headers={"User-Agent": "ShagaemVmesteThumbnailProxy/1.0", "Accept": "image/webp,image/jpeg,image/png"},
    )
    with build_opener(_SafeRedirectHandler()).open(request, timeout=8) as response:
        content_type = str(response.headers.get_content_type()).casefold()
        declared = response.headers.get("Content-Length")
        if declared and int(declared) > MAX_SOURCE_BYTES:
            raise ProductImageError("Исходное изображение слишком большое.")
        body = response.read(MAX_SOURCE_BYTES + 1)
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise ProductImageError("Источник вернул неподдерживаемый формат.")
    if not body or len(body) > MAX_SOURCE_BYTES:
        raise ProductImageError("Исходное изображение пустое или слишком большое.")
    return content_type, body


def _render_webp(body: bytes) -> bytes:
    try:
        with Image.open(io.BytesIO(body)) as image:
            image.load()
            if image.width * image.height > MAX_SOURCE_PIXELS:
                raise ProductImageError("Исходное изображение имеет слишком большое разрешение.")
            image.thumbnail((THUMBNAIL_EDGE, THUMBNAIL_EDGE), Image.Resampling.LANCZOS)
            if image.mode not in {"RGB", "RGBA"}:
                image = image.convert("RGBA" if "transparency" in image.info else "RGB")
            output = io.BytesIO()
            image.save(output, format="WEBP", quality=82, method=4)
            return output.getvalue()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as error:
        raise ProductImageError("Не удалось декодировать изображение.") from error


def cache_root() -> Path:
    configured = os.environ.get("PRODUCT_THUMBNAIL_CACHE_DIR", "").strip()
    if configured:
        return Path(configured)
    return Path(os.environ.get("DB_DIR", ".")) / "cache" / "product-thumbnails"


def get_thumbnail(source_url: str, *, root: Path | None = None, fetcher=None) -> bytes:
    source = validate_source_url(source_url)
    digest = source_digest(source)
    directory = root or cache_root()
    destination = directory / f"{digest}.webp"
    if destination.is_file():
        return destination.read_bytes()
    with _locks_guard:
        lock = _locks.setdefault(digest, threading.Lock())
    with lock:
        if destination.is_file():
            return destination.read_bytes()
        _content_type, body = (fetcher or _default_fetch)(source)
        thumbnail = _render_webp(body)
        directory.mkdir(parents=True, exist_ok=True)
        temporary = directory / f".{digest}.{threading.get_ident()}.tmp"
        temporary.write_bytes(thumbnail)
        os.chmod(temporary, 0o600)
        os.replace(temporary, destination)
        return thumbnail
