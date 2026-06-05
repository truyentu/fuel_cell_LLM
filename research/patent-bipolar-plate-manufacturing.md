# Patent Bipolar Plate — Gia Công & Flow Field Design

> **Mục đích:** Hướng dẫn Freedom-to-Operate (FTO) cho sản xuất tấm lưỡng cực PEM fuel cell
> **Phạm vi:** Phương pháp gia công (hollow embossing rolling) + thiết kế kênh dẫn (flow field)
> **Cập nhật:** 2026-06-01

---

## 1. Tổng Quan Rủi Ro Patent

Khi sản xuất thương mại PEM fuel cell, có **6 vùng rủi ro patent** độc lập:

```
Vùng A: Phương pháp gia công bipolar plate (rolling, stamping, hydroforming)
Vùng B: Thiết kế kênh dẫn (flow field channel geometry)
Vùng C: Lớp mạ bảo vệ (PVD coating — xem file pvd-coatings-bipolar-plate.md)
Vùng D: Hệ thống humidification (membrane humidifier design)
Vùng E: H₂ recirculation (ejector geometry)
Vùng F: Startup/shutdown control algorithm — xem file patent-startup-shutdown-control.md
```

> Vi phạm bất kỳ vùng nào đều có thể bị kiện — kể cả khi các vùng còn lại hoàn toàn tự do.

---

## 2. Lớp 1: Phương Pháp Gia Công — Hollow Embossing Rolling

### Định nghĩa
Hollow embossing rolling = cán liên tục tấm inox qua cặp con lăn có hoa văn kênh dẫn, tạo flow field channels theo kiểu "hollow" (rỗng bên trong). Khác với stamping (dập từng tấm), rolling cho phép sản xuất liên tục, tốc độ cao hơn.

### Kết quả FTO Search

#### Đã HẾT HẠN — Tự do sử dụng ✓

| Patent | Chủ sở hữu | Nội dung | Hết hạn |
|---|---|---|---|
| **CN1964114A** | Shanghai Jiao Tong University | Roll forming method cho metal BPP | **2017** (không đóng phí) |
| **CN100423331C** | Shanghai Jiao Tong University | Manufacturing method BPP bằng roll forming | **2018** (không đóng phí) |
| **US7459227B2** | GM Global Technology | Stamped metal BPP (2 half-plates hàn laser) | **Jan 2025** |

#### Còn HIỆU LỰC — Cần tránh ⚠️

| Patent | Chủ sở hữu | Nội dung | Hết hạn |
|---|---|---|---|
| **CN118060387B** | Southwest Petroleum University | **Thiết bị** rolling tích hợp cụ thể (máy móc) | **2044** |
| **US20220242034** | (CN origin) | Roller embossing cho **graphite** plates (không phải SS) | ~2041 |

### Kết luận Lớp 1

```
Phương pháp rolling/hollow embossing tổng quát cho SS bipolar plate
→ Các patent chính đã hết hạn ✓ TỰ DO SỬ DỤNG

Lưu ý: CN118060387B bảo hộ thiết bị máy móc cụ thể, không bảo hộ phương pháp
→ Tự thiết kế máy rolling khác → không vi phạm ✓
```

---

## 3. Lớp 2: Thiết Kế Kênh Dẫn (Flow Field Geometry)

### Tại sao đây là rủi ro lớn hơn?

Dù bạn dùng rolling hay stamping, nếu **hình dạng kênh dẫn** giống patent của Toyota/Honda/GM/Ballard → vẫn vi phạm. Flow field geometry là nơi tập trung nhiều patent nhất trong lĩnh vực fuel cell.

### Các loại flow field cơ bản và tình trạng patent

| Loại | Tình trạng | Ghi chú |
|---|---|---|
| **Serpentine** (kênh rắn lượn) | **Prior art** từ 1990s | Ballard patent gốc đã hết hạn |
| **Parallel** (kênh song song) | **Prior art** | Quá cũ để patent |
| **Interdigitated** (kênh xen kẽ) | **Prior art** | Đã published rộng rãi |
| **Pin-type / mesh** | Phần lớn prior art | Kiểm tra từng design cụ thể |
| **Biomimetic** (lá cây, phổi) | Vùng xám — nhiều paper | Cần kiểm tra từng design |
| **Fractal** (Hilbert, Koch) | Vùng xám — nhiều paper | Cần kiểm tra từng design |
| **Tapered/converging-diverging** | Một số patent còn hiệu lực | Kiểm tra kỹ trước khi dùng |
| **Hybrid interwoven** | **Còn hiệu lực** (US20230082620, 2021) | Tránh |

