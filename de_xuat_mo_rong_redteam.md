# Đề xuất mở rộng book-to-skill cho tài liệu Red Team/Pentest

## 1. Bối cảnh và vấn đề

`book-to-skill` là công cụ chuyển đổi sách hoặc tài liệu kỹ thuật thành một bộ Agent Skill có cấu trúc, giúp tác nhân AI có thể tra cứu, học và áp dụng tri thức từ tài liệu gốc trong quá trình làm việc. Thiết kế ban đầu của công cụ phù hợp với các tài liệu dạng sách, trong đó nội dung thường được tổ chức theo chương, mục, thuật ngữ, mô hình tư duy và các mẫu kỹ thuật.

Tuy nhiên, khi áp dụng cho tài liệu Red Team/Pentest nói chung, cấu trúc tài liệu có đặc điểm khác so với sách thông thường. Nhóm tài liệu mục tiêu có thể bao gồm pentest handbook, methodology guide, lab manual, tool manual, checklist, playbook, report template, tài liệu web/mobile/API/cloud pentest, hoặc tiêu chuẩn kiểm thử bảo mật. Các tài liệu này thường được tổ chức theo section, test case, phương pháp luận, checklist, quy trình đánh giá, công cụ, lệnh kiểm thử và yêu cầu an toàn. OWASP Web Security Testing Guide và NIST SP 800-115 chỉ được sử dụng như hai tài liệu benchmark đại diện để kiểm thử chất lượng, không phải giới hạn phạm vi của hệ thống.

Kết quả thử nghiệm ban đầu cho thấy công cụ có khả năng trích xuất văn bản tốt, nhưng chất lượng artifact sinh ra còn hạn chế nếu không có cơ chế xử lý chuyên biệt cho tài liệu Red Team/Pentest. Một số vấn đề chính gồm:

- Không nhận diện đầy đủ các nhóm kiến thức quan trọng như Information Gathering, Authentication Testing, Session Management Testing, Security Assessment Planning hoặc Rules of Engagement.
- Các lệnh kỹ thuật trong tài liệu PDF có thể bị nhiễu do xuống dòng hoặc trộn với output khi dùng `pdftotext`.
- Artifact sinh ra có thể đủ file và đủ heading nhưng chưa đảm bảo bao phủ nội dung cốt lõi của tài liệu nguồn.
- Chưa có cơ chế đánh giá chất lượng semantic, citation coverage và traceability giữa artifact với tài liệu gốc.

Do đó, cần mở rộng `book-to-skill` theo hướng hỗ trợ profile Red Team/Pentest chuyên biệt, tập trung vào độ chính xác, khả năng truy vết nguồn và chất lượng artifact.

## 2. Mục tiêu mở rộng

Mục tiêu của đề xuất là xây dựng cơ chế mở rộng cho `book-to-skill` để sinh Red Team/Pentest Skill từ tài liệu kỹ thuật bảo mật với chất lượng cao hơn so với cách sinh artifact tuyến tính. Hệ thống mở rộng cần đạt các mục tiêu sau:

- Nhận diện cấu trúc tài liệu theo section và concept thay vì chỉ theo chapter.
- Sinh artifact có khả năng truy vết về tài liệu gốc thông qua citation hoặc source map.
- Tạo các artifact phù hợp với hoạt động Red Team/Pentest như checklist, commands, workflows, troubleshooting, reporting và safety.
- Đồng thời giữ lại tinh thần thiết kế ban đầu của `book-to-skill` thông qua các file như `chapters/`, `glossary.md`, `patterns.md` và `cheatsheet.md`.
- Xây dựng evaluator/benchmark để đo chất lượng output thay vì chỉ kiểm tra sự tồn tại của file.
- Không làm phá vỡ pipeline gốc của `book-to-skill`; các thay đổi nên có tính mở rộng và có thể tích hợp dần.

## 3. Phạm vi thực hiện

Trong phạm vi hiện tại, đề xuất tập trung vào hai hướng chính, áp dụng cho tài liệu Red Team/Pentest nói chung:

1. **Generator dựa trên section/concept có citation**
2. **Benchmark/evaluator để đánh giá chất lượng và độ chính xác**

Các hướng phát triển lớn hơn như tích hợp trực tiếp vào CLI chính thức, sử dụng LLM/API nhiều pass, hoặc thay thế hoàn toàn cơ chế extraction bằng layout-aware parser có thể được đưa vào phần hướng phát triển tương lai.

## 4. Kiến trúc mở rộng đề xuất

Kiến trúc mở rộng gồm các thành phần chính sau:

### 4.1. Red Team/Pentest Profile

Thêm một profile riêng cho Red Team/Pentest tại:

```text
profiles/redteam/
```

Profile này định nghĩa:

- Schema tri thức Red Team/Pentest.
- Danh sách artifact cần sinh.
- Prompt template hoặc template mô tả cách sinh từng artifact.
- Các knowledge type như conceptual, procedural, command, tool, scenario, troubleshooting, reporting và safety.

Profile giúp tách riêng logic Red Team/Pentest khỏi pipeline lõi, từ đó không phá vỡ chức năng gốc của `book-to-skill`.

### 4.2. Section/Concept Splitter

Thay vì phụ thuộc vào chapter detector gốc, hệ thống cần có cơ chế chia tài liệu theo section hoặc concept. Với tài liệu Red Team/Pentest, các đơn vị tri thức quan trọng có thể là:

- Nhóm kiểm thử ứng dụng web, ví dụ Information Gathering, Authentication Testing, Authorization Testing, Session Management Testing, Input Validation Testing.
- Nhóm kiểm thử API, ví dụ endpoint discovery, authentication model review, authorization boundary testing, input validation, rate limiting, error handling.
- Nhóm kiểm thử mobile, ví dụ static analysis, dynamic analysis, local storage review, transport security, platform permission testing.
- Nhóm kiểm thử cloud/container, ví dụ identity and access review, misconfiguration testing, exposed service discovery, logging and monitoring review.
- Nhóm phương pháp luận pentest, ví dụ planning, rules of engagement, target identification, vulnerability validation, exploitation constraints, reporting, remediation.
- Các phần về scope, authorization, rules of engagement, reporting và evidence handling.

Section/concept splitter có nhiệm vụ:

- Phát hiện các heading và section quan trọng.
- Gán nội dung liên quan vào từng concept.
- Loại bỏ nhiễu như số trang, dòng mục lục, timestamp, output bị trộn hoặc dòng PDF bị cắt.
- Tạo các chunk nội dung có phạm vi rõ ràng để dùng cho artifact generation.

### 4.3. Citation Map

Để tăng accuracy và khả năng kiểm chứng, mỗi section chunk nên được gắn thông tin nguồn:

