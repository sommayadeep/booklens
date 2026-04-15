from __future__ import annotations

import re
import time
from typing import Dict, List
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
except Exception:  # pragma: no cover
    webdriver = None
    Options = None
    By = None

BASE_URL = "https://books.toscrape.com/"


def scrape_books(*, pages: int = 2, max_books: int = 40) -> List[Dict]:
    # Selenium is useful for small crawls, but for large ingests it can be a bottleneck.
    if pages <= 5 and max_books <= 200:
        books = _scrape_with_selenium(pages, max_books)
        if books:
            return books
    books = _scrape_with_requests(pages, max_books)
    if books:
        return books
    return _fallback_books(max_books=max_books)


def _scrape_with_selenium(pages: int, max_books: int) -> List[Dict]:
    if webdriver is None or Options is None or By is None:
        return []

    driver = None
    books: List[Dict] = []

    try:
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1600,1200")

        driver = webdriver.Chrome(options=options)
        detail_links: List[str] = []

        for page in range(1, pages + 1):
            page_url = urljoin(BASE_URL, f"catalogue/page-{page}.html")
            driver.get(page_url)
            time.sleep(0.5)
            anchors = driver.find_elements(By.CSS_SELECTOR, ".product_pod h3 a")
            for anchor in anchors:
                href = anchor.get_attribute("href")
                if href and href not in detail_links:
                    detail_links.append(href)
                if len(detail_links) >= max_books:
                    break
            if len(detail_links) >= max_books:
                break

        for link in detail_links[:max_books]:
            driver.get(link)
            time.sleep(0.2)
            books.append(_parse_detail_from_selenium(driver, link))

        return books
    except Exception:
        return []
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass


def _parse_detail_from_selenium(driver, link: str) -> Dict:
    title = _safe_text(driver, "h1")
    price = _safe_text(driver, ".price_color")
    description = _safe_text(driver, "#product_description + p")
    image_src = _safe_attr(driver, ".thumbnail img", "src")
    category = _safe_text(driver, ".breadcrumb li:nth-child(3)")
    rating_classes = _safe_attr(driver, "p.star-rating", "class")

    rating = _extract_rating_from_class(rating_classes)
    reviews_count = _extract_reviews_count(_safe_text(driver, ".instock.availability"))

    return {
        "title": title or "Untitled",
        "author": "Unknown",
        "rating": rating,
        "reviews_count": reviews_count,
        "description": description or f"A {category.lower() if category else 'general'} book listed at Books to Scrape.",
        "book_url": link,
        "image_url": urljoin(BASE_URL, image_src) if image_src else "",
        "metadata": {"source": "books.toscrape.com", "price": price, "category": category},
    }


def _scrape_with_requests(pages: int, max_books: int) -> List[Dict]:
    session = requests.Session()
    session.headers.update({"User-Agent": "BookLensBot/1.0"})
    listing_only_mode = max_books > 300

    detail_links: List[str] = []
    quick_books: List[Dict] = []
    for page in range(1, pages + 1):
        page_url = urljoin(BASE_URL, f"catalogue/page-{page}.html")
        try:
            resp = session.get(page_url, timeout=20)
        except requests.RequestException:
            continue
        if not resp.ok:
            continue

        soup = BeautifulSoup(resp.text, "html.parser")
        for pod in soup.select(".product_pod"):
            anchor = pod.select_one("h3 a")
            if anchor is None:
                continue
            href = anchor.get("href")
            if not href:
                continue
            full_url = urljoin(page_url, href)
            if full_url not in detail_links:
                detail_links.append(full_url)
            if listing_only_mode:
                title = anchor.get("title") or anchor.get_text(strip=True) or "Untitled"
                image = pod.select_one(".image_container img")
                rating_tag = pod.select_one("p.star-rating")
                price = pod.select_one(".price_color")
                quick_books.append(
                    {
                        "title": title,
                        "author": "Unknown",
                        "rating": _extract_rating_from_class(rating_tag.get("class", "") if rating_tag else ""),
                        "reviews_count": 0,
                        "description": "Book metadata imported from listing page.",
                        "book_url": full_url,
                        "image_url": urljoin(BASE_URL, image.get("src")) if image and image.get("src") else "",
                        "metadata": {
                            "source": "books.toscrape.com",
                            "price": price.get_text(strip=True) if price else "",
                            "mode": "listing_only",
                        },
                    }
                )
                if len(quick_books) >= max_books:
                    break
            if len(detail_links) >= max_books:
                break
        if (listing_only_mode and len(quick_books) >= max_books) or len(detail_links) >= max_books:
            break

    if listing_only_mode and quick_books:
        return quick_books[:max_books]

    books: List[Dict] = []
    for link in detail_links[:max_books]:
        try:
            resp = session.get(link, timeout=20)
        except requests.RequestException:
            continue
        if not resp.ok:
            continue
        soup = BeautifulSoup(resp.text, "html.parser")

        title = soup.select_one("h1")
        description = soup.select_one("#product_description + p")
        price = soup.select_one(".price_color")
        category = soup.select_one(".breadcrumb li:nth-child(3)")
        image = soup.select_one(".thumbnail img")
        rating_tag = soup.select_one("p.star-rating")
        availability = soup.select_one(".instock.availability")

        books.append(
            {
                "title": title.get_text(strip=True) if title else "Untitled",
                "author": "Unknown",
                "rating": _extract_rating_from_class(rating_tag.get("class", "") if rating_tag else ""),
                "reviews_count": _extract_reviews_count(availability.get_text(" ", strip=True) if availability else ""),
                "description": description.get_text(" ", strip=True)
                if description
                else f"A {(category.get_text(strip=True).lower() if category else 'general')} book listed at Books to Scrape.",
                "book_url": link,
                "image_url": urljoin(BASE_URL, image.get("src")) if image and image.get("src") else "",
                "metadata": {
                    "source": "books.toscrape.com",
                    "price": price.get_text(strip=True) if price else "",
                    "category": category.get_text(strip=True) if category else "",
                },
            }
        )

    return books