### Patent flow field còn hiệu lực cần chú ý

| Patent | Chủ sở hữu | Nội dung | Hết hạn |
|---|---|---|---|
| **US20230082620** | (2021) | Hybrid interwoven channel pattern | ~2041 |
| **US20230079046** | (2021) | Method of designing fluid flow field structure | ~2041 |
| **JP5915613B2** | Toyota | Serpentine, groove width 0.2–1.0 mm, depth 0.2–0.8 mm | ~2033 |
| **US10553881B2** | Toyota | Tapered serpentine, cross-section 1.04–1.20 mm | ~2037 |
| **US12027730B2** | Toyota | Parallel wavy channels (Gen 2 Mirai) | ~2041 |
| **US10186718B2** | Honda | Wave-shaped vertical channels (V Flow) | ~2036 |
| **US12525621B2** | Honda | Trapezoidal cross-section flow grooves | ~2044 |
| **US11145887B2** | Honda | Wavy + straight groove combination | ~2039 |
| **US9059442B2** | Honda | Corrugated flow grooves, press-formed SS | ~2034 |
| **US11233261B2** | Hyundai + Kia | Inclined waveform separator, alternating gas/coolant | ~2040 |
| **US12580206B2** | Hyundai + Kia | Through-hole cap structure, manifold transition | ~2044 |
| **CN105680066B** | Hyundai + Kia | Metal foam + segmented reaction zones | ~2035 |
| **CN105006582B** | Hyundai + Kia | Diagonal manifold + progressive channel length | ~2035 |
| **US20240204214A1** | Hyundai + Kia | Asymmetric graduated diffusion ribs (pending) | ~2044 |

---

## 4. Chi Tiết Flow Field Theo Nhà Sản Xuất

### 4.1 Toyota — Mirai Gen 1 & Gen 2

#### Thiết kế thực tế
| Thế hệ | Vật liệu | Loại flow field | Đặc điểm |
|---|---|---|---|
| **Mirai Gen 1** (2014–2020) | Titanium | 3D fine-mesh cathode | Lưới 3D tạo turbulence, thoát nước tốt |
| **Mirai Gen 2** (2021+) | Titanium | Straight parallel + periodic narrowing | Kênh thẳng, thu hẹp định kỳ để tăng vận tốc |

#### Patent còn hiệu lực — cần tránh

| Patent | Nội dung claims cụ thể | Hết hạn |
|---|---|---|
| **JP5915613B2** | Serpentine với groove width **0.2–1.0 mm**, depth **0.2–0.8 mm**, rib width **0.2–1.0 mm** | ~2033 |
| **US10553881B2** | Tapered serpentine: cross-section **1.04–1.20 mm**, taper angle tạo converging-diverging flow | ~2037 |
| **US12027730B2** | Parallel wavy channels: kênh thẳng có sóng định kỳ, titanium separator | ~2041 |

#### Vùng an toàn (không bị Toyota patent)
```
✓ Serpentine cơ bản với channel width > 1.0 mm hoặc < 0.2 mm
✓ Channel depth > 0.8 mm hoặc < 0.2 mm
✓ Không dùng titanium separator (dùng SS316L thay thế)
✓ Không dùng 3D mesh structure
✓ Không dùng periodic narrowing (partially narrow channel)
```

---

### 4.2 Honda — Clarity FCEV / CR-V e:FCEV

#### Thiết kế thực tế — "V Flow"
Honda dùng thiết kế **V Flow** đặc trưng:
- Kênh dẫn **hình sóng (wave-shaped)** theo chiều dọc (vertical)
- Tận dụng **trọng lực** để thoát nước (gravity-assisted drainage)
- Tấm inox dập (press-formed SS), hàn laser 2 half-plates
- Mặt cắt kênh hình **thang (trapezoidal)**

#### Patent còn hiệu lực — cần tránh

