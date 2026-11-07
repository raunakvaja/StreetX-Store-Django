"""Read-only FakeStore catalog. No orders or payments are created."""
import json
import logging
import time
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from urllib.parse import urlsplit

import requests
from django.core.cache import cache
from django.shortcuts import render
from django.views.decorators.http import require_safe

logger = logging.getLogger(__name__)

API_URL = "https://fakestoreapi.com/products"
CACHE_KEY = "streetx:catalog:v1"

CATEGORIES = (
    ("men's clothing", "Men", "Everyday essentials"),
    ("women's clothing", "Women", "Your own silhouette"),
    ("jewelery", "Jewelry", "Details that speak"),
    ("electronics", "Electronics", "Plug into your world"),
)

PLACEHOLDER = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
    "viewBox='0 0 400 400'%3E"
    "%3Crect width='400' height='400' fill='%23eeeef0'/%3E"
    "%3Cpath d='M155 160v-25a45 45 0 0 1 90 0v25m-110 0h130l15 140H120z' "
    "fill='none' stroke='%23777080' stroke-width='7'/%3E"
    "%3Ctext x='200' y='350' text-anchor='middle' font-family='sans-serif' "
    "font-size='18' fill='%2355505c'%3EImage unavailable%3C/text%3E%3C/svg%3E"
)


def image_url(value):
    """Allow HTTPS images from FakeStoreAPI's own image directory."""
    if not isinstance(value, str) or len(value) > 1000:
        return ""

    try:
        parsed = urlsplit(value)

        if (
            parsed.scheme == "https"
            and parsed.hostname == "fakestoreapi.com"
            and parsed.port in (None, 443)
            and not parsed.username
            and not parsed.password
            and parsed.path.startswith("/img/")
            and not any(ord(character) < 33 for character in value)
        ):
            return value
    except ValueError:
        pass

    return ""


def clean_products(payload):
    if not isinstance(payload, list) or len(payload) > 100:
        raise ValueError("Invalid catalog shape")

    products = []
    seen = set()
    labels = {key: label for key, label, _ in CATEGORIES}

    for row in payload:
        if not isinstance(row, dict):
            continue

        product_id = row.get("id")
        title = row.get("title")
        category = row.get("category")

        if (
            type(product_id) is not int
            or not 0 < product_id < 1000000
            or product_id in seen
            or not isinstance(title, str)
            or not title.strip()
            or not isinstance(category, str)
            or category not in labels
        ):
            continue

        try:
            raw_price = row.get("price")

            if isinstance(raw_price, bool):
                continue

            price = Decimal(str(raw_price))

            if not price.is_finite() or not 0 <= price <= 1000000:
                continue

            price_cents = int(
                (price * 100).quantize(
                    Decimal("1"),
                    rounding=ROUND_HALF_UP,
                )
            )
        except (InvalidOperation, ValueError, TypeError):
            continue

        description = row.get("description", "")
        rating = row.get("rating")
        rating_text = "Not rated"

        if isinstance(rating, dict):
            try:
                rate = Decimal(str(rating.get("rate")))
                count = rating.get("count")

                if (
                    rate.is_finite()
                    and 0 <= rate <= 5
                    and type(count) is int
                    and 0 <= count <= 10000000
                ):
                    rating_text = f"{rate:.1f} / 5 · {count:,} ratings"
            except (InvalidOperation, ValueError, TypeError):
                pass

        products.append(
            {
                "id": product_id,
                "title": title.strip()[:200],
                "category": category,
                "category_label": labels[category],
                "price_cents": price_cents,
                "price_display": f"${price_cents / 100:,.2f}",
                "description": (
                    description[:4000]
                    if isinstance(description, str)
                    else ""
                ),
                "image": image_url(row.get("image")),
                "rating_text": rating_text,
            }
        )

        seen.add(product_id)

    if payload and not products:
        raise ValueError("Catalog contained no usable products")

    return products


def fetch_products():
    # Connect/read inactivity limits, plus a checked elapsed-time budget.
    # Requests timeouts are not a strict total wall-clock deadline.
    started = time.monotonic()

    with requests.get(
        API_URL,
        timeout=(3.05, 8),
        stream=True,
        allow_redirects=False,
        headers={"Accept": "application/json"},
    ) as response:
        response.raise_for_status()

        if response.status_code != 200:
            raise ValueError("Unexpected upstream status")

        body = bytearray()

        for chunk in response.iter_content(chunk_size=16384):
            body.extend(chunk)

            if (
                len(body) > 1048576
                or time.monotonic() - started > 15
            ):
                raise ValueError(
                    "Catalog exceeded size or elapsed-time budget"
                )

        return clean_products(json.loads(body))


@require_safe
def products(request):
    data = cache.get(CACHE_KEY)
    error = ""
    stale = False
    status = 200

    if data is None:
        try:
            data = fetch_products()

            cache.set(CACHE_KEY, data, 60)
            cache.set(CACHE_KEY + ":stale", data, 3600)

        except (requests.RequestException, ValueError):
            logger.warning(
                "StreetX catalog unavailable",
                exc_info=True,
            )

            data = cache.get(CACHE_KEY + ":stale")

            if data is None:
                data = []
                status = 503
                error = (
                    "The catalog is temporarily unavailable. "
                    "Please try again shortly."
                )
            else:
                stale = True

    categories = []

    for key, label, subtitle in CATEGORIES:
        sample = next(
            (
                product
                for product in data
                if product["category"] == key and product["image"]
            ),
            None,
        )

        categories.append(
            {
                "key": key,
                "label": label,
                "subtitle": subtitle,
                "image": sample["image"] if sample else "",
            }
        )

    response = render(
        request,
        "products.html",
        {
            "products": data,
            "categories": categories,
            "catalog_error": error,
            "catalog_stale": stale,
            "placeholder": PLACEHOLDER,
        },
        status=status,
    )

    if status == 503:
        response["Retry-After"] = "60"

    return response