# Thien-Skill-Creative-Diagram

<p align="center">
  <img src="evidence/p09/candidates/full-crest-plate-light-400.png" alt="TDTN crest with sword, lion, letterforms and open book in navy and gold" width="180">
</p>

`Thien-Skill-Creative-Diagram` là skill tạo và kiểm tra diagram chuyên nghiệp cho Claude, ChatGPT và Codex. Phiên bản `1.0.0` cung cấp một canonical runtime với ba artifact phát hành xác định: Claude Code plugin, OpenAI plugin và Universal raw skill.

Repository này là **private audit repository**. Quyền truy cập, xem, tải xuống hoặc clone repository **không tự cấp quyền sử dụng**. Xem mục [Giấy phép](#giấy-phép) trước khi cài đặt hoặc thực thi.

## Artifact v1.0.0

| Mục tiêu | File | SHA-256 |
|---|---|---|
| Claude Code plugin | `thien-skill-creative-diagram-1.0.0-claude-plugin.zip` | `bba5b464322d8d50ec2f9b76e18581df3e5614004078ba40708f2c8cd1104fa9` |
| OpenAI plugin | `thien-skill-creative-diagram-1.0.0-openai-plugin.zip` | `7d7a33dbdecdd87e9f5237c3ab39b1416ba11c3b736424ba3eb0151c9d73893c` |
| Universal raw skill | `thien-skill-creative-diagram-1.0.0-universal-raw-skill.zip` | `4fcccc656008dd1caba8c1605b0523b0c041afaf216f739aba7373b5d5ac748f` |

Tải ba ZIP và `SHA256SUMS.txt` từ GitHub Release `v1.0.0`, sau đó để chúng trong cùng một thư mục.

## Kiểm tra checksum trước khi cài đặt

macOS/Linux:

```bash
shasum -a 256 -c SHA256SUMS.txt
```

Nếu hệ thống có GNU coreutils:

```bash
sha256sum -c SHA256SUMS.txt
```

Windows PowerShell:

```powershell
Get-FileHash .\thien-skill-creative-diagram-1.0.0-claude-plugin.zip -Algorithm SHA256
Get-FileHash .\thien-skill-creative-diagram-1.0.0-openai-plugin.zip -Algorithm SHA256
Get-FileHash .\thien-skill-creative-diagram-1.0.0-universal-raw-skill.zip -Algorithm SHA256
```

Chỉ tiếp tục nếu hash khớp hoàn toàn với bảng trên và `SHA256SUMS.txt`.

## Cài đặt Claude Code

### Cách 1 — nạp Claude plugin ZIP cho một phiên

Yêu cầu Claude Code hiện hành có hỗ trợ `--plugin-dir` với ZIP. Từ thư mục chứa artifact:

```bash
claude --plugin-dir ./thien-skill-creative-diagram-1.0.0-claude-plugin.zip
```

Trong phiên Claude Code, yêu cầu tự nhiên một diagram hoặc gọi skill theo namespace plugin nếu host hiển thị lệnh đó:

```text
/thien-skill-creative-diagram:thien-skill-creative-diagram
```

Nếu lệnh không xuất hiện, chạy `/help`, kiểm tra log nạp plugin và xác nhận checksum/phiên bản Claude Code.

### Cách 2 — giải nén, validate và nạp thư mục plugin

```bash
mkdir -p ./tcd-claude-plugin
unzip ./thien-skill-creative-diagram-1.0.0-claude-plugin.zip -d ./tcd-claude-plugin
claude plugin validate ./tcd-claude-plugin/thien-skill-creative-diagram
claude --plugin-dir ./tcd-claude-plugin/thien-skill-creative-diagram
```

Claude Code plugin là route phát hành dành cho Claude. Không dùng OpenAI plugin ZIP thay cho Claude plugin.

Tài liệu nền tảng chính thức: [Claude Code plugins](https://code.claude.com/docs/en/plugins), [Claude Code skills](https://code.claude.com/docs/en/skills), [plugin reference](https://code.claude.com/docs/en/plugins-reference).

## Cài đặt Codex bằng Universal raw skill

Đây là route local đơn giản nhất cho Codex CLI, Codex IDE và các host đọc Agent Skills từ `.agents/skills`.

### Cài cho một repository

Chạy tại repository đích:

```bash
mkdir -p ./.agents/skills
unzip /path/to/thien-skill-creative-diagram-1.0.0-universal-raw-skill.zip -d ./.agents/skills
test -f ./.agents/skills/thien-skill-creative-diagram/SKILL.md
```

Cây kết quả bắt buộc:

```text
.agents/
└── skills/
    └── thien-skill-creative-diagram/
        ├── SKILL.md
        ├── scripts/
        ├── references/
        └── ...
```

Khởi động hoặc khởi động lại Codex trong repository đó. Codex sẽ phát hiện skill từ `.agents/skills` dọc theo cây thư mục tới repository root.

### Cài cho người dùng hiện tại

```bash
mkdir -p "$HOME/.agents/skills"
unzip /path/to/thien-skill-creative-diagram-1.0.0-universal-raw-skill.zip -d "$HOME/.agents/skills"
test -f "$HOME/.agents/skills/thien-skill-creative-diagram/SKILL.md"
```

Khởi động lại Codex nếu skill chưa xuất hiện. Không đổi tên folder vì `name` trong `SKILL.md` phải khớp `thien-skill-creative-diagram`.

Tài liệu nền tảng chính thức: [OpenAI — Build skills](https://learn.chatgpt.com/docs/build-skills).

## Cài OpenAI plugin cho ChatGPT Desktop/Codex

OpenAI plugin ZIP là delivery archive có `.codex-plugin/plugin.json`; đây **không phải** cam kết rằng mọi tài khoản có thể upload ZIP trực tiếp. Route marketplace/plugin phụ thuộc phiên bản ứng dụng, tài khoản, workspace policy và quyền admin.

### Local repository marketplace

1. Giải nén plugin vào repository sử dụng:

```bash
mkdir -p ./plugins
unzip /path/to/thien-skill-creative-diagram-1.0.0-openai-plugin.zip -d ./plugins
test -f ./plugins/thien-skill-creative-diagram/.codex-plugin/plugin.json
mkdir -p ./.agents/plugins
```

2. Tạo hoặc bổ sung `./.agents/plugins/marketplace.json`:

```json
{
  "name": "thien-private-plugins",
  "interface": {
    "displayName": "Thien Private Plugins"
  },
  "plugins": [
    {
      "name": "thien-skill-creative-diagram",
      "source": {
        "source": "local",
        "path": "./plugins/thien-skill-creative-diagram"
      },
      "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL"
      },
      "category": "Productivity"
    }
  ]
}
```

Nếu file đã có plugin khác, hợp nhất entry mới vào mảng `plugins`; không ghi đè các entry hiện hữu.

3. Khởi động lại ChatGPT Desktop, mở **Plugins Directory**, chọn marketplace `Thien Private Plugins`, cài plugin và thử trong chat mới.

Codex CLI hiện hành cũng có thể đăng ký marketplace Git bằng `codex plugin marketplace add`, nhưng repository này chứa full audit corpus chứ không phải catalog marketplace độc lập. Không dùng lệnh đó thay cho local marketplace ở trên nếu chưa tạo marketplace Git chuyên biệt.

Tài liệu nền tảng chính thức: [OpenAI — Package your plugin](https://developers.openai.com/plugins/build/plugins), [OpenAI Plugins](https://developers.openai.com/plugins).

## Kiểm tra sau cài đặt

Thử một yêu cầu rõ loại diagram, dữ liệu và định dạng, ví dụ:

```text
Tạo swimlane diagram bằng tiếng Việt cho quy trình thu tiền, xuất HTML tĩnh và kèm bảng dữ liệu truy cập được.
```

Kết quả mong đợi:

- skill nhận diện yêu cầu diagram và chọn type phù hợp;
- HTML/SVG tự chứa, không tải tài nguyên ngoài;
- dữ liệu đầu vào được coi là dữ liệu không tin cậy, không phải chỉ dẫn;
- PNG chỉ được tạo khi host đã có rasterizer phù hợp; nếu không, skill trả SVG và cảnh báo, không tự cài dependency;
- output định lượng giữ dữ liệu nguồn và có biểu diễn text/table phù hợp.

## Phạm vi và giới hạn đã xác minh

- Runtime hỗ trợ taxonomy 27 canonical diagram type và bảy semantic pattern.
- Ba package đã qua deterministic build, parity, hygiene và extracted-runtime smoke checks.
- Ma trận host tại thời điểm phát hành giữ `0 supported`, `13 conditional`, `2 unsupported`; repository không quảng bá surface conditional thành supported.
- Browser/cross-browser execution không được tuyên bố PASS do local `file://` policy trong môi trường QA.
- Skill không thay thế ý kiến pháp lý, thuế, kiểm toán, an toàn, kiến trúc hoặc chuyên môn khác.

## Giấy phép

Phiên bản này chịu sự điều chỉnh của **Tran Ngoc Thien's Skill Commercial Source-Available License 2.0**:

- đây là giấy phép thương mại nguồn có thể xem, **không phải giấy phép nguồn mở**;
- bản tiếng Việt được ưu tiên áp dụng;
- quyền truy cập, clone, tải xuống hoặc nhận bản sao không tự cấp quyền cài đặt, thực thi, sửa đổi, phân phối hay cung cấp dịch vụ;
- quyền sử dụng chỉ phát sinh theo Paid Order, Written Permission/email hoặc Commercial Agreement hợp lệ;
- logo, crest, tên, nhãn hiệu và goodwill TDTN bị loại khỏi quyền cấp chung và cần văn bản cho phép riêng;
- liên hệ cấp quyền: `thien.8888@gmail.com`.

Đọc đầy đủ trước khi sử dụng:

- [`LICENSE.md`](LICENSE.md) — bản ở root repository, byte-identical với legal candidate đã duyệt
- [`thien-skill-creative-diagram/LICENSE-APPLICATION.md`](thien-skill-creative-diagram/LICENSE-APPLICATION.md)
- [`thien-skill-creative-diagram/NOTICE`](thien-skill-creative-diagram/NOTICE)
- [`thien-skill-creative-diagram/THIRD_PARTY_NOTICES.md`](thien-skill-creative-diagram/THIRD_PARTY_NOTICES.md)
- [`thien-skill-creative-diagram/SOURCE_MANIFEST.json`](thien-skill-creative-diagram/SOURCE_MANIFEST.json)
- [`thien-skill-creative-diagram/ASSET_MANIFEST.json`](thien-skill-creative-diagram/ASSET_MANIFEST.json)

Legal package bytes là exact candidate `TCD-LEGAL-1.0.0-RC2` đã được owner/Vietnamese-lawyer approval và G-06/G-07 ràng buộc trong evidence phát hành. Các câu trạng thái candidate bên trong legal files phản ánh thời điểm freeze; evidence gate sau đó ghi nhận quyết định phê duyệt mà không sửa lại legal bytes đã khóa.

## Provenance

`diagram-design` là nguồn chức năng chủ đạo ở mức taxonomy, hành vi và yêu cầu trừu tượng. Repository này là **clean-room-oriented independent reimplementation**: không sao chép code, prose, CSS, template, script, specimen hoặc asset upstream. `Thien-UI-UX-Ultra` chỉ được dùng ở mức nguyên tắc và workflow.

Chi tiết nằm trong `SOURCE_MANIFEST.json`, `THIRD_PARTY_NOTICES.md` và evidence G-01/G-06 của private audit repository.

## Release integrity

Release hợp lệ phải có:

- tag `v1.0.0`;
- ba ZIP đúng hash ở đầu README;
- `SHA256SUMS.txt`;
- G-00 đến G-07 `PASS` trong private audit records;
- không thay đổi legal, brand hoặc package bytes sau approval.