| Patent | Nội dung claims cụ thể | Hết hạn |
|---|---|---|
| **US10186718B2** | Wave-shaped channels theo chiều dọc, crest/trough tạo góc với horizontal để thoát nước | ~2036 |
| **US12525621B2** | Mặt cắt kênh **hình thang (trapezoidal)**: đáy rộng hơn miệng, tỷ lệ cụ thể | ~2044 |
| **US11145887B2** | Kết hợp wavy groove + straight groove trên cùng tấm | ~2039 |
| **US9059442B2** | Corrugated flow grooves trên SS press-formed plate, laser-welded | ~2034 |

#### Vùng an toàn (không bị Honda patent)
```
✓ Kênh nằm ngang (horizontal) thay vì dọc (vertical)
✓ Mặt cắt hình chữ nhật hoặc bán tròn (không phải trapezoidal)
✓ Không kết hợp wavy + straight trên cùng tấm
✓ Serpentine hoặc parallel thuần túy (không phải wave-shaped vertical)
```

---

### 4.3 Hyundai — NEXO / Tucson FCEV

#### Thiết kế thực tế
- Stack NEXO (2018): 95 kW gross, **440 cells**, inox dập
- Hyundai dùng **multi-pass serpentine hoặc parallel-serpentine hybrid**
- Đặc điểm nổi bật: tích hợp **metal foam (porous body)** vào separator để phân phối khí đều
- Cấu trúc dual-plate hàn laser (anode plate + cathode plate + coolant giữa)

#### Patent còn hiệu lực — cần tránh

| Patent | Nội dung claims cụ thể | Hết hạn |
|---|---|---|
| **US11233261B2** | Waveform separator với crest/trough **nghiêng (inclined)** so với horizontal, kênh gas/coolant xen kẽ | ~2040 |
| **US12580206B2** | Through-hole cap: top cap che ≥50% diện tích lỗ, side holes giảm áp suất | ~2044 |
| **CN105680066B** | Metal foam + segmented reaction zones, connector elements hàn laser | ~2035 |
| **CN105006582B** | Diagonal manifold + channel length tăng dần từ inlet → outlet | ~2035 |
| **US20240204214A1** | Diffusion ribs bất đối xứng (asymmetric) tại vùng inlet/outlet, thickness và gap thay đổi dần | ~2044 |

#### Vùng an toàn (không bị Hyundai patent)
```
✓ Kênh thẳng (non-inclined) — không nghiêng crest/trough
✓ Không dùng metal foam / porous body insert
✓ Manifold thẳng (không diagonal)
✓ Channel length đồng đều (không tăng dần)
✓ Diffusion ribs đồng đều (không asymmetric graduated)
✓ Mặt cắt kênh cụ thể: rectangular, semicircular — không bị claim
✓ Channel width/depth/rib width cụ thể: không có active US patent nào của Hyundai claim range số học
```

> **Lưu ý:** Hyundai có nhiều patent KR (Hàn Quốc) tại KIPRIS chưa được index đầy đủ trên Google Patents. Nếu xuất khẩu sang Hàn Quốc → cần search thêm KIPRIS.

---

### 4.4 Bảng Tổng Hợp — Vùng Tránh Theo Nhà Sản Xuất

| Tính năng | Toyota | Honda | Hyundai | Trạng thái |
|---|---|---|---|---|
| Serpentine width 0.2–1.0 mm | ⚠️ JP5915613 | — | — | Tránh range này |
| Serpentine depth 0.2–0.8 mm | ⚠️ JP5915613 | — | — | Tránh range này |
| Tapered/converging channel | ⚠️ US10553881 | — | — | Tránh |
| Parallel wavy (periodic narrowing) | ⚠️ US12027730 | — | — | Tránh |
| Wave-shaped vertical channels | — | ⚠️ US10186718 | — | Tránh |
| Trapezoidal cross-section | — | ⚠️ US12525621 | — | Tránh |
| Wavy + straight combination | — | ⚠️ US11145887 | — | Tránh |
| Inclined waveform separator | — | — | ⚠️ US11233261 | Tránh |
| Metal foam integration | — | — | ⚠️ CN105680066 | Tránh |
| Diagonal manifold | — | — | ⚠️ CN105006582 | Tránh |
| **Serpentine cơ bản, width > 1.0 mm** | ✓ An toàn | ✓ An toàn | ✓ An toàn | **Dùng được** |
| **Parallel cơ bản, rectangular cross-section** | ✓ An toàn | ✓ An toàn | ✓ An toàn | **Dùng được** |
| **Interdigitated cơ bản** | ✓ An toàn | ✓ An toàn | ✓ An toàn | **Dùng được** |

