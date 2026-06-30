# NOTES — securitybook-to-skill

Ghi lại quá trình phát triển, các quyết định thiết kế, và kết quả thu được theo thứ tự thời gian.

---

## 1. Bối cảnh và vấn đề ban đầu

`book-to-skill` gốc trích xuất văn bản tốt nhưng artifact sinh ra còn hạn chế với tài liệu Red Team/Pentest vì:

- Không nhận diện được các nhóm kiến thức như Information Gathering, Authentication Testing, Security Assessment Planning, Rules of Engagement.
- Lệnh kỹ thuật trong PDF bị nhiễu do xuống dòng hoặc trộn với output.
- Artifact đủ file, đủ heading nhưng không đảm bảo phủ nội dung cốt lõi của tài liệu nguồn.
- Không có cơ chế đánh giá semantic, citation coverage và traceability.

**Hai benchmark đại diện ban đầu:** OWASP Web Security Testing Guide và NIST SP 800-115.
**Scope mở rộng sau:** API pentest, mobile, cloud/container, AI Red Team (OFFSEC AI-300), classic pentest (PEN200/OSCP).

---

## 2. Thiết kế đề xuất (giai đoạn đầu)

Kiến trúc mở rộng gồm bốn thành phần:

1. **Red Team Profile** — `profiles/redteam/` với schema, artifact list, prompt templates, knowledge types.
2. **Section/Concept Splitter** — tách tài liệu theo concept thay vì chapter vật lý; gán nội dung vào từng nhóm kiến thức.
3. **Citation Map** — `coverage.json` + `citations.json` ghi tên file nguồn, line range, concept key, confidence.
4. **Evaluator/Benchmark** — đánh giá nhiều lớp: artifact completeness, concept coverage, citation linkage, command quality, safety constraints.

**14 artifact output theo thiết kế:**
`SKILL.md`, `chapters/`, `glossary.md`, `patterns.md`, `cheatsheet.md`, `checklist.md`, `commands.md`, `workflows.md`, `troubleshooting.md`, `reporting.md`, `safety.md`, `references.md`, `coverage.json`, `citations.json`.

---

## 3. Nhật ký cải thiện

### Vòng 1 — Nhận diện concept và bổ sung taxonomy

**Vấn đề phát hiện khi kiểm thử ban đầu:**
- Structural evaluator báo PASS nhưng nội dung còn nghèo nàn.
- OWASP WSTG giữ lại 1/11 concept quan trọng.
- NIST SP 800-115 giữ lại 3/12 concept quan trọng.
- `commands.md` bị nhiễu do PDF line-wrap.
- Tên skill sinh từ filename thô như `Nistspecialpublication800 115`.

**Thay đổi:**
1. Bổ sung taxonomy OWASP/NIST (23 concept) vào generator.
2. Ưu tiên heading theo concept đã nhận diện; lọc bỏ heading nhiễu.
3. Làm sạch command extraction: nhận diện inline command, tách command khỏi output.
4. Đưa concept coverage vào nhiều artifact.
5. Chuẩn hóa tên skill.
6. Bổ sung regression tests.

**Kết quả:**
- OWASP: 11/11 concept (100%). NIST: 12/12 concept (100%).
- `commands.md` giảm nhiễu PDF output.
- Tests: **129 passed**.

---

### Vòng 2 — Bắt buộc Docling + Full artifact set + Concept-based chapters

**Quyết định kiến trúc:** bắt buộc Docling cho PDF Red Team/Pentest. Nếu PDF không dùng `extraction_method: docling`, generator dừng với lỗi.

**Thay đổi:**
7. Bắt buộc Docling; thêm `--allow-non-docling` chỉ cho synthetic unit test.
8. Mở rộng output từ 8 lên 14 artifact (full set).
9. Sinh `chapters/` theo concept thay vì chapter detector gốc.
10. Thêm `coverage.json` và `citations.json`.
11. Nâng evaluator: artifact completeness, Docling requirement, concept coverage, citation linkage, command quality, safety.
12. Cập nhật regression tests.