- Tên file nguồn.
- Dòng bắt đầu và dòng kết thúc trong `full_text.txt`.
- Tên concept hoặc section.
- Loại tri thức tương ứng.
- Mức độ tin cậy của việc map nội dung.

Citation map có thể được lưu dưới dạng:

```text
coverage.json
```

hoặc:

```text
citations.json
```

Thông tin này giúp người dùng kiểm tra artifact sinh ra có dựa trên tài liệu nguồn hay không. Đây là điểm quan trọng để giảm hallucination và nâng độ tin cậy của Skill.

### 4.4. Full Artifact Generation

Red Team/Pentest profile nên sinh cả hai nhóm artifact:

Nhóm artifact theo thiết kế gốc của `book-to-skill`:

- `SKILL.md`
- `chapters/`
- `glossary.md`
- `patterns.md`
- `cheatsheet.md`

Nhóm artifact chuyên biệt cho Red Team/Pentest:

- `checklist.md`
- `commands.md`
- `workflows.md`
- `troubleshooting.md`
- `reporting.md`
- `safety.md`
- `references.md`
- `coverage.json` hoặc `citations.json`

Cách kết hợp này giúp Skill vừa giữ được khả năng học và tra cứu theo tri thức nền, vừa hỗ trợ trực tiếp các hoạt động đánh giá bảo mật có kiểm soát.

## 5. Thiết kế artifact đề xuất

### 5.1. SKILL.md

`SKILL.md` đóng vai trò là file trung tâm của Skill. File này nên chứa:

- Mục tiêu của Skill.
- Phạm vi sử dụng.
- Ràng buộc an toàn và authorized-use.
- Danh sách concept chính.
- Chỉ mục liên kết tới các chapter theo concept.
- Chỉ mục tới checklist, commands, workflows, reporting và references.

File này cần ngắn gọn, không chứa toàn bộ nội dung chi tiết. Các phần chi tiết nên được đưa vào file con để agent chỉ tải khi cần.

### 5.2. chapters/

Thư mục `chapters/` nên được sinh theo concept thay vì theo chương vật lý. Với tài liệu web pentest hoặc OWASP-like, có thể sinh:

```text
chapters/information-gathering.md
chapters/authentication-testing.md
chapters/session-management-testing.md
chapters/input-validation-testing.md
chapters/business-logic-testing.md
```

Với tài liệu phương pháp luận pentest hoặc NIST-like, có thể sinh:

```text
chapters/information-security-assessment-methodology.md
chapters/security-assessment-planning.md
chapters/security-assessment-execution.md
chapters/post-testing-activities.md
chapters/rules-of-engagement.md
```

Mỗi chapter nên gồm:

- Mục tiêu của concept.
- Nội dung chính từ nguồn.
- Quy trình hoặc phương pháp liên quan.
- Công cụ hoặc lệnh nếu có.
- Kết quả mong đợi.
- Rủi ro và điều kiện an toàn.
- Citation về tài liệu gốc.

### 5.3. glossary.md

`glossary.md` chứa các thuật ngữ quan trọng trong tài liệu, ví dụ:

- Assessment
- Penetration testing
- Vulnerability validation
- Rules of engagement
- Authentication
- Authorization
- Session management
- Evidence
- Remediation

Mỗi thuật ngữ nên có định nghĩa ngắn, ngữ cảnh sử dụng và nguồn tham chiếu.

### 5.4. patterns.md

`patterns.md` chứa các mẫu kỹ thuật hoặc phương pháp lặp lại trong tài liệu, ví dụ:

- Reconnaissance pattern
- Authentication testing pattern
- Session validation pattern
- Input validation testing pattern
- Planning-execution-reporting assessment pattern

Artifact này giúp agent không chỉ nhớ khái niệm, mà còn hiểu cách áp dụng tri thức trong quy trình đánh giá.

### 5.5. cheatsheet.md

`cheatsheet.md` nên đóng vai trò là bảng quyết định nhanh:

- Khi nào dùng checklist nào.
- Khi nào cần dừng vì thiếu authorization.
- Khi nào một command bị thiếu context.
- Khi nào một finding đủ điều kiện đưa vào report.
- Mapping giữa concept, workflow, evidence và artifact liên quan.

### 5.6. commands.md

`commands.md` cần được xử lý cẩn thận vì tài liệu Red Team/Pentest có tính dual-use. Mỗi command cần có:

- Command.
- Mục đích.
- Context of use.
- Preconditions.
- Required inputs.
- Expected output.
- Common errors.
- Safety note.
- Source reference.

Command thiếu context không nên được trình bày như hướng dẫn thực thi hoàn chỉnh. Thay vào đó, cần đánh dấu `context incomplete`.

### 5.7. workflows.md

`workflows.md` mô tả các luồng công việc có kiểm soát:

- Chuẩn bị scope và authorization.
- Lựa chọn kỹ thuật đánh giá.
- Thực hiện kiểm thử trong môi trường được phép.
- Thu thập evidence.
- Phân tích kết quả.
- Viết report.
- Đề xuất remediation.

Các workflow phải luôn đi kèm ràng buộc an toàn.

### 5.8. safety.md

`safety.md` là artifact bắt buộc với Red Team/Pentest profile. Nội dung cần nhấn mạnh:

- Chỉ sử dụng cho giáo dục, nghiên cứu, phòng thủ, lab hoặc kiểm thử được ủy quyền.
- Không sử dụng chống lại hệ thống không có permission.
- Không tự động hóa tấn công.
- Không vượt scope.
- Dừng khi authorization hoặc safety không rõ ràng.

## 6. Evaluator và benchmark chất lượng

Để nâng cao accuracy, chỉ kiểm tra file tồn tại là chưa đủ. Cần xây dựng evaluator có nhiều lớp.

### 6.1. Artifact Completeness

Kiểm tra các artifact bắt buộc có tồn tại hay không:

- `SKILL.md`
- `chapters/`
- `glossary.md`
- `patterns.md`
- `cheatsheet.md`
- `checklist.md`
- `commands.md`
- `workflows.md`
- `troubleshooting.md`
- `reporting.md`
- `safety.md`
- `references.md`

### 6.2. Concept Coverage

Kiểm tra các concept quan trọng từ tài liệu nguồn có xuất hiện trong output hay không. Concept list không nên hardcode cho một tài liệu duy nhất; hệ thống nên có một taxonomy Red Team/Pentest tổng quát, sau đó bổ sung bộ benchmark riêng cho từng nhóm tài liệu.

Ví dụ với nhóm web pentest/OWASP-like:

- Information Gathering
- Configuration and Deployment Management Testing
- Identity Management Testing
- Authentication Testing
- Authorization Testing
- Session Management Testing
- Input Validation Testing
- Business Logic Testing
- Client Side Testing