---

## 5. Chiến Lược Tránh Patent Flow Field

### Chiến lược A: Dùng Prior Art (An toàn nhất)

**Nguyên tắc:** Patent chỉ bảo hộ **implementation cụ thể** — tỷ lệ channel/rib, góc cạnh, pattern đặc biệt. Không ai sở hữu khái niệm "kênh rắn lượn" nói chung.

```
Serpentine cơ bản + tối ưu thông số theo CFD của riêng bạn
→ Hoàn toàn tự do ✓
```

Thông số bạn tự chọn (không bị patent) — đã loại trừ range của Toyota/Honda/Hyundai:
- Channel width: **> 1.0 mm** (tránh 0.2–1.0 mm của Toyota JP5915613)
- Channel depth: **> 0.8 mm** (tránh 0.2–0.8 mm của Toyota JP5915613)
- Rib width: **> 1.0 mm** (tránh range của JP5915613)
- Mặt cắt: **hình chữ nhật hoặc bán tròn** (tránh trapezoidal của Honda US12525621)
- Hướng kênh: **nằm ngang hoặc serpentine** (tránh vertical wave của Honda)
- Số lượng passes, góc bo cạnh: tự do chọn

### Chiến lược B: Toyota Royalty-Free Patents

Toyota năm 2015 mở **5,680 patent** miễn phí, gia hạn đến **2030**, bao gồm nhiều flow field design và stack technology.