**Kết quả:**
- Tests: **130 passed**.
- Smoke test CLI với metadata Docling synthetic: generator sinh 18 artifact, evaluator PASS.

---

### Vòng 3 — Cải thiện section selection + command cleanup (OWASP/NIST Docling thật)

**Vấn đề phát hiện sau chạy Docling thật:**
- `authentication-testing.md` ban đầu lấy bảng danh sách OTG-AUTHN thay vì body section.
- `information-gathering.md` đôi khi lấy bảng cuối tài liệu thay vì `Testing for Information Gathering`.
- Command bị nhiễu do Docling giữ cả command lẫn output trên cùng dòng.

**Thay đổi:**
13. Chấm điểm nhiều candidate section; phạt mục lục/bảng; ưu tiên `Testing for <concept>`; gắn confidence rõ: `primary_section`, `body_match`, `weak_mention`, `toc_only`.
14. Command cleanup: chuẩn hóa `https:/ /`, escaped markdown `s\_client`, HTML entities, cắt output DNS dính vào `host`.
15. Thêm regression tests: `test_redteam_section_selection_prefers_body_over_toc`, `test_redteam_testing_for_heading_keeps_subtest_body`, `test_redteam_command_cleanup_handles_docling_artifacts`.

**Kết quả:**
- Tests focused: **8 passed**.
- OWASP Docling regenerate: evaluator PASS, concept coverage 19/19, citation linked 19 chapters.
- Đánh giá tổng: ~8/10 (tăng từ ~7/10).

---

### Vòng 4 — Chapter substance + parser heading theo cấp số mục (NIST)

**Vấn đề:**
- Heading `6. Security Assessment Planning` bị cắt tại `6.1...` vì parser chỉ đếm `#`.
- Source Summary quá nông; evaluator chưa bắt được.

**Thay đổi:**
16. Sửa `heading_level()`: nhận dạng `6`, `6.1`, `6.4.3` như cấp 1/2/3.
17. Tăng source excerpt: không loại bỏ paragraph dài >140 ký tự.
18. Thêm `check_chapter_substance()`: bắt buộc mỗi chapter có `Source Summary`, `Source-Derived Procedure`, `Evidence To Collect`, `Reporting Notes`, `Decision Points`, `Safety Constraints`, `Citation`.
19. Mở rộng template chapter: thêm procedure, evidence, reporting, decision points.

**Kết quả:**
- NIST SP 800-115 Docling: evaluator PASS, concept coverage 20/20, citation linked 20 chapters, chapter substance PASS.
- OWASP Docling: evaluator PASS, concept coverage 19/19, citation linked 19 chapters, chapter substance PASS.
- Tests: **134 passed**.
- Đánh giá tổng: ~8/10 → chapter usefulness tăng từ 6.5 lên 7.5.

---

### Vòng 5 — Semantic filtering + document taxonomy profile + dọn stale chapters

**Vấn đề:**
- NIST sinh nhầm chapter web/API/cloud từ weak mention.
- OWASP sinh nhầm `api-pentest`, `mobile-pentest`, `cloud-container-pentest`.
- Generator ghi chapter mới nhưng không xóa chapter cũ → stale files.
- Evaluator chưa bắt nhãn concept sai domain.

**Thay đổi:**
21. Thêm `document_profile`: `nist_methodology`, `owasp_web`, `general_redteam`.
22. Không promote `weak_mention` thành chapter; giữ ở `coverage.json` + `references.md`.
23. Thêm `check_semantic_alignment()`: API/mobile/cloud/auth/session/input phải có keyword semantic tương ứng.
24. Dọn stale chapters khi regenerate.

**Kết quả:**
- OWASP: 13 primary chapters, 0 stale, semantic PASS.
- NIST: 10 primary chapters, 2 weak references, 0 stale, semantic PASS.
- Tests focused: **10 passed**. Full: **136 passed**.
- Concept selection accuracy: ~6.5 → ~8/10. Domain labeling: ~6 → ~8/10.

