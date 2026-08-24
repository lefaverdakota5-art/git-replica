"""Local, privacy-preserving image indexing and visual similarity matching.

The engine deliberately indexes only media explicitly uploaded to a project.  It
does not perform unrestricted network retrieval; a federated web retriever needs
separate provider credentials, rate limits, robots handling, and source terms.
"""

from __future__ import annotations

import hashlib
import io
import json
import math
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageOps, UnidentifiedImageError

MAX_IMAGE_BYTES = 25 * 1024 * 1024
MAX_IMAGE_PIXELS = 40_000_000
SUPPORTED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


class MediaValidationError(ValueError):
    """Raised when uploaded media is unsafe or cannot be decoded as an image."""


@dataclass(frozen=True)
class ImageFeatures:
    sha256: str
    perceptual_hash: str
    average_color: tuple[int, int, int]
    histogram: tuple[float, ...]
    width: int
    height: int


@dataclass(frozen=True)
class IndexedImage:
    id: str
    filename: str
    content_type: str
    stored_path: str
    indexed_at: str
    features: ImageFeatures


def _resampling_filter() -> Image.Resampling:
    return Image.Resampling.LANCZOS


def _perceptual_hash(image: Image.Image) -> str:
    """Return a 64-bit dHash resilient to modest resizing and JPEG artifacts."""
    grayscale = ImageOps.grayscale(image).resize((9, 8), _resampling_filter())
    pixels = list(grayscale.getdata())
    bits = 0
    for row in range(8):
        offset = row * 9
        for column in range(8):
            bits = (bits << 1) | int(pixels[offset + column] > pixels[offset + column + 1])
    return f"{bits:016x}"