Ví dụ với nhóm methodology/NIST-like:

- Information Security Assessment Methodology
- Technical Assessment Techniques
- Security Assessment Planning
- Security Assessment Execution
- Post-Testing Activities
- Rules of Engagement
- Final Report

### 6.3. Citation Coverage

Kiểm tra các artifact có dẫn được về section nguồn hay không. Mục tiêu là các nội dung quan trọng trong `SKILL.md`, `chapters/`, `commands.md` và `workflows.md` đều có citation hoặc source reference.

### 6.4. Command Quality

Kiểm tra:

- Command không bị trộn với output PDF.
- Command có context of use.
- Command có safety note.
- Command thiếu input hoặc expected output phải được đánh dấu rõ.
- Không sinh command không có trong nguồn.

### 6.5. Safety Constraints

Kiểm tra:

- `safety.md` tồn tại.
- Có authorized-use constraints.
- Có scope control.
- Có prohibited use.
- Có human oversight.
- Không mô tả Skill như công cụ tấn công tự động.

### 6.6. Missing Context Detection

Evaluator cần phát hiện các trường hợp output thiếu ngữ cảnh, ví dụ:

- Command có nhưng không có mục đích.
- Workflow có bước thực hiện nhưng không có precondition.
- Finding/reporting có evidence nhưng không có source.
- Concept quan trọng có trong nguồn nhưng không xuất hiện trong artifact.

## 7. Lợi ích kỳ vọng

Việc mở rộng theo hướng section/concept generator và evaluator benchmark mang lại các lợi ích sau:

- Tăng độ chính xác vì artifact được sinh từ section có phạm vi rõ ràng.
- Giảm hallucination nhờ citation map và source reference.
- Tăng khả năng kiểm chứng vì người dùng có thể trace output về tài liệu gốc.
- Giữ được cấu trúc on-demand của `book-to-skill`, giúp Skill không quá nặng.
- Phù hợp hơn với nhiều loại tài liệu Red Team/Pentest có cấu trúc phương pháp luận, checklist, test case, tool guide hoặc lab guide.
- Có cơ sở định lượng để chứng minh cải thiện chất lượng thông qua evaluator.

## 8. Rủi ro và giới hạn

Một số giới hạn cần lưu ý:

- Chất lượng phụ thuộc vào bước extraction. Nếu PDF bị lỗi layout nặng, section splitter vẫn có thể sai.
- Heuristic-based generator chưa thể thay thế hoàn toàn LLM synthesis nhiều pass.
- Benchmark ban đầu có thể thiên về OWASP/NIST nếu danh sách concept được thiết kế riêng cho hai tài liệu này. Vì vậy OWASP/NIST nên được xem là benchmark đại diện ban đầu, sau đó mở rộng thêm benchmark cho API pentest, mobile pentest, cloud pentest, Active Directory pentest và exploit-development/lab manual.
- Citation theo line range giúp trace nguồn nhưng chưa đảm bảo hiểu đúng semantic.
- Command extraction cần tiếp tục kiểm thử với nhiều định dạng tài liệu khác nhau.

## 9. Hướng phát triển tương lai

Sau phạm vi hiện tại, có thể mở rộng theo các hướng sau:

- Tích hợp `--profile redteam` trực tiếp vào CLI chính thức của `book-to-skill`.
- Sử dụng Docling hoặc layout-aware extraction để giữ tốt hơn heading, bảng và code block.
- Dùng LLM/API multi-pass để sinh chapter sâu hơn, phân loại tri thức tốt hơn và đánh giá semantic quality.
- Mở rộng profile sang Blue Team, Cloud Security, Compliance, Malware Analysis hoặc Secure Coding.
- Xây dựng gold benchmark lớn hơn với nhiều tài liệu bảo mật khác nhau.
- So sánh chất lượng output giữa heuristic generator, LLM generator và hybrid generator.

## 10. Kết luận

Đề xuất mở rộng `book-to-skill` cho tài liệu Red Team/Pentest nên tập trung trước vào generator dựa trên section/concept và evaluator benchmark. Đây là hướng cân bằng giữa tính khả thi và chất lượng, đồng thời phù hợp với mục tiêu nâng cao accuracy có thể kiểm chứng.

Thay vì chỉ sinh các artifact dựa trên cấu trúc chương truyền thống, hệ thống cần hiểu các đơn vị tri thức quan trọng trong tài liệu bảo mật, gắn chúng với citation nguồn, sinh artifact chuyên biệt cho Red Team/Pentest, và đánh giá chất lượng bằng benchmark rõ ràng. Cách tiếp cận này giúp biến `book-to-skill` từ công cụ chuyển đổi tài liệu tổng quát thành nền tảng có thể mở rộng cho nhiều nhóm tài liệu an toàn thông tin chuyên sâu.

## 11. Kết quả triển khai và đánh giá hiện tại

Sau giai đoạn thiết kế, prototype Red Team/Pentest profile đã được triển khai dưới dạng standalone pipeline, chưa can thiệp vào CLI lõi của `book-to-skill`. Pipeline hiện tại gồm:

- `profiles/redteam/`: định nghĩa schema, artifact list và prompt templates cho Red Team/Pentest profile.
- `tools/generate_redteam_skill.py`: sinh artifact từ `full_text.txt` và `metadata.json`.
- `tools/evaluate_redteam_skill.py`: đánh giá chất lượng output theo nhiều lớp.
- `tests/test_redteam_profile.py`: kiểm thử hồi quy cho generator, evaluator, command extraction và yêu cầu Docling.

### 11.1. Các chức năng đã triển khai

Hệ thống hiện đã hỗ trợ sinh full artifact set:

- `SKILL.md`
- `chapters/`
- `glossary.md`
- `patterns.md`
- `cheatsheet.md`
- `checklist.md`
- `commands.md`
- `workflows.md`
- `troubleshooting.md`
- `reporting.md`
- `safety.md`
- `references.md`
- `coverage.json`
- `citations.json`

Các điểm nâng cấp quan trọng:

- Bắt buộc dùng Docling cho PDF Red Team/Pentest. Nếu metadata cho thấy PDF được extract bằng `pdftotext`, generator sẽ dừng.
- Sinh `chapters/` theo concept thay vì phụ thuộc vào chapter detector gốc.
- Ghi `coverage.json` để thể hiện concept nào tìm được, concept nào còn thiếu.
- Ghi `citations.json` để trace concept/chapter về line range trong `full_text.txt`.
- Evaluator kiểm tra artifact completeness, Docling requirement, concept coverage, citation linkage, command quality và safety constraints.

### 11.2. Kết quả benchmark với Docling

Sau khi cài Docling, hai tài liệu benchmark đã được chạy lại bằng `--mode technical`.