---

### Vòng 6 — OFFSEC AI-300 Advanced AI Red Teaming

**Baseline (trước nâng cấp):**
- Generator nhận diện `general_redteam`, chỉ sinh 4 primary chapters.
- Tài liệu thực tế: agents (877x), RAG (418x), embeddings (350x), MCP (278x), A2A (144x).
- Concept selection accuracy: ~4.5/10. Overall: ~5.5-6/10.

**Thay đổi:**
27. Thêm document profile `ai_redteam`.
28. Thêm AI Red Team taxonomy: `ai-threat-modeling`, `ai-reconnaissance`, `ai-agent-attacks`, `multi-agent-a2a-attacks`, `rag-pipeline-exploitation`, `embedding-attacks`, `mcp-tool-surface-attacks`, `ai-supply-chain-attacks`, `ai-infrastructure-deployment-exploits`, `ai-capstone-red-team`.
29. Sửa parser heading nhận diện `3. Attacking AI Agents`, `4. Attacking Multi-Agent Systems...`.
30. Mở rộng semantic evaluator cho AI concepts.

**Kết quả:**
- Output `outputs/redteam-offsec-ai300`: 13 primary chapters, 1 weak ref, 11 `primary_section`, 2 `body_match`.
- Evaluator PASS. Semantic PASS. Stale 0.
- Tests focused: **11 passed**. Full: **137 passed**.
- Concept accuracy: ~4.5 → ~8/10. Overall: ~5.5-6 → ~8/10.

---

### Vòng 7 — PEN200/OSCP: profile `classic_pentest` + taxonomy mở rộng

**Thông tin nguồn:** PEN200 - OSCP 2023, PDF 869 trang, ~47 MB.

**Baseline (text mode, trước Docling):**
- Chapters detected: 2 (pdftotext mất cấu trúc).
- Generator nhận nhầm `general_redteam`: sinh nhầm `api-pentest` từ URL, `ai-capstone-red-team` từ `Challenge Lab`.

**Thay đổi:**
34. Thêm profile `classic_pentest`: loại taxonomy AI/API/Mobile/Cloud; bỏ alias `Credential` quá rộng.
35. Chạy Docling (~7-8 phút): 869 trang, 269,168 words, **66 chapters detected**.
38. Thu hẹp alias `rules-of-engagement` (bỏ `Scope`, `Authorization` đơn lẻ); sửa command sanitizer cắt `Listing/Figure <number>`.
41. Mở rộng taxonomy `classic_pentest`: thêm `network-port-scanning`, `service-enumeration`, `vulnerability-scanning`, `web-application-attacks`, `exploit-research-and-adaptation`, `password-attacks`, `windows-privilege-escalation`, `linux-privilege-escalation`, `port-redirection-and-tunneling`, `metasploit-framework`, `active-directory-enumeration`, `active-directory-attacks`, `lateral-movement`, `post-exploitation`.
42. Nâng parser command: nhận diện prompt Kali/Linux/PowerShell/Metasploit/Meterpreter; cắt output phổ biến; scoring ưu tiên command pentest.
43. Thêm benchmark gold set `profiles/redteam/benchmarks/gold_set.json` cho 4 profiles; thêm rubric scoring vào evaluator.
44. Context command: ưu tiên `Listing/Figure caption` gần command.
45. Artifact theo domain: chapter procedure steps, workflow riêng cho pentest concepts, `checklist.md` domain-specific.

**Kết quả PEN200 Docling sau toàn bộ nâng cấp:**
- Active taxonomy: 22 concepts. Primary chapters: 20. Weak refs: 2. Stale: 0.
- Commands: 40 (sau nâng parser). Rubric: 100/100 `classic_pentest`.
- Evaluator PASS. Semantic PASS.
- Tests focused: **16 passed**. Full: **142 passed**.
- Overall: ~6.2-6.5 (baseline text) → ~8.3-8.5/10.

