"""
discord_sender.py
Đăng nhập bot Discord, với mỗi pack tạo 1 thread mới trong Forum Channel.
"""

import asyncio

import discord
from discord import ForumChannel, Embed


async def send_pack_to_forum(forum: ForumChannel, pack: dict) -> None:
    """
    Tạo 1 thread mới trong forum cho 1 pack.
    pack: dict có title, image, description, tags, url (xem scraper.py)
    """
    embed = Embed(
        title=pack["title"][:256],
        url=pack["url"],
        description=pack["description"][:2000],
        color=discord.Color.blurple(),
    )
    embed.set_image(url=pack["image"])

    if pack["tags"]:
        embed.add_field(name="Tags", value=", ".join(pack["tags"])[:1024], inline=False)

    embed.add_field(name="Link gốc", value=pack["url"], inline=False)

    # Tên thread tối đa 100 ký tự theo giới hạn Discord
    thread_name = pack["title"][:100]

    await forum.create_thread(
        name=thread_name,
        embed=embed,
    )


async def run_bulk_upload(
    token: str,
    forum_channel_id: int,
    packs: list[dict],
    delay_seconds: float = 2.0,
) -> None:
    """
    Đăng nhập bot, gửi toàn bộ packs lên forum, sau đó thoát.
    delay_seconds: nghỉ giữa mỗi thread để tránh rate limit Discord.
    """
    intents = discord.Intents.default()
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        try:
            channel = client.get_channel(forum_channel_id)
            if channel is None:
                channel = await client.fetch_channel(forum_channel_id)

            if not isinstance(channel, ForumChannel):
                print(f"Channel ID {forum_channel_id} không phải là Forum Channel.")
                await client.close()
                return

            print(f"Đăng nhập thành công: {client.user}. Bắt đầu gửi {len(packs)} pack...")

            success, failed = 0, 0
            for i, pack in enumerate(packs, 1):
                try:
                    await send_pack_to_forum(channel, pack)
                    success += 1
                    print(f"[{i}/{len(packs)}] Đã tạo thread: {pack['title']}")
                except discord.HTTPException as e:
                    failed += 1
                    print(f"[{i}/{len(packs)}] Lỗi gửi '{pack['title']}': {e}")

                await asyncio.sleep(delay_seconds)

            print(f"Hoàn tất. Thành công: {success}, Lỗi: {failed}")
        finally:
            await client.close()

    await client.start(token)