def _fallback_books(max_books: int) -> List[Dict]:
    fallback = [
        {
            "title": "Atomic Habits",
            "author": "James Clear",
            "rating": 4.8,
            "reviews_count": 12000,
            "description": "A practical framework for improving every day through small habits, identity shifts, and repeatable systems.",
            "book_url": "https://example.com/books/atomic-habits",
            "image_url": "https://images.unsplash.com/photo-1512820790803-83ca734da794",
            "metadata": {"source": "fallback_seed", "category": "Self Help"},
        },
        {
            "title": "Deep Work",
            "author": "Cal Newport",
            "rating": 4.5,
            "reviews_count": 6700,
            "description": "A guide to focused, distraction-free productivity and the value of cognitively demanding work in the digital era.",
            "book_url": "https://example.com/books/deep-work",
            "image_url": "https://images.unsplash.com/photo-1524995997946-a1c2e315a42f",
            "metadata": {"source": "fallback_seed", "category": "Productivity"},
        },
        {
            "title": "Dune",
            "author": "Frank Herbert",
            "rating": 4.6,
            "reviews_count": 9800,
            "description": "An epic science fiction story of politics, ecology, prophecy, and survival on the desert planet Arrakis.",
            "book_url": "https://example.com/books/dune",
            "image_url": "https://images.unsplash.com/photo-1519682577862-22b62b24e493",
            "metadata": {"source": "fallback_seed", "category": "Science Fiction"},
        },
        {
            "title": "The Hobbit",
            "author": "J.R.R. Tolkien",
            "rating": 4.7,
            "reviews_count": 15000,
            "description": "Bilbo Baggins joins a quest involving dwarves, dragons, hidden treasure, and an unexpected journey of courage.",
            "book_url": "https://example.com/books/the-hobbit",
            "image_url": "https://images.unsplash.com/photo-1474932430478-367dbb6832c1",
            "metadata": {"source": "fallback_seed", "category": "Fantasy"},
        },
        {
            "title": "The Silent Patient",
            "author": "Alex Michaelides",
            "rating": 4.3,
            "reviews_count": 8700,
            "description": "A psychological mystery about trauma, obsession, and the shocking secrets behind a famous murder case.",
            "book_url": "https://example.com/books/the-silent-patient",
            "image_url": "https://images.unsplash.com/photo-1495446815901-a7297e633e8d",
            "metadata": {"source": "fallback_seed", "category": "Mystery"},
        },
        {
            "title": "Pride and Prejudice",
            "author": "Jane Austen",
            "rating": 4.6,
            "reviews_count": 14200,
            "description": "A classic romance and social satire following Elizabeth Bennet as she navigates family expectations and love.",
            "book_url": "https://example.com/books/pride-and-prejudice",
            "image_url": "https://images.unsplash.com/photo-1544947950-fa07a98d237f",
            "metadata": {"source": "fallback_seed", "category": "Romance"},
        },
    ]
    return fallback[: max(1, max_books)]


def _extract_rating_from_class(class_names) -> float:
    if isinstance(class_names, list):
        class_names = " ".join(class_names)

    map_rating = {
        "One": 1.0,
        "Two": 2.0,
        "Three": 3.0,
        "Four": 4.0,
        "Five": 5.0,
    }
    for label, value in map_rating.items():
        if label in class_names:
            return value
    return 0.0


def _extract_reviews_count(text: str) -> int:
    match = re.search(r"(\d+)", text)
    return int(match.group(1)) if match else 0


def _safe_text(driver, selector: str) -> str:
    try:
        return driver.find_element(By.CSS_SELECTOR, selector).text.strip()
    except Exception:
        return ""


def _safe_attr(driver, selector: str, attr: str) -> str:
    try:
        return driver.find_element(By.CSS_SELECTOR, selector).get_attribute(attr) or ""
    except Exception:
        return ""