def _histogram(image: Image.Image) -> tuple[float, ...]:
    reduced = image.resize((64, 64), _resampling_filter()).convert("RGB")
    bins = [0] * 24
    for red, green, blue in reduced.getdata():
        bins[red // 32] += 1
        bins[8 + green // 32] += 1
        bins[16 + blue // 32] += 1
    total = sum(bins)
    return tuple(value / total for value in bins) if total else tuple(0.0 for _ in bins)


def extract_features(data: bytes) -> ImageFeatures:
    """Decode one bounded image payload and calculate deterministic visual signals."""
    if not data:
        raise MediaValidationError("The uploaded file is empty.")
    if len(data) > MAX_IMAGE_BYTES:
        raise MediaValidationError("Images must be 25 MB or smaller.")
    try:
        with Image.open(io.BytesIO(data)) as source:
            source.verify()
        with Image.open(io.BytesIO(data)) as source:
            source.load()
            if source.width * source.height > MAX_IMAGE_PIXELS:
                raise MediaValidationError("Images must contain 40 million pixels or fewer.")
            image = ImageOps.exif_transpose(source).convert("RGB")
    except (UnidentifiedImageError, OSError, SyntaxError) as error:
        raise MediaValidationError("The upload is not a valid supported image.") from error

    pixels = list(image.resize((1, 1), _resampling_filter()).getdata())
    return ImageFeatures(
        sha256=hashlib.sha256(data).hexdigest(),
        perceptual_hash=_perceptual_hash(image),
        average_color=tuple(pixels[0]),
        histogram=_histogram(image),
        width=image.width,
        height=image.height,
    )


def hamming_similarity(left: str, right: str) -> float:
    if len(left) != len(right):
        return 0.0
    distance = (int(left, 16) ^ int(right, 16)).bit_count()
    return max(0.0, 1 - distance / (len(left) * 4))


def cosine_similarity(left: Iterable[float], right: Iterable[float]) -> float:
    left_values, right_values = tuple(left), tuple(right)
    numerator = sum(a * b for a, b in zip(left_values, right_values))
    left_length = math.sqrt(sum(a * a for a in left_values))
    right_length = math.sqrt(sum(b * b for b in right_values))
    if not left_length or not right_length:
        return 0.0
    return max(0.0, min(1.0, numerator / (left_length * right_length)))


def color_similarity(left: tuple[int, int, int], right: tuple[int, int, int]) -> float:
    distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(left, right)))
    return max(0.0, 1 - distance / (255 * math.sqrt(3)))


def compare_images(query: ImageFeatures, candidate: ImageFeatures) -> dict[str, object]:
    perceptual = hamming_similarity(query.perceptual_hash, candidate.perceptual_hash)
    histogram = cosine_similarity(query.histogram, candidate.histogram)
    color = color_similarity(query.average_color, candidate.average_color)
    exact = query.sha256 == candidate.sha256
    score = 1.0 if exact else 0.6 * perceptual + 0.3 * histogram + 0.1 * color
    if exact:
        category = "exact_duplicate"
    elif score >= 0.88:
        category = "near_duplicate"
    elif score >= 0.70:
        category = "visually_similar"
    else:
        category = "weak_similarity"
    return {
        "score": round(score * 100, 2),
        "category": category,
        "signals": {
            "perceptual": round(perceptual * 100, 2),
            "color_histogram": round(histogram * 100, 2),
            "average_color": round(color * 100, 2),
            "sha256_exact": exact,
        },
    }


class LocalImageIndex:
    """Small JSON-backed project-local index with atomically persisted metadata."""

    def __init__(self, project_directory: Path) -> None:
        self.root = project_directory / ".prometheus-media"
        self.media_directory = self.root / "images"
        self.index_path = self.root / "index.json"
        self.media_directory.mkdir(parents=True, exist_ok=True)

    def _read(self) -> list[IndexedImage]:
        if not self.index_path.exists():
            return []
        try:
            raw = json.loads(self.index_path.read_text(encoding="utf-8"))
            items = []
            for item in raw:
                feature_data = item.pop("features")
                feature_data["average_color"] = tuple(feature_data["average_color"])
                feature_data["histogram"] = tuple(feature_data["histogram"])
                items.append(IndexedImage(features=ImageFeatures(**feature_data), **item))
            return items
        except (json.JSONDecodeError, OSError, TypeError, KeyError) as error:
            raise MediaValidationError("The local media index is unreadable.") from error

    def _write(self, items: list[IndexedImage]) -> None:
        temporary_path = self.index_path.with_suffix(".tmp")
        temporary_path.write_text(json.dumps([asdict(item) for item in items], indent=2), encoding="utf-8")
        temporary_path.replace(self.index_path)

    def add(self, filename: str, content_type: str, data: bytes) -> IndexedImage:
        if content_type not in SUPPORTED_MIME_TYPES:
            raise MediaValidationError("Only JPEG, PNG, WebP, and GIF image uploads are supported.")
        features = extract_features(data)
        items = self._read()
        duplicate = next((item for item in items if item.features.sha256 == features.sha256), None)
        if duplicate:
            return duplicate
        image_id = hashlib.sha256(f"{features.sha256}:{filename}".encode()).hexdigest()[:24]
        suffix = Path(filename).suffix.lower() if Path(filename).suffix else ".img"
        stored_path = self.media_directory / f"{image_id}{suffix}"
        stored_path.write_bytes(data)
        item = IndexedImage(
            id=image_id,
            filename=Path(filename).name or "image",
            content_type=content_type,
            stored_path=str(stored_path.relative_to(self.root)),
            indexed_at=datetime.now(timezone.utc).isoformat(),
            features=features,
        )
        items.append(item)
        self._write(items)
        return item

    def search(self, data: bytes, limit: int = 20) -> list[dict[str, object]]:
        query = extract_features(data)
        results = []
        for item in self._read():
            comparison = compare_images(query, item.features)
            results.append({
                "id": item.id,
                "filename": item.filename,
                "indexed_at": item.indexed_at,
                "dimensions": {"width": item.features.width, "height": item.features.height},
                **comparison,
            })
        return sorted(results, key=lambda result: float(result["score"]), reverse=True)[:limit]