---

### Vòng 8 — Review và cải thiện chất lượng OWASP/NIST/OFFSEC AI-300

**Vấn đề phát hiện:**
- OWASP: `host -l` mất domain; domain bị tách thành `www.example. com`.
- OFFSEC AI-300: command multiline bị cắt ở `\`; giới hạn 40 command chưa đủ.
- NIST: gần không có command (đúng bản chất tài liệu phương pháp luận).
- Source summary trong chapter còn mỏng (~10 dòng).

**Thay đổi:**
- Tăng source excerpt lên ~18 dòng/chapter.
- Thêm domain procedure steps cho OWASP web testing, NIST methodology, và AI Red Team concepts.
- Sửa sanitizer giữ đúng `host -l`; chuẩn hóa domain bị tách.
- Nối command multiline khi kết thúc bằng `\` hoặc JSON/quote chưa đóng.
- Tăng giới hạn command từ 40 lên **80**.
- Ưu tiên thêm `python3`, `kubectl` trong command scoring.
- Điều chỉnh benchmark AI: `curl`, `python`, `proxychains` thay vì yêu cầu `docker` khi source không có.

**Kết quả sau regenerate:**

| Source | Found concepts | Commands | Rubric | Evaluator |
|--------|----------------|----------|--------|-----------|
| OWASP WSTG | 12 | 11 | 100/100 | PASS |
| NIST SP 800-115 | 12 | 0 (đúng bản chất) | 100/100 | PASS |
| OFFSEC AI-300 | 13 | 80 | 100/100 | PASS |
| PEN200 Docling | 20 | 80 | 100/100 | PASS |

- Tests focused: **17 passed**. Full: **143 passed**.
- Stale chapter: 0 cho tất cả output.

---

### Vòng 9 — Agent runtime (giai đoạn trung gian → harness path)

**Mục tiêu ban đầu:** thêm lớp agent-assisted để Codex/Claude Code sinh prose artifact chất lượng hơn.

**Thay đổi:**
49. Thêm `--mode rule|agent|hybrid` và `--provider mock|manual` vào `generate_redteam_skill.py`.
- `rule`: giữ deterministic output cũ.
- `agent`: render prompt bundle; với `--provider manual --dry-run-prompts` dùng để handoff trung gian.
- `hybrid`: Python giữ concept/citation/safety; provider sinh prose.
- `mock`: deterministic cho tests.
- `manual`: ghi prompt bundle vào `prompt_runs/`.
- Thêm prompt rendering từ `profiles/redteam/prompts/`.
- Thêm revision loop capped bởi `--max-revisions`.
- Thêm `evaluation.json` và `quality_report.md` output.
- Thêm sensitive source material detection.

**Làm rõ lại workflow chính (mục 50):** đường chính không phải `generate_redteam_skill.py → prompt_runs → agent` mà là:

```
extract.py
  → full_text.txt + metadata.json
  → Codex/Claude Code đọc trực tiếp
  → tự sinh full skill artifacts
  → evaluate_redteam_skill.py
```

`tools/generate_redteam_skill.py` giữ vai trò **baseline/fallback/regression helper**, không phải trung tâm workflow.

**Kết quả:**
- Tests: **156 passed**.
- Pipeline sẵn sàng cho provider LLM thật mà không đổi schema.

---

### Vòng 10 — Harness-first upgrade: shared module, quality gates, profile cleanup

**Vấn đề phát hiện sau chuyển sang harness path:**
- `evaluate_redteam_skill.py` phụ thuộc trực tiếp vào `generate_redteam_skill.py` → evaluator không thể chạy độc lập.
- Tests import từ generator → kết nối sai, evaluator không thể tái sử dụng.
- Evaluator score 100/100 nhưng bỏ qua 4 vấn đề nội dung: Purpose field generic, Source Summary chứa `## heading` artifact từ Docling, nhiều chapter không có command, procedure template giống nhau qua tất cả chapter.
- `docs/harness/` và `.claude/commands/` chứa 80 dòng workflow lặp lại hoàn toàn từ canonical `.agents/skills/`.
- `general_redteam` profile không có benchmark → tài liệu generic luôn bị WARN "rubric not configured".
- `artifacts.yaml` không có `description:` → harness không biết purpose của từng artifact.
- `classify_knowledge.md` tồn tại nhưng không được reference ở đâu.
- `knowledge_types` trong `schema.yaml` định nghĩa nhưng không được enforce.

