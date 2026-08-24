import io

from PIL import Image

from prometheus.backend.visual_search import LocalImageIndex, compare_images, extract_features


def image_bytes(color: tuple[int, int, int], size: tuple[int, int] = (32, 32)) -> bytes:
    image = Image.new("RGB", size, color)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_exact_image_is_classified_as_exact_duplicate():
    payload = image_bytes((12, 34, 56))

    result = compare_images(extract_features(payload), extract_features(payload))

    assert result["score"] == 100.0
    assert result["category"] == "exact_duplicate"
    assert result["signals"]["sha256_exact"] is True


def test_project_index_persists_and_returns_ranked_match(tmp_path):
    index = LocalImageIndex(tmp_path)
    first = index.add("navy.png", "image/png", image_bytes((10, 20, 80)))
    index.add("amber.png", "image/png", image_bytes((230, 160, 20)))

    results = index.search(image_bytes((10, 20, 80)))

    assert results[0]["id"] == first.id
    assert results[0]["category"] == "exact_duplicate"
    assert results[0]["score"] == 100.0


def test_index_deduplicates_identical_uploads(tmp_path):
    index = LocalImageIndex(tmp_path)
    payload = image_bytes((100, 110, 120))

    initial = index.add("initial.png", "image/png", payload)
    repeated = index.add("renamed.png", "image/png", payload)

    assert repeated.id == initial.id
    assert len(index.search(payload)) == 1