Với NIST SP 800-115:

- Metadata ghi nhận `extraction_method: docling`.
- Số heading/chapter detector gốc phát hiện: 16.
- Generator sinh full artifact set tại `outputs/redteam-nist-sp800-115-docling`.
- Evaluator PASS.
- Concept coverage theo evaluator: 20/20, đạt 100%.

Với OWASP Web Security Testing Guide:

- Metadata ghi nhận `extraction_method: docling`.
- Số heading/chapter detector gốc phát hiện: 840.
- Generator sinh full artifact set tại `outputs/redteam-owasp-wstg-docling`.
- Evaluator PASS.
- Concept coverage theo evaluator: 19/19, đạt 100%.

Kết quả này cho thấy Docling cải thiện rõ rệt khả năng giữ cấu trúc tài liệu so với `pdftotext`. Tuy nhiên, số heading rất lớn ở OWASP cũng cho thấy không thể dùng trực tiếp chapter detector gốc làm cơ sở sinh skill; cần tiếp tục dùng concept-based chunking và cải thiện thuật toán chọn section.

### 11.3. Đánh giá chất lượng hiện tại

Các điểm đạt được:

- Output đã đầy đủ artifact hơn so với bản prototype ban đầu.
- Có cơ chế traceability thông qua `coverage.json` và `citations.json`.
- Có safety constraints rõ ràng cho tài liệu dual-use.
- Evaluator đã phát hiện được trường hợp không dùng Docling.
- Output có thể dùng để chứng minh hướng tiếp cận section/concept-based generation.

Các điểm còn hạn chế:

- Concept coverage hiện mới đo sự xuất hiện của concept trong output, chưa đảm bảo chapter đã lấy đúng phần nội dung sâu nhất.
- Một số chapter vẫn lấy nhầm vùng mục lục hoặc bảng tổng hợp thay vì body section chính.
- Một số command trong OWASP vẫn bị dính output hoặc bị biến dạng do layout, ví dụ command `host` bị kèm kết quả phân giải DNS.
- Taxonomy có thể over-match: tài liệu methodology như NIST vẫn sinh một số concept web pentest nếu từ khóa xuất hiện thoáng qua.
- Chapter hiện còn thiên về source index và safety wrapper, chưa đủ sâu để trở thành chapter chất lượng cao.

Chấm điểm hiện tại:

- Artifact completeness: 9/10.
- Docling integration: 8/10.
- Safety: 9/10.
- Traceability/citation: 7/10.
- Concept coverage bề mặt: 9/10.
- Semantic accuracy: 6/10.
- Chapter usefulness: 5/10.
- Command quality: 6/10.
- Overall prototype quality: khoảng 7/10.

### 11.4. Hướng cải thiện ngay sau đánh giá

Bước cải thiện tiếp theo là nâng thuật toán section selection:

- Không chọn occurrence đầu tiên của concept nếu occurrence đó nằm trong mục lục hoặc bảng tổng hợp.
- Ưu tiên heading/body section có nội dung đủ dài.
- Phân biệt `primary_section`, `toc_only`, `weak_mention` và `body_match`.
- Không sinh chapter cho concept chỉ xuất hiện thoáng qua.
- Nâng command cleaner để loại command bị dính output hoặc malformed URL.
- Nâng evaluator để chấm chapter substance, không chỉ chấm concept coverage.

### 11.5. Kết quả sau vòng cải thiện chất lượng

Sau phần đánh giá trên, prototype đã được cải thiện thêm ở ba điểm chính:

- Thuật toán chọn section không còn chọn occurrence đầu tiên một cách máy móc, mà chấm điểm nhiều candidate, phạt mục lục/bảng tổng hợp, ưu tiên body heading và section có nội dung đủ dày.
- Parser heading được sửa để hiểu cấp số mục như `6`, `6.1`, `6.4.3`, nhờ đó các section cấp chương trong tài liệu NIST không bị cắt ngay tại heading con đầu tiên.
- Evaluator được bổ sung kiểm tra `chapter substance`, bắt buộc mỗi chapter có `Source Summary`, `Source-Derived Procedure`, `Evidence To Collect`, `Reporting Notes`, `Decision Points`, `Safety Constraints` và `Citation`.

Template chapter cũng được mở rộng để artifact không chỉ là excerpt, mà có thêm quy trình sử dụng nguồn, bằng chứng cần thu thập, ghi chú báo cáo và điểm quyết định an toàn. Điều này làm cho output phù hợp hơn với mục tiêu Red Team/Pentest Skill trong môi trường được ủy quyền.

Kết quả kiểm thử sau cải thiện:

- Focused Red Team tests: `8 passed`.
- Full test suite của repository: `134 passed`.
- Compile check cho `tools` và `tests`: không lỗi.

Benchmark sau cải thiện:

- NIST SP 800-115: evaluator PASS, concept coverage `20/20`, citation linked `20 chapters`, chapter substance PASS.
- OWASP Web Security Testing Guide: evaluator PASS, concept coverage `19/19`, citation linked `19 chapters`, chapter substance PASS.

Chấm điểm sau cải thiện:

- Artifact completeness: 9/10.
- Docling integration: 8.5/10.
- Safety: 9/10.
- Traceability/citation: 8/10.
- Concept coverage bề mặt: 9/10.
- Semantic accuracy: khoảng 7.5/10.
- Chapter usefulness: khoảng 7.5/10.
- Command quality: khoảng 7/10.
- Overall prototype quality: khoảng 8/10.

Các giới hạn còn lại vẫn cần đưa vào hướng phát triển:

- Chưa có LLM multi-pass để tổng hợp sâu từng chapter từ nhiều đoạn nguồn.
- Chưa có gold-answer semantic rubric cho từng họ tài liệu Red Team/Pentest.
- Taxonomy cần mở rộng thêm cho Active Directory, network pentest, wireless, cloud-native, container/Kubernetes, social engineering và adversary emulation.
- Chưa có cơ chế merge/ranking đa nguồn khi sinh một Skill từ nhiều tài liệu lớn cùng lúc.

### 11.6. Cải thiện accuracy sau khi review thủ công output

Sau khi đọc thủ công các artifact đã sinh, nhóm vấn đề lớn nhất không còn là thiếu file hay thiếu citation, mà là độ chính xác semantic của concept selection. Cụ thể:

- NIST SP 800-115 là tài liệu methodology nhưng vẫn từng sinh các chapter web/API/cloud do một số từ khóa xuất hiện thoáng qua.
- OWASP WSTG từng sinh `api-pentest`, `mobile-pentest`, `cloud-container-pentest` từ các đoạn không thật sự là section chính của API/Mobile/Cloud testing.
- Một số chapter cũ còn sót trong thư mục `chapters/` sau khi regenerate, dù không còn nằm trong `citations.json`.