**Thay đổi:**
51. Tạo `tools/redteam_shared.py` — single source of truth cho `TAXONOMY`, `REQUIRED_GENERATED_ARTIFACTS`, `REQUIRED_SECTION_TITLES`, và các helper functions dùng chung. Evaluator và generator đều import từ đây.
52. Decouple `evaluate_redteam_skill.py` khỏi `generate_redteam_skill.py`.
53. Đánh dấu `generate_redteam_skill.py` là **comparison baseline** — không extend thêm, giữ để so sánh chất lượng rule-based vs harness.
54. Thêm 3 evaluator quality checks mới:
    - `check_command_purpose_quality`: FAIL nếu `Purpose:` vẫn là "Source-supported command or tool invocation".
    - `check_source_summary_cleanliness`: FAIL nếu `Source Summary` có bullet bắt đầu bằng `- ## Heading`.
    - `check_chapter_command_coverage`: WARN nếu >70% chapters không có command.
55. Mở rộng Step 4 trong canonical SKILL.md với 4 quy tắc bắt buộc cho harness:
    - Per-chapter command extraction (tìm command trong section của concept đó).
    - Source Summary formatting (không để markdown heading artifact).
    - Source-Derived Procedure specificity (reference test case/tool cụ thể từ source).
    - Command metadata quality (`Purpose` ≥1 câu mô tả accomplishment; `Context of use` ≥25 words).
56. Giảm `.claude/commands/securitybook-to-skill.md` và `docs/harness/codex-...` thành thin dispatch stubs (từ 88 dòng xuống 15 dòng mỗi file). Xóa `docs/harness/` hoàn toàn (Codex không đọc tự động).
57. Thêm `general_redteam` benchmark vào `gold_set.json` (min_score 70, min_found_concepts 3, min_command_count 0).
58. Thêm `description:` cho tất cả 14 artifact trong `artifacts.yaml`.
59. Sync `generate_commands.md` prompt với các quality rules mới (Purpose, Context min-length).
60. Comment `knowledge_types` trong `schema.yaml` là documentation-only; xóa `classify_knowledge.md`.
61. Thêm 4 harness-output integration tests (`@pytest.mark.skipif`) và cập nhật CI với job `evaluate-harness-output`.
62. Gộp `improve_quality` và `de_xuat_mo_rong_redteam.md` vào `NOTES.md`; xóa 2 file gốc.

**Kết quả:**
- Tests: **160 passed**.
- Evaluator bắt được 4 quality issues mà trước đây score 100/100 bỏ qua.
- `general_redteam` benchmark: tài liệu generic không còn bị WARN về thiếu rubric.
- Canonical harness: `.agents/skills/securitybook-to-skill/SKILL.md` — các file khác là stubs tham chiếu về canonical.

---

## 4. Kết quả tổng hợp

### Điểm chất lượng theo vòng cải thiện (rule-based path)

| Tiêu chí | Ban đầu | Sau vòng 4 | Sau vòng 8 | Sau vòng 10 |
|----------|---------|------------|------------|-------------|
| Artifact completeness | 5/10 | 9/10 | 9/10 | 9/10 |
| Docling integration | N/A | 8.5/10 | 9/10 | 9/10 |
| Safety | 6/10 | 9/10 | 9/10 | 9/10 |
| Traceability/citation | 2/10 | 8/10 | 8.5/10 | 8.5/10 |
| Concept selection accuracy | 3/10 | 7.5/10 | 8.3/10 | 8.3/10 |
| Command quality | 3/10 | 7/10 | 8.2/10 | 8.2/10 |
| Chapter usefulness | 2/10 | 7.5/10 | 8.3/10 | 8.3/10 |
| Evaluator quality gate rigor | 2/10 | 6/10 | 7/10 | **8.5/10** |
| **Overall (rule-based)** | **~3/10** | **~8/10** | **~8.3-8.5/10** | **~8.3-8.5/10** |

