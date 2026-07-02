"""
scraper.py
Lấy danh sách texture pack từ 1 trang profile PVPRP, và chi tiết từng pack.

Không tải file .mcpack (vì nút Download cần JS + xem YouTube trước).
Chỉ lấy: tên, ảnh banner, mô tả, tags, link gốc.
"""

import re
import time
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    )
}

BASE_URL = "https://pvprp.com"


def get_profile_pack_links(profile_url: str, session: requests.Session) -> list[str]:
    """
    Truy cập trang profile, trả về danh sách URL đầy đủ của từng pack.
    Ví dụ pack link trên trang: /pack?p=17840&or=profile
    """
    resp = session.get(profile_url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/pack?p=" in href:
            if href.startswith("http"):
                full = href
            else:
                full = BASE_URL + href if href.startswith("/") else BASE_URL + "/" + href
            links.add(full)

    return sorted(links)


def get_pack_details(pack_url: str, session: requests.Session) -> dict | None:
    """
    Truy cập 1 trang pack và trích xuất:
      - title
      - image (banner og:image)
      - description
      - tags (list str)
      - url (canonical, sạch, không kèm &or=...)
    Trả về None nếu không lấy được dữ liệu tối thiểu (title + image).
    """
    resp = session.get(pack_url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    # Title: ưu tiên og:title, fallback <h1>
    title = None
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        title = og_title["content"].split(" - Free Download")[0].strip()
    if not title:
        h1 = soup.find("h1")
        if h1:
            title = h1.get_text(strip=True)

    # Ảnh banner
    image = None
    og_image = soup.find("meta", property="og:image")
    if og_image and og_image.get("content"):
        image = og_image["content"]

    if not title or not image:
        return None

    # Mô tả
    description = None
    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc and meta_desc.get("content"):
        description = meta_desc["content"].strip()
    else:
        # fallback: tìm heading "Description" và lấy đoạn kế tiếp
        desc_heading = soup.find(
            lambda tag: tag.name in ("h2", "h3") and tag.get_text(strip=True) == "Description"
        )
        if desc_heading:
            nxt = desc_heading.find_next(["h3", "p"])
            if nxt:
                description = nxt.get_text(strip=True)

    # Tags: link dạng /search?t=xxx
    tags = []
    for a in soup.find_all("a", href=True):
        if "/search?t=" in a["href"]:
            tag_text = a.get_text(strip=True)
            if tag_text and tag_text not in tags:
                tags.append(tag_text)

    # Canonical URL sạch
    canonical = pack_url
    link_canon = soup.find("link", rel="canonical")
    if link_canon and link_canon.get("href"):
        canonical = link_canon["href"]

    return {
        "title": title,
        "image": image,
        "description": description or "Không có mô tả.",
        "tags": tags,
        "url": canonical,
    }


def scan_profile(profile_url: str, delay: float = 1.0, limit: int | None = None):
    """
    Generator: quét toàn bộ pack của 1 profile, yield từng dict pack đã lấy chi tiết.
    delay: thời gian nghỉ (giây) giữa các request để tránh bị chặn.
    limit: giới hạn số pack xử lý (dùng để test), None = lấy hết.
    """
    session = requests.Session()

    pack_links = get_profile_pack_links(profile_url, session)
    if limit:
        pack_links = pack_links[:limit]

    total = len(pack_links)
    for i, link in enumerate(pack_links, 1):
        try:
            details = get_pack_details(link, session)
        except requests.RequestException as e:
            print(f"[{i}/{total}] Lỗi khi tải {link}: {e}")
            details = None

        if details:
            print(f"[{i}/{total}] OK: {details['title']}")
            yield details
        else:
            print(f"[{i}/{total}] Bỏ qua (thiếu dữ liệu): {link}")

        time.sleep(delay)