Để xử lý, prototype đã được nâng cấp thêm:

- Thêm `document_profile` để phân biệt loại tài liệu:
  - `owasp_web` dùng taxonomy web pentest, safety và reporting.
  - `nist_methodology` dùng taxonomy methodology, safety, tooling và reporting.
  - `general_redteam` giữ taxonomy tổng quát cho tài liệu chưa nhận diện được.
- Không promote `weak_mention` thành chapter chính. Weak concepts được giữ trong `coverage.json` và `references.md` để không mất dấu vết, nhưng không được trình bày như kiến thức chính.
- Thêm semantic alignment evaluator cho các concept dễ bị over-match như API, Mobile, Cloud/Container, Authentication, Authorization, Session và Input Validation.
- Dọn stale chapter khi regenerate để số file trong `chapters/` luôn khớp `citations.json`.

Kết quả sau cải thiện:

- OWASP WSTG:
  - Document profile: `owasp_web`.
  - Primary chapters: 13.
  - Weak references: 0.
  - Citation confidence: 5 `primary_section`, 8 `body_match`.
  - Evaluator: PASS.
  - Semantic alignment: PASS.
- NIST SP 800-115:
  - Document profile: `nist_methodology`.
  - Primary chapters: 10.
  - Weak references: 2, được giữ trong coverage/reference thay vì sinh thành chapter.
  - Citation confidence: 10 `body_match`.
  - Evaluator: PASS.
  - Semantic alignment: PASS.
- Kiểm tra stale chapters:
  - OWASP: expected 13, actual 13, không có file dư.
  - NIST: expected 10, actual 10, không có file dư.
- Test suite:
  - Focused Red Team tests: 10 passed.
  - Full repository tests: 136 passed.
  - Compile check: không lỗi.

Đánh giá chất lượng sau vòng semantic filtering:

- Artifact completeness: 9/10.
- Safety: 9/10.
- Traceability/citation: khoảng 8.5/10.
- Concept selection accuracy: khoảng 8/10.
- Domain labeling accuracy: khoảng 8/10.
- Chapter usefulness: khoảng 8/10.
- Command quality: khoảng 7/10.
- Overall prototype quality: khoảng 8.2-8.4/10.

Như vậy, hướng cải thiện này làm output ít nhiễu hơn và đúng trọng tâm tài liệu hơn. Đổi lại, số lượng chapter giảm xuống vì hệ thống không còn cố sinh chapter cho mọi từ khóa xuất hiện trong tài liệu. Đây là trade-off phù hợp với mục tiêu nâng accuracy và chất lượng artifact.

### 11.7. Thử nghiệm với OFFSEC AI-300 Advanced AI Red Teaming

Sau OWASP và NIST, hệ thống được thử với bộ tài liệu OFFSEC AI-300 Advanced AI Red Teaming. Đây là nhóm tài liệu khác biệt rõ so với web pentest và methodology truyền thống vì trọng tâm là AI Red Teaming.

Nguồn thử nghiệm:

- `books_test/OffSec - AI-300 Advanced AI Red Teaming/`
- 11 file HTML.
- Khoảng 135,698 words, 180K token.
- 119 heading/chapter candidates.

Baseline ban đầu cho thấy hệ thống chưa phù hợp với AI-300. Generator nhận diện tài liệu là `general_redteam` và chỉ sinh 4 primary chapters, trong khi tài liệu thực tế tập trung vào agents, RAG, embeddings, MCP, A2A, supply chain và AI infrastructure. Một số thống kê trong nguồn:

- `agent`: 877 lần.
- `RAG`: 418 lần.
- `embedding`: 350 lần.
- `MCP`: 278 lần.
- `A2A`: 144 lần.
- `Kubernetes`: 110 lần.
- `prompt injection`: 43 lần.
- `supply chain`: 38 lần.

Đánh giá baseline:

- Concept selection accuracy: khoảng 4.5/10.
- Domain labeling accuracy: khoảng 4/10.
- Chapter usefulness: khoảng 5/10.
- Overall: khoảng 5.5-6/10.

Để cải thiện, prototype được mở rộng thêm:

- Thêm document profile `ai_redteam`.
- Thêm taxonomy AI Red Team gồm:
  - AI threat modeling.
  - AI reconnaissance.
  - AI agent attacks.
  - Multi-agent/A2A attacks.
  - RAG pipeline exploitation.
  - Embedding attacks.
  - MCP/tool surface attacks.
  - AI/ML supply chain attacks.
  - AI infrastructure/deployment exploits.
  - AI capstone red team.
- Sửa parser heading để nhận diện heading dạng `3. Attacking AI Agents`, `4. Attacking Multi-Agent Systems...`.
- Ưu tiên `primary_section` và `body_match` hơn `weak_mention` khi chọn best span.
- Mở rộng semantic evaluator cho các concept AI-specific.

Kết quả sau nâng cấp:

- Output: `outputs/redteam-offsec-ai300`.
- Document profile: `ai_redteam`.
- Primary chapters: 13.
- Weak references: 1 (`logistics`).
- Missing concepts trong active taxonomy: 0.
- Citation confidence: 11 `primary_section`, 2 `body_match`.
- Evaluator: PASS.
- Semantic alignment: PASS.
- Stale chapter check: expected 13, actual 13.

Các primary chapters chính:

- `ai-threat-modeling`
- `ai-reconnaissance`
- `ai-agent-attacks`
- `multi-agent-a2a-attacks`
- `rag-pipeline-exploitation`
- `embedding-attacks`
- `mcp-tool-surface-attacks`
- `ai-supply-chain-attacks`
- `ai-infrastructure-deployment-exploits`
- `ai-capstone-red-team`
- `cloud-container-pentest`
- `rules-of-engagement`
- `final-report`

Kết quả kiểm thử:

- Focused Red Team tests: 11 passed.
- Full repository tests: 137 passed.
- Compile check: không lỗi.

Đánh giá sau nâng cấp AI-300:

- Artifact completeness: 9/10.
- Safety: 9/10.
- Traceability/citation: khoảng 8.5/10.
- Concept selection accuracy: khoảng 8/10.
- Domain labeling accuracy: khoảng 8/10.
- Chapter usefulness: khoảng 7.5-8/10.
- Overall AI-300 output: khoảng 8/10.

Kết quả này cho thấy hệ thống profile-based có thể mở rộng sang họ tài liệu Red Team mới bằng cách bổ sung document profile và taxonomy chuyên biệt, thay vì phải viết lại core pipeline.

### 11.8. Thử nghiệm với OFFSEC PEN200/OSCP

Tài liệu tiếp theo được thử nghiệm là `PEN200 - OSCP - 2023 version_1.pdf`.