- Tra cứu: [Toyota Fuel Cell Patent License](https://www.toyota.com/usa/operations/fcv-patents)
- Điều kiện: Miễn phí cho xe chạy hydrogen, có thể áp dụng cho stationary systems
- **Đây là nguồn lớn nhất để dùng hợp pháp không tốn phí**

### Chiến lược C: Design Around

Đọc **claims** (không phải abstract) của patent đang còn hiệu lực, xác định thông số cụ thể được bảo hộ, thiết kế ngoài vùng đó.

**Ví dụ thực tế:**
```
Patent của GM: "serpentine channel với rib/channel ratio = 0.8–1.2"
→ Bạn dùng ratio = 0.5 hoặc 1.5 → không vi phạm claim đó ✓

Patent X: "channel depth 0.3–0.5 mm với specific taper angle 5–15°"
→ Bạn dùng depth 0.7 mm, không taper → không vi phạm ✓
```

**Quy trình design around:**
1. Tìm patent liên quan trên Google Patents / Espacenet
2. Đọc kỹ phần **Claims** (không phải Description)
3. Xác định thông số số học cụ thể trong claims
4. Thiết kế ngoài range đó
5. Document lại lý do → bằng chứng good faith

### Chiến lược D: Publish Paper Trước (Tự tạo Prior Art)

Nếu bạn phát triển design mới:
1. **Publish paper** (kể cả preprint trên arXiv) trước khi sản xuất
2. Design đó trở thành **prior art** công khai
3. Người khác **không thể patent** design của bạn nữa
4. Bạn cũng không cần patent — chỉ cần publish là đủ để bảo vệ

> Đây là chiến lược của nhiều công ty nhỏ và startup: publish để "defensive publication", không tốn phí patent nhưng vẫn bảo vệ được quyền sử dụng.

---

## 5. Quy Trình FTO Thực Tế

```
Bước 1: Chọn serpentine hoặc parallel cơ bản
        → Prior art, hoàn toàn tự do ✓

Bước 2: Kiểm tra Toyota royalty-free list
        → Nếu design phù hợp → dùng luôn, miễn phí ✓

Bước 3: Tối ưu thông số bằng CFD simulation
        → Channel width, depth, rib width, số passes
        → Miễn không copy exact ratio từ patent còn hiệu lực ✓

Bước 4: Search Google Patents với keywords:
        "bipolar plate" + "flow field" + "serpentine" (hoặc loại bạn chọn)
        → Filter: Status = Active, Country = US + EP + CN
        → Đọc claims của top 10 kết quả liên quan nhất

Bước 5: Document lại
        → Ghi rõ: "Design của chúng tôi khác patent X ở điểm Y"
        → Lưu hồ sơ → bằng chứng good faith nếu bị kiện

Bước 6 (tùy chọn): Thuê luật sư IP làm FTO analysis chính thức
        → Chi phí: ~$5,000–20,000
        → Cần thiết nếu sản xuất quy mô lớn hoặc xuất khẩu
```

---

## 6. Tóm Tắt Rủi Ro Theo Lớp

| Lớp | Rủi ro | Chiến lược |
|---|---|---|
| **Gia công (rolling)** | **Thấp** — patent chính đã hết hạn | Tự do dùng rolling method |
| **Flow field geometry** | **Trung bình** — prior art rộng nhưng có patent mới | Dùng serpentine cơ bản + tối ưu CFD |
| **PVD coating** | **Cao** — nhiều patent còn hiệu lực | Xem file pvd-coatings-bipolar-plate.md |

---

## 7. Nguồn Tham Khảo

- [CN1964114A](https://patents.google.com/patent/CN1964114A/en) — Shanghai Jiao Tong, roll forming BPP (hết hạn 2017)
- [CN100423331C](https://patents.google.com/patent/CN100423331C/en) — Shanghai Jiao Tong, roll forming method (hết hạn 2018)
- [US7459227B2](https://patents.justia.com/patent/7459227) — GM, stamped metal BPP (hết hạn Jan 2025)
- [CN118060387B](https://patents.google.com/patent/CN118060387B/en) — Southwest Petroleum Univ., rolling device (còn hiệu lực đến 2044)
- [US20230082620](https://patents.justia.com/patent/20230082620) — Hybrid interwoven flow field (còn hiệu lực)
- [US20230079046](https://patents.justia.com/patent/20230079046) — Method of designing flow field (còn hiệu lực)
- Toyota Fuel Cell Patent License — toyota.com/usa/operations/fcv-patents
- ResearchGate: [Flow Field Patterns for PEM Fuel Cells](https://www.researchgate.net/publication/339358901_Flow_Field_Patterns_for_Proton_Exchange_Membrane_Fuel_Cells) — review paper, prior art reference
- MDPI: [Manufacturing of Metallic Bipolar Plate Channels by Rolling](https://www.mdpi.com/2504-4494/3/2/48)
- MDPI: [Production of Metallic BPP by Incremental Hollow Embossing Using Rollers](https://www.mdpi.com/2673-4591/26/1/15)

### Toyota Flow Field Patents
- [JP5915613B2](https://patents.google.com/patent/JP5915613B2/en) — Toyota, serpentine groove width 0.2–1.0 mm, depth 0.2–0.8 mm (~2033)
- [US10553881B2](https://patents.google.com/patent/US10553881B2/en) — Toyota, tapered serpentine cross-section 1.04–1.20 mm (~2037)
- [US12027730B2](https://patents.google.com/patent/US12027730B2/en) — Toyota, parallel wavy channels Gen 2 Mirai (~2041)

### Honda Flow Field Patents
- [US10186718B2](https://patents.google.com/patent/US10186718B2/en) — Honda, wave-shaped vertical channels V Flow (~2036)
- [US12525621B2](https://patents.google.com/patent/US12525621B2/en) — Honda, trapezoidal cross-section flow grooves (~2044)
- [US11145887B2](https://patents.google.com/patent/US11145887B2/en) — Honda, wavy + straight groove combination (~2039)
- [US9059442B2](https://patents.google.com/patent/US9059442B2/en) — Honda, corrugated flow grooves press-formed SS (~2034)

### Hyundai Flow Field Patents
- [US11233261B2](https://patents.google.com/patent/US11233261B2/en) — Hyundai+Kia, inclined waveform separator (~2040)
- [US12580206B2](https://patents.google.com/patent/US12580206B2/en) — Hyundai+Kia, through-hole cap manifold structure (~2044)
- [CN105680066B](https://patents.google.com/patent/CN105680066B/en) — Hyundai+Kia, metal foam + segmented reaction zones (~2035)
- [CN105006582B](https://patents.google.com/patent/CN105006582B/en) — Hyundai+Kia, diagonal manifold + progressive channel length (~2035)
- [US20240204214A1](https://patents.google.com/patent/US20240204214A1/en) — Hyundai+Kia, asymmetric graduated diffusion ribs (pending ~2044)