### Harness path (Claude Code / Codex direct generation)

Sau khi chuyển sang harness path, output `outputs/redteam-owasp-wstg-docling` đạt:
- Rubric evaluator: **100/100** (`owasp_web` benchmark).
- Required concepts: 6/6. Commands: 11/5 (min). Command terms: 3/3.
- Tất cả required artifacts: PASS. Safety: PASS. Semantic alignment: PASS.

---

## 5. Quyết định kiến trúc quan trọng

| # | Quyết định | Lý do |
|---|-----------|-------|
| 1 | Bắt buộc Docling cho PDF | `pdftotext` mất cấu trúc: 2 chapters vs 66 chapters với Docling trên PEN200 |
| 2 | Không promote `weak_mention` thành chapter | Giảm over-match; output ít file hơn nhưng đúng trọng tâm hơn |
| 3 | Document profile (`owasp_web`, `nist_methodology`, `ai_redteam`, `classic_pentest`, `general_redteam`) | Mỗi họ tài liệu có taxonomy riêng, tránh lẫn concept không phù hợp |
| 4 | Harness sinh trực tiếp từ `full_text.txt` + `metadata.json` | Rule-based generator có giới hạn semantic; Claude Code/Codex tổng hợp prose chất lượng hơn |
| 5 | `generate_redteam_skill.py` giữ làm comparison baseline | Có giá trị để so sánh chất lượng giữa rule-based và harness output |
| 6 | `redteam_shared.py` là single source of truth | Tách constants/functions dùng chung để evaluator không phụ thuộc generator |
| 7 | `.agents/skills/SKILL.md` là canonical harness định nghĩa | Claude Code, Copilot đọc từ đây; `.claude/commands/` và `docs/harness/` là thin stubs |

---

## 6. Hạn chế còn lại

- `commands.md` OWASP còn ít command (11) vì source PDF có ít command rõ ràng — parser request/code block cần sâu hơn.
- Một số command có thể chứa credential/lab token từ source — cần redaction layer trước khi chia sẻ rộng.
- Evaluator vẫn keyword/rubric-based; 3 quality checks mới (vòng 10) cải thiện nhưng chưa có gold-answer semantic judge.
- Taxonomy chưa bao phủ: wireless pentest, social engineering, adversary emulation, compliance audit.
- Chưa có merge/ranking đa nguồn khi sinh skill từ nhiều tài liệu lớn cùng lúc.
- Harness output hiện có (`redteam-owasp-wstg-docling`) sinh trước quality rules mới — cần regenerate để pass `check_command_purpose_quality` và `check_source_summary_cleanliness`.

---

## 7. Hướng tiếp theo

- ~~Tách evaluator khỏi generator~~ ✅ done (vòng 10 — `redteam_shared.py`)
- ~~Thêm quality gate cho command Purpose và Source Summary~~ ✅ done (vòng 10)
- ~~Thêm `general_redteam` benchmark~~ ✅ done (vòng 10)
- Regenerate harness output (`redteam-owasp-wstg-docling`) để pass evaluator mới.
- Thêm secret redaction cho command output từ lab/courseware.
- Parser request/code block sâu hơn để tăng OWASP command count.
- Mở rộng gold benchmark cho API, mobile, cloud-native, AD pentest.
- Thêm gold-answer semantic rubric thay thế keyword matching.
- So sánh có hệ thống: rule-based vs harness output trên cùng nguồn (đây là lý do giữ generator làm baseline).