Thông tin nguồn:

- PDF 1.7.
- Dung lượng khoảng 47 MB.
- 869 trang.
- Không encrypted.

Đầu tiên, hệ thống thử extraction bằng Docling:

- Lệnh: `python3 scripts/extract.py "books_test/PEN200 - OSCP - 2023 version_1.pdf" --mode technical --no-install-missing`.
- Docling bắt đầu xử lý nhưng không hoàn tất sau khoảng 5 phút.
- Tiến trình được ngắt thủ công để tránh treo phiên.

Do đó, chưa có output PEN200 Docling hợp lệ. Điều này cho thấy với PDF rất lớn, pipeline cần thêm cơ chế chạy job dài hoặc extract theo chunk/page range.

Để có baseline đánh giá tạm thời, hệ thống chạy thêm text mode:

- Method: `pdftotext`.
- Words: 272,887.
- Tokens ước lượng: khoảng 363K.
- Chapters detected: 2.
- ToC detected: yes.

Số chapter detected rất thấp cho thấy `pdftotext` không giữ được cấu trúc tốt cho tài liệu này.

Khi chạy baseline ban đầu, generator nhận diện PEN200 là `general_redteam`, gây over-match. Ví dụ:

- Sinh nhầm `api-pentest` từ dòng mỏng `The affected URL/endpoint`.
- Sinh nhầm `ai-capstone-red-team` từ cụm `Challenge Lab`.
- `authentication-testing` bị promote từ alias `Credential` quá rộng.

Để giảm lỗi này, prototype được bổ sung:

- Document profile `classic_pentest` cho tài liệu có dấu hiệu `PEN200`, `OSCP`, `PWK`, `Penetration Testing with Kali`.
- Loại taxonomy AI/API/Mobile/Cloud khỏi profile `classic_pentest`.
- Bỏ alias `Credential` quá rộng khỏi `Authentication Testing`, thay bằng `Default Credentials`.

Kết quả baseline sau chỉnh profile:

- Output: `outputs/redteam-pen200-text`.
- Document profile: `classic_pentest`.
- Primary chapters: 8.
- Weak references: 5.
- Missing active taxonomy concepts: 10.
- Citation confidence: 1 `primary_section`, 7 `body_match`.
- Evaluator: PASS khi không truyền metadata Docling.
- Stale chapter check: expected 8, actual 8.

Primary chapters:

- `information-gathering`
- `authorization-testing`
- `input-validation-testing`
- `testing-for-weak-cryptography`
- `client-side-testing`
- `information-security-assessment-methodology`
- `logistics`
- `final-report`

Đánh giá chất lượng PEN200 baseline:

- Artifact completeness: 9/10.
- Safety: 9/10.
- Traceability/citation: khoảng 6.5/10.
- Concept selection accuracy: khoảng 6.5/10.
- Domain labeling accuracy: khoảng 7/10.
- Command quality: khoảng 4/10.
- Chapter usefulness: khoảng 6/10.
- Overall baseline quality: khoảng 6.2-6.5/10.

Các hạn chế chính:

- Đây không phải output Docling, nên không nên coi là benchmark chính thức.
- `commands.md` có nhiều command giả do câu văn bị nhận nhầm thành command.
- Taxonomy `classic_pentest` còn thiếu nhiều mảng quan trọng như network enumeration, exploitation, privilege escalation, lateral movement, tunneling/pivoting, Active Directory, password attacks.
- Cần cơ chế page-range/chunk extraction để xử lý PDF lớn bằng Docling.

Sau khi Docling được cài đặt, hệ thống đã chạy lại PEN200 bằng Docling và có kết quả đầy đủ hơn:

- Lệnh: `python3 scripts/extract.py "books_test/PEN200 - OSCP - 2023 version_1.pdf" --mode technical --no-install-missing`.
- Thời gian xử lý: khoảng 7-8 phút.
- Pages: 869.
- Words: 269,168.
- Tokens ước lượng: khoảng 358K.
- Chapters detected: 66.
- Output text: `/tmp/book_skill_work/full_text.txt`.
- Output metadata: `/tmp/book_skill_work/metadata.json`.

Kết quả này xác nhận Docling cải thiện rõ rệt cấu trúc tài liệu so với baseline `pdftotext`, từ 2 chapter detected lên 66 chapter detected.

Sau khi sinh lại skill tại `outputs/redteam-pen200-docling`, quá trình review thủ công phát hiện hai lỗi chất lượng:

- `rules-of-engagement.md` bị sinh nhầm từ một dòng routing table có cụm `scope link`.
- `commands.md` có command bị dính caption dạng `Listing 883`.

Các lỗi này đã được sửa trong prototype:

- Thu hẹp alias của `rules-of-engagement`, bỏ các alias quá rộng như `Scope` và `Authorization`.
- Thêm xử lý làm sạch command để cắt hậu tố `Listing <number>` và `Figure <number>`.
- Thêm quality gate trong evaluator để command còn chứa marker caption sẽ bị đánh FAIL.
- Thêm regression test để tránh lỗi tái xuất hiện.

Kết quả PEN200 Docling sau sửa:

- Output: `outputs/redteam-pen200-docling`.
- Document profile: `classic_pentest`.
- Primary chapters: 8.
- Weak references: 5.
- Evaluator: PASS.
- Command quality: PASS.
- Semantic alignment: PASS.
- Stale chapter: 0.

Primary chapters:

- `information-gathering`
- `authorization-testing`
- `input-validation-testing`
- `testing-for-weak-cryptography`
- `client-side-testing`
- `information-security-assessment-methodology`
- `logistics`
- `final-report`

Weak references:

- `authentication-testing`
- `session-management-testing`
- `review-techniques`
- `rules-of-engagement`
- `technical-tools-resources-selection`

Đánh giá chất lượng PEN200 Docling sau sửa:

- Artifact completeness: khoảng 9/10.
- Safety: khoảng 9/10.
- Traceability/citation: khoảng 7.5/10.
- Concept selection accuracy: khoảng 7/10.
- Domain labeling accuracy: khoảng 7.5/10.
- Command quality: khoảng 6.5/10.
- Chapter usefulness: khoảng 7/10.
- Overall quality: khoảng 7.0-7.3/10.

Kết luận từ thử nghiệm PEN200:

- Docling nên được xem là thành phần bắt buộc cho pipeline mở rộng vì cải thiện mạnh cấu trúc extraction.
- Việc dùng profile `classic_pentest` giúp giảm over-match sang AI/API/Web taxonomy không phù hợp.
- Để tăng accuracy cao hơn nữa, cần mở rộng taxonomy pentest chuyên biệt thay vì chỉ tái sử dụng taxonomy OWASP/NIST. Các nhóm concept nên bổ sung gồm network enumeration, service enumeration, vulnerability scanning, exploitation, Linux privilege escalation, Windows privilege escalation, password attacks, tunneling/pivoting, Active Directory, web exploitation, post-exploitation, cleanup và reporting.

