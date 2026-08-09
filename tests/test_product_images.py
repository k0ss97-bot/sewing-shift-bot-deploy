from __future__ import annotations

import io
from pathlib import Path
import tempfile
import unittest

from PIL import Image

from product_images import (
    ProductImageError,
    get_thumbnail,
    source_digest,
    source_from_request,
    thumbnail_url,
    validate_source_url,
)


class ProductImageTests(unittest.TestCase):
    def test_only_marketplace_https_hosts_are_allowed(self):
        allowed = [
            "https://ir.ozone.ru/s3/a.jpg",
            "https://cdn1.ozone.ru/a.png",
            "https://basket-01.wbbasket.ru/a.webp",
        ]
        for source in allowed:
            self.assertEqual(validate_source_url(source), source)
        for source in (
            "http://ir.ozone.ru/a.jpg",
            "https://ir.ozone.ru.evil.example/a.jpg",
            "https://127.0.0.1/a.jpg",
            "https://user@cdn1.ozone.ru/a.jpg",
        ):
            with self.assertRaises(ProductImageError):
                validate_source_url(source)

    def test_thumbnail_address_binds_hash_to_source(self):
        source = "https://ir.ozone.ru/s3/product.jpg"
        url = thumbnail_url(source)
        path, query_string = url.split("?", 1)
        query = {"source": [query_string.split("=", 1)[1]]}
        self.assertEqual(source_from_request(path, query), source)
        with self.assertRaises(ProductImageError):
            source_from_request(path.replace(source_digest(source), "0" * 64), query)

    def test_large_source_is_resized_to_cached_webp(self):
        source = "https://cdn1.ozone.ru/product.jpg"
        original = io.BytesIO()
        Image.new("RGB", (1600, 900), "red").save(original, format="JPEG")
        calls = []

        def fetcher(url):
            calls.append(url)
            return "image/jpeg", original.getvalue()

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = get_thumbnail(source, root=root, fetcher=fetcher)
            second = get_thumbnail(source, root=root, fetcher=lambda _url: self.fail("cache miss"))
            with Image.open(io.BytesIO(first)) as thumbnail:
                self.assertLessEqual(max(thumbnail.size), 640)
                self.assertEqual(thumbnail.format, "WEBP")

        self.assertEqual(first, second)
        self.assertEqual(calls, [source])


if __name__ == "__main__":
    unittest.main()
