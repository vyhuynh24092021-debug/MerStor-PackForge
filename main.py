"""
main.py
Chạy trên Termux (Android):

    python main.py

Bot Token đọc từ file .env (DISCORD_BOT_TOKEN) - chỉ cần điền 1 lần.

Mỗi lần chạy, tool sẽ hỏi:
  1. Link profile PVPRP (vd: https://pvprp.com/profile/xThonyG)
  2. Forum Channel ID

Tool sẽ quét toàn bộ pack trong profile, rồi tạo 1 thread mới trong Forum
cho mỗi pack (tên pack, ảnh banner, mô tả, tags, link gốc).
KHÔNG tải file .mcpack vì nút Download trên PVPRP cần JS + xem YouTube trước.
"""

import asyncio
import sys
import os
from pathlib import Path

from dotenv import load_dotenv

from scraper import scan_profile
from discord_sender import run_bulk_upload

ENV_PATH = Path(__file__).parent / ".env"


def ask(prompt: str) -> str:
    val = input(prompt).strip()
    if not val:
        print("Giá trị không được để trống.")
        sys.exit(1)
    return val


def main():
    print("=== PVPRP -> Discord Forum Tool ===\n")

    load_dotenv(ENV_PATH)

    # Token: chỉ đọc từ .env, không hỏi lại
    token = os.getenv("DISCORD_BOT_TOKEN") or ""
    if not token:
        print("Chưa có DISCORD_BOT_TOKEN trong file .env. Điền vào đó rồi chạy lại.")
        sys.exit(1)

    # Hỏi lại mỗi lần chạy
    profile_url = ask("Link profile PVPRP (vd: https://pvprp.com/profile/xThonyG): ")
    channel_id_raw = ask("Forum Channel ID: ")

    try:
        channel_id = int(channel_id_raw)
    except ValueError:
        print("Channel ID phải là số nguyên.")
        sys.exit(1)

    limit_raw = input("Giới hạn số pack để test (Enter = lấy hết): ").strip()
    limit = int(limit_raw) if limit_raw else None

    print(f"\nBắt đầu quét profile (limit={limit or 'không giới hạn'})...\n")

    packs = list(scan_profile(profile_url, delay=1.0, limit=limit))

    if not packs:
        print("Không lấy được pack nào. Kiểm tra lại link profile.")
        sys.exit(1)

    print(f"\nĐã quét xong {len(packs)} pack. Bắt đầu gửi lên Discord...\n")

    asyncio.run(run_bulk_upload(token, channel_id, packs, delay_seconds=2.0))

    print("\nHoàn tất toàn bộ.")


if __name__ == "__main__":
    main()