Sau bước đánh giá này, prototype đã thực hiện luôn phần mở rộng taxonomy `classic_pentest` cho tài liệu PEN200/OSCP.

Các concept pentest chuyên biệt được bổ sung:

- `network-port-scanning`
- `service-enumeration`
- `vulnerability-scanning`
- `web-application-attacks`
- `exploit-research-and-adaptation`
- `password-attacks`
- `windows-privilege-escalation`
- `linux-privilege-escalation`
- `port-redirection-and-tunneling`
- `metasploit-framework`
- `active-directory-enumeration`
- `active-directory-attacks`
- `lateral-movement`
- `post-exploitation`

Ngoài việc thêm concept, profile `classic_pentest` cũng được chuyển sang allowlist taxonomy riêng. Cách này tránh việc lấy toàn bộ taxonomy OWASP/NIST vào PEN200, vì một số concept như `authorization-testing` hoặc `logistics` có thể bị match sai từ các cụm như `Access Control Mechanisms` hoặc `Scheduled Tasks`.

Kết quả sau khi mở rộng taxonomy:

- Output: `outputs/redteam-pen200-docling`.
- Active taxonomy total: 22.
- Primary chapters: 20.
- Weak references: 2.
- Missing active taxonomy concepts: 0.
- Concept coverage score: 22/22.
- Evaluator: PASS.
- Stale chapter: 0.

Các chapter chính sau nâng cấp:

- `information-gathering`
- `input-validation-testing`
- `testing-for-weak-cryptography`
- `client-side-testing`
- `information-security-assessment-methodology`
- `final-report`
- `network-port-scanning`
- `service-enumeration`
- `vulnerability-scanning`
- `web-application-attacks`
- `exploit-research-and-adaptation`
- `password-attacks`
- `windows-privilege-escalation`
- `linux-privilege-escalation`
- `port-redirection-and-tunneling`
- `metasploit-framework`
- `active-directory-enumeration`
- `active-directory-attacks`
- `lateral-movement`
- `post-exploitation`

Đánh giá chất lượng sau nâng cấp taxonomy:

- Artifact completeness: khoảng 9/10.
- Safety: khoảng 9/10.
- Traceability/citation: khoảng 8/10.
- Concept selection accuracy: khoảng 8/10.
- Domain labeling accuracy: khoảng 8.2/10.
- Command quality: khoảng 6.5/10.
- Chapter usefulness: khoảng 8/10.
- Overall quality: khoảng 8/10.

Điểm cải thiện quan trọng là output PEN200 không còn chỉ ánh xạ sang taxonomy OWASP/NIST. Hệ thống đã sinh được các chapter phản ánh đúng nội dung pentest/OSCP hơn, gồm scanning, enumeration, exploitation, privilege escalation, tunneling, Metasploit và Active Directory. Đây là bằng chứng cho thấy cơ chế profile-based extension phù hợp với mục tiêu xử lý nhiều loại tài liệu Red Team/Pentest khác nhau.

Sau đó, prototype tiếp tục cải thiện `commands.md`, vì đây là artifact quan trọng với tài liệu kỹ thuật Red Team/Pentest.

Vấn đề ban đầu:

- Parser cũ chỉ hiểu các dòng command đơn giản hoặc code block rõ ràng.
- Docling thường nén prompt, command và output vào cùng một dòng, ví dụ `kali@kali:~$ nmap ... Starting Nmap ...`.
- Vì vậy output ban đầu chỉ có rất ít command hoặc có command bị dính output.

Cải tiến đã thực hiện:

- Nhận diện prompt Linux/Kali, PowerShell, Metasploit và Meterpreter.
- Tách nhiều command trên cùng một dòng.
- Cắt output phổ biến như `Starting Nmap`, `Nmap scan report`, `Serving HTTP`, `payload =>`, `404 page not found`, `VRFY`, `220 mail`, `(UNKNOWN)`.
- Bổ sung danh sách command pentest như `dnsrecon`, `dnsenum`, `nmap`, `nc`, `crackmapexec`, `proxychains`, `msfvenom`, `searchsploit`, `ssh2john`, `hashcat`, `john`, `impacket-*`, `swaks`, `socat`.
- Thêm cơ chế scoring để ưu tiên command pentest-specific thay vì lấy các lệnh Linux cơ bản ở đầu tài liệu.

Kết quả:

- `commands.md` của PEN200 Docling tăng lên 40 command.
- Các command được ưu tiên tốt hơn, gồm whois, host, dnsrecon, nc, nmap, curl, impacket.
- Evaluator: PASS.
- Command quality checks: PASS.
- Full tests: 141 passed.

Đánh giá sau nâng parser:

- Command quality tăng từ khoảng 6.5/10 lên khoảng 8/10.
- Overall PEN200 Docling tăng lên khoảng 8.2/10.

Sau bước này, prototype tiếp tục cải thiện context quanh command:

- Ưu tiên caption `Listing <number> - ...` hoặc `Figure <number> - ...` gần command.
- Bỏ qua các dòng nhiễu như `<!-- image -->`, `Nmap scan report`, `Nmap done`, `Host is up`, `PORT STATE SERVICE`, dòng reference, và output markers.

Ví dụ context tốt hơn:

- `whois 38.100.193.70 -h 192.168.50.251` -> `Whois reverse lookup`.
- `dnsrecon -d megacorpone.com -D ~/list.txt -t brt` -> `Brute forcing hostnames using dnsrecon`.
- `nc -nvv -w 1 -z 192.168.50.152 3388-3390` -> `Using netcat to perform a TCP port scan`.
- `sudo nmap -sS 192.168.50.149` -> `Using nmap to perform a SYN scan`.

Để đánh giá chất lượng định lượng hơn, prototype đã bổ sung benchmark/gold set nhỏ:

- File: `profiles/redteam/benchmarks/gold_set.json`.
- Bao phủ 4 profile tài liệu:
  - `owasp_web`
  - `nist_methodology`
  - `ai_redteam`
  - `classic_pentest`

Mỗi benchmark định nghĩa số concept tối thiểu, concept bắt buộc, số command tối thiểu, nhóm command/tool quan trọng, và điểm rubric tối thiểu.

Evaluator được mở rộng từ PASS/FAIL cấu trúc sang rubric-based evaluation. Các thành phần điểm gồm:

- Coverage score.
- Required concept score.
- Command count score.
- Command term score.
- Citation score.
- Chapter/domain substance score.

Kết quả với PEN200 Docling:

