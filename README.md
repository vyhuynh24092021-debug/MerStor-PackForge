# MerStor-PackForge
# PVPRP → Discord Forum Tool

Quét toàn bộ texture pack từ 1 trang profile PVPRP (vd: `https://pvprp.com/profile/xThonyG`),
và tạo 1 thread mới trong Discord Forum Channel cho mỗi pack (tên, ảnh banner, mô tả, tags, link gốc).

**Lưu ý quan trọng:** Tool KHÔNG tải file `.mcpack`. Nút Download trên PVPRP yêu cầu
JavaScript và bắt xem YouTube trước khi link tải thật hiện ra — việc giả lập bước này
phức tạp và có thể vi phạm điều khoản của trang. Tool chỉ đăng ảnh + thông tin + link gốc
để người xem tự bấm vào tải.

---

## 1. Cài đặt trên Termux

```bash
pkg update && pkg upgrade -y
pkg install python -y
pip install -r requirements.txt
```

Nếu `lxml` lỗi khi cài (thường do thiếu thư viện biên dịch), chạy thêm:

```bash
pkg install libxml2 libxslt -y
pip install lxml
```

## 2. Tạo Discord Bot & lấy Token

1. Vào https://discord.com/developers/applications → **New Application**
2. Vào tab **Bot** → **Add Bot** → **Reset Token** → copy Token (giữ bí mật, không share)
3. Vào tab **OAuth2 → URL Generator**:
   - Scopes: `bot`
   - Bot Permissions: `Send Messages`, `Manage Threads`, `Create Public Threads`, `Embed Links`
4. Copy link tạo ra, mở trình duyệt, chọn server của bạn → Authorize

## 3. Lấy Forum Channel ID

1. Trong Discord: **Cài đặt người dùng → Nâng cao → bật Chế độ nhà phát triển (Developer Mode)**
2. Chuột phải vào kênh Forum → **Copy Channel ID**

## 4. Cấu hình Bot Token (chỉ cần điền 1 lần)

Mở file `.env`, điền token vào sau dấu `=`:

```
DISCORD_BOT_TOKEN=nhap_token_that_vao_day
```

File `.env` đã được thêm vào `.gitignore`, không lo bị commit nhầm lên Git.
**Tuyệt đối không chia sẻ file này hoặc token cho ai.**

## 5. Chạy tool

```bash
python main.py
```

Mỗi lần chạy, tool sẽ hỏi:
- Link profile PVPRP
- Forum Channel ID
- Giới hạn số pack để test (Enter = lấy hết)

Token thì không hỏi lại — tự lấy từ `.env`.

## 6. Gợi ý chạy thử trước

Với 364 pack, nên nhập `5` khi tool hỏi "Giới hạn số pack để test" trước, chắc chắn:
- Bot có quyền tạo thread trong forum
- Embed hiển thị đúng ảnh/tên/mô tả

Sau khi ổn, chạy lại và nhấn Enter (bỏ trống) ở bước giới hạn để lấy hết.

## Cấu trúc file

```
pvprp_discord_tool/
├── main.py            # Chạy chính, hỏi profile_url + channel_id mỗi lần, đọc token từ .env
├── scraper.py          # Lấy danh sách pack + chi tiết từ PVPRP
├── discord_sender.py   # Đăng nhập bot, tạo thread cho mỗi pack
├── .env                 # Bot Token (không share, không commit)
├── .gitignore
└── requirements.txt
```

## Giới hạn / lưu ý

- Tool nghỉ 1s giữa mỗi request lấy dữ liệu, và 2s giữa mỗi lần tạo thread — để tránh
  bị PVPRP chặn IP hoặc bị Discord rate-limit. Với 364 pack, quá trình sẽ mất khoảng
  20-30 phút, đừng tắt Termux giữa chừng.
- Nếu PVPRP thay đổi cấu trúc HTML trong tương lai, phần `scraper.py` có thể cần chỉnh lại
  selector (tag `og:title`, `og:image`, `/search?t=`).
- Discord giới hạn tên thread tối đa 100 ký tự — tool tự cắt bớt nếu tên pack dài hơn.