- Rubric score: 100/100 cho `classic_pentest`.
- Required concepts: 15/15.
- Commands: 40/25.
- Command terms: 5/5.
- Benchmark target: PASS.

Prototype cũng cải thiện artifact theo domain:

- `chapters/*.md` có thêm procedure steps riêng cho các concept pentest.
- `workflows.md` sinh workflow riêng cho các concept như network scanning, Linux privilege escalation, tunneling, Active Directory attacks.
- `checklist.md` có thêm phần `Domain-Specific Checks`.

Đánh giá cuối cho PEN200 Docling sau toàn bộ nâng cấp:

- Artifact completeness: khoảng 9/10.
- Safety: khoảng 9/10.
- Traceability/citation: khoảng 8.3/10.
- Concept selection accuracy: khoảng 8.3/10.
- Domain labeling accuracy: khoảng 8.5/10.
- Command quality: khoảng 8.2/10.
- Workflow/checklist usefulness: khoảng 8.3/10.
- Overall quality: khoảng 8.3-8.5/10.

Kết quả kiểm thử cuối:

- Focused Red Team tests: 16 passed.
- Full repository tests: 142 passed.
- Stale chapter check: 0 cho tất cả output đã sinh.

Như vậy, phần mở rộng hiện tại đã hoàn thành đủ các thành phần chính: profile-based generation, Docling requirement, taxonomy theo tài liệu, command parser, citation/coverage, benchmark evaluator, và artifact theo domain Red Team/Pentest.

Sau khi review lại các output OWASP, NIST và OFFSEC AI-300, prototype tiếp tục được cải thiện vì chất lượng nội dung và command ở các tài liệu này chưa đồng đều.

Các vấn đề phát hiện:

- OWASP có command bị cắt sai, ví dụ `host -l` mất domain/name server.
- OWASP có lỗi spacing do Docling, ví dụ `www.example. com`.
- OFFSEC AI-300 có command multiline bị cắt ở dấu `\`.
- OFFSEC AI-300 chưa lấy đủ command vì giới hạn command trước đó còn thấp.
- NIST SP 800-115 gần như không có command thật, vì đây là tài liệu phương pháp luận, không phải lab guide. Do đó NIST nên được đánh giá bằng methodology/workflow completeness thay vì command count.
- Source summary trong chapter còn hơi mỏng vì excerpt trước đó chỉ lấy khoảng 10 dòng.

Các cải tiến đã thực hiện:

- Tăng source excerpt trong mỗi chapter lên khoảng 18 dòng.
- Thêm procedure steps riêng cho OWASP Web Testing concepts.
- Thêm procedure steps riêng cho NIST methodology concepts.
- Thêm procedure steps riêng cho AI Red Team concepts.
- Sửa sanitizer để giữ đúng `host -l www.owasp.org ns1.secure.net`.
- Chuẩn hóa domain bị tách như `. com`, `. org`, `. net`.
- Nối command multiline khi dòng kết thúc bằng `\` hoặc JSON/quote/braces chưa đóng.
- Tăng giới hạn command lên 80.
- Ưu tiên thêm `python3`, `kubectl` và các command liên quan trong scoring.

Kết quả regenerate:

OWASP WSTG:

- Extraction bằng Docling: 224 trang, 149,401 words, 840 heading candidates.
- Found concepts: 12.
- Weak references: 1.
- Commands: 11.
- Bad command markers: 0.
- Rubric score: 100/100.
- Evaluator: PASS.
- Đánh giá: khoảng 8.3-8.5/10.

NIST SP 800-115:

- Extraction bằng Docling: 80 trang, 34,862 words, 16 heading candidates.
- Found concepts: 12.
- Weak references: 0.
- Commands thật: 0, phù hợp với bản chất guideline.
- Rubric score: 100/100.
- Evaluator: PASS.
- Đánh giá: khoảng 8.2-8.4/10 cho methodology artifacts.

OFFSEC AI-300:

- Extraction từ 11 HTML files, 135,698 words, 119 heading candidates.
- Found concepts: 13.
- Weak references: 0.
- Commands: 80.
- Bad command markers: 0.
- Rubric score: 100/100.
- Evaluator: PASS.
- Đánh giá: khoảng 8.4-8.6/10.

Kiểm thử sau cải thiện:

- Focused Red Team tests: 17 passed.
- Full repository tests: 143 passed.
- Stale chapter check: 0 cho OWASP, NIST, OFFSEC AI-300 và PEN200.

Kết luận bổ sung:

- Chất lượng artifact tăng rõ nhất ở phần chapter procedure và workflow/checklist, vì mỗi profile giờ có domain steps riêng.
- Command parser tốt hơn đáng kể với OFFSEC AI-300 nhờ nối multiline và tăng giới hạn command.
- NIST cần được trình bày trong báo cáo như tài liệu methodology, không phải nguồn command.
- Hướng production tiếp theo là thêm chế độ redact secrets cho các command lấy từ lab/offensive courseware và parser request/code block sâu hơn cho OWASP.

PEN200 cũng được chạy lại sau các nâng cấp parser/renderer mới nhất để đảm bảo kết quả đồng bộ với OWASP, NIST và OFFSEC.

Kết quả PEN200 mới nhất:

- Extraction: Docling.
- Pages: 869.
- Words: 269,168.
- Chapters detected: 66.
- Output: `outputs/redteam-pen200-docling`.
- Active profile: `classic_pentest`.
- Found concepts: 20.
- Weak references: 2.
- Commands: 80.
- Bad command markers: 0.
- Stale chapter: 0.
- Rubric score: 100/100.
- Evaluator: PASS.

Các cải thiện mới ảnh hưởng đến PEN200:

- Command limit tăng từ 40 lên 80.
- Chapter summary dài hơn nên nội dung ít sơ sài hơn.
- Lọc nhiễu command tốt hơn, gồm `220 mail`, `Recipient address rejected`, `Host ... not found`, và Python byte-output artifact.
- Sửa các command host bị lặp domain do Docling nén command và output vào cùng dòng.

Đánh giá PEN200 sau bản mới nhất:

- Artifact completeness: khoảng 9/10.
- Safety: khoảng 9/10.
- Traceability/citation: khoảng 8.4/10.
- Concept selection accuracy: khoảng 8.4/10.
- Domain labeling accuracy: khoảng 8.5/10.
- Command quality: khoảng 8.3/10.
- Workflow/checklist usefulness: khoảng 8.3/10.
- Overall quality: khoảng 8.4-8.6/10.

Nhận xét: PEN200 hiện là output mạnh nhất cho nhóm classic pentest vì có taxonomy riêng, nhiều command thực tế, và chapter bao phủ đúng các mảng như scanning, enumeration, exploitation, privilege escalation, tunneling, Metasploit, Active Directory, lateral movement và post-exploitation.
