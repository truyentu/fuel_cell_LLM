# Lớp Mạ PVD cho Tấm Lưỡng Cực (Bipolar Plate) — PEM Hydrogen Fuel Cell

> **Nguồn:** DOE Technical Targets, RSC, MDPI Coatings, Springer, IHI/Hauzer, Ionbond, Naco Technologies
> **Cập nhật:** 2026-06-01

---

## 1. Tại Sao Cần Mạ?

Tấm lưỡng cực bằng Inox 316L (SS316L) **không thể dùng trực tiếp** vì:

| Thông số | DOE yêu cầu | SS316L trần | Kết quả |
|---|---|---|---|
| ICR (điện trở tiếp xúc) | < 10 mΩ·cm² | ~155 mΩ·cm² | ❌ Thất bại 15× |
| Mật độ dòng ăn mòn | < 1 µA/cm² | ~1,170 µA/cm² | ❌ Thất bại 1,000× |

**ICR** (Interfacial Contact Resistance) = điện trở tại bề mặt tiếp xúc giữa tấm lưỡng cực và GDL.
Càng thấp → tổn thất điện càng ít → hiệu suất pin càng cao.

Môi trường hoạt động rất khắc nghiệt:
- Dung dịch mô phỏng: **0.5M H₂SO₄ + 2 ppm HF**, pH ~2–3
- Điện thế: −0.1 V (cực âm) đến +0.6 V (cực dương) vs NHE
- Nhiệt độ: 60–80°C liên tục

---

## 2. DOE Technical Targets (Mục Tiêu Kỹ Thuật)

| Thông số | DOE 2020/2025 Target |
|---|---|
| ICR | **< 10 mΩ·cm²** tại 140 N/cm² |
| Corrosion current (cực âm) | **< 1 µA/cm²**, không có active peak |
| Corrosion current (cực dương) | **< 1 µA/cm²** |
| Chi phí tấm lưỡng cực | **$3/kWnet** |
| Độ dẫn điện | > 100 S/cm |
| Độ thấm H₂ | < 1.3×10⁻¹⁴ std cm³/(s·cm²·Pa) |

---

## 3. Các Lớp Mạ Phổ Biến & Được Chọn

### 3.1 TiN — Titanium Nitride ⭐ Phổ biến nhất trong nghiên cứu

**Thông số kỹ thuật:**

| Thông số | Giá trị |
|---|---|
| Thành phần | TiN |
| Phương pháp | Cathodic Arc Deposition (CAD), DC Magnetron Sputtering |
| Độ dày | 0.5–2 µm (sputtering) / 4 µm (CAD) |
| ICR | ~8–10 mΩ·cm² → đạt DOE |
| Ăn mòn | < 1 µA/cm² → đạt DOE |
| Độ cứng | **20–25 GPa** (2000–2500 HV) |
| Góc tiếp xúc nước | ~30–60° (ưa nước) |
| Màu sắc | Vàng đặc trưng |

**Ưu điểm:**
- Dữ liệu nghiên cứu nhiều nhất, dễ so sánh
- Màu vàng → dễ kiểm tra bằng mắt
- Đạt cả 2 mục tiêu DOE (ICR + ăn mòn)
- Bám dính tốt khi có lớp Ti interlayer

**Nhược điểm:**
- Lỗ kim (pinhole) → ăn mòn substrate theo thời gian
- CAD cần 4 µm → tốn vật liệu, tăng chi phí
- Suy giảm trong môi trường cực âm (−0.1 V) dài hạn

**Biến thể cải tiến:**
- **Ti/TiN multilayer** (xen kẽ): ICR thấp hơn TiN đơn lớp, ít pinhole hơn
- **TiN–Ag** (pha bạc): ICR = 4.18–4.81 mΩ·cm², ăn mòn = 0.29–0.68 µA/cm²

---

### 3.2 CrN và Biến Thể — Chromium Nitride ⭐ ICR tốt hơn TiN

**Thông số kỹ thuật:**

| Thông số | CrN | CrAlN | CrTiN | CrMoCN |
|---|---|---|---|---|
| Phương pháp | Magnetron sputtering, Arc | Multi-arc ion plating | Multi-arc ion plating | Magnetron sputtering |
| Độ dày | 1–3 µm | 1–3 µm | 1–3 µm | 1–3 µm |
| ICR | < TiN (tốt hơn) | Tốt hơn CrN | Tốt hơn CrN | **7.54 mΩ·cm²** |
| Ăn mòn | < 1 µA/cm² | < 1 µA/cm² | < 1 µA/cm² | Xuất sắc |
| Độ cứng | 18–22 GPa | **25–30 GPa** | 22–28 GPa | ~22 GPa |

**So sánh trực tiếp TiN vs CrN** (cùng substrate SS410):
- CrN có ICR **thấp hơn** TiN
- CrN có bề mặt **mịn hơn** TiN
- → CrN được ưu tiên hơn TiN trong nhiều ứng dụng thực tế

**Biến thể nổi bật:**
- **CrAlN**: Cứng nhất trong nhóm Cr (~30 GPa), chịu nhiệt tốt
- **CrMoCN**: Thêm Mo và C → ICR = 7.54 mΩ·cm², gần sát giới hạn DOE
- **Cr/CrN multilayer**: Cải thiện ăn mòn 100× so với SS316L trần

---

### 3.3 DLC / a-C — Diamond-Like Carbon ⭐⭐ Ứng viên hàng đầu sản xuất ô tô

**Thông số kỹ thuật:**

| Thông số | Giá trị |
|---|---|
| Thành phần | Amorphous carbon (sp2/sp3 hybrid) |
| Phương pháp | Magnetron Sputtering, PECVD, **HiPIMS** |
| Độ dày | **< 300 nm** (mỏng nhất trong tất cả) |
| ICR | << 10 mΩ·cm² sau 500h AST → đạt DOE |
| Ăn mòn | Thấp, ổn định |
| Độ cứng | 15–40 GPa (tùy tỷ lệ sp3/sp2) |
| Góc tiếp xúc | Điều chỉnh được (60–90°) |
| Kim loại quý | **Không có** |

**Ưu điểm:**
- **Mỏng nhất** (< 300 nm) → tiết kiệm vật liệu nhất
- Không dùng kim loại quý → chi phí thấp
- Có thể sản xuất roll-to-roll → phù hợp sản xuất đại trà
- Góc tiếp xúc điều chỉnh được → tối ưu quản lý nước

**Nhược điểm:**
- Cần thiết kế interlayer cẩn thận để bám dính
- **Pha nitơ (N-DLC) làm GIẢM** cả ICR lẫn chống ăn mòn (nghiên cứu 2025 — ngược với báo cáo cũ)
- DLC giàu sp3 có thể cách điện → cần kiểm soát tỷ lệ sp2/sp3

**Biến thể:**
- **a-C:Cr (CrCx)**: Pha Cr → ICR thấp nhất trong nhóm carbon (sp2-C cao)
- **a-C:Cr:Ti**: Pha cả Cr và Ti → cải thiện bám dính
- **Cr/C multilayer**: Giảm passive current density ≥ 2× so với SS316L

**Thương mại hóa:**
> **Hauzer Technocoating (IHI Group)** — đã phát triển và thương mại hóa DLC < 300 nm cho BPP ô tô sản xuất đại trà.

---

### 3.4 Au — Vàng (Benchmark tham chiếu)

**Thông số kỹ thuật:**

| Thông số | Giá trị |
|---|---|
| Thành phần | Au (vàng nguyên chất) |
| Phương pháp | PVD sputtering, electrodeposition |
| Độ dày | > 10 nm (tối thiểu cho chống ăn mòn) |
| ICR | **0.9 mΩ·cm²** (flat, 60 N/cm²) / **6.3 mΩ·cm²** (formed BPP) |
| Ăn mòn | **< 1 µA/cm²** tại 0.8 V/NHE |
| Độ cứng | ~200 HV (mềm) |

**Đặc điểm:**
- Vật liệu kim loại **duy nhất** đạt cả 2 mục tiêu DOE (ICR + ăn mòn) theo RSC 2009
- ICR tốt nhất tuyệt đối trong tất cả các lớp mạ
- **Không dùng được cho sản xuất đại trà** vì chi phí quá cao

**Công nghệ DOT (Ionbond/IHI):**
Rải Au/Pt dạng hạt nhỏ (chỉ phủ **2–10% diện tích**) trên lớp Ti/TiO₂ barrier → giảm lượng kim loại quý nhưng vẫn đạt ICR < 10 mΩ·cm².

---

### 3.5 ZrN — Zirconium Nitride ⚠️ Cẩn thận: thất bại dài hạn

| Thông số | Giá trị |
|---|---|
| Phương pháp | PVD magnetron sputtering |
| Độ dày | 1–3 µm |
| ICR | **THẤT BẠI** dài hạn |
| Ăn mòn | Đạt DOE ngắn hạn |
| Độ cứng | 20–25 GPa |

**Vấn đề:** Bề mặt bị oxy hóa thành **ZrO₂** (cách điện) → ICR tăng theo thời gian → không đạt DOE dài hạn.

**Giải pháp:** **ZrON (Zr₂N₂O)** qua PEALD — kết hợp độ bền ăn mòn của ZrO₂ với độ dẫn của ZrN → ICR ổn định hơn.

---

### 3.6 Naco BN — Bimetallic Nitride ⭐⭐ Dẫn đầu thương mại hiện tại

| Thông số | Giá trị |
|---|---|
| Thành phần | Bimetallic nitride (độc quyền, không kim loại quý) |
| Cấu trúc | 3 lớp: adhesion / nitride chính / top layer dẫn điện |
| Phương pháp | PVD magnetron sputtering |
| Độ dày | < 300 nm |
| ICR | **< 1 mΩ·cm²** (10× tốt hơn DOE) |
| Ăn mòn | Xuất sắc |

**Xếp hạng #1** trong test độc lập về hiệu suất và độ bền.

---

### 3.7 High-Entropy Nitride (HEN) — Thế hệ mới

| Thông số | Giá trị |
|---|---|
| Thành phần | (TiVCrNbMo)N — 5 nguyên tố |
| Phương pháp | Arc evaporation / sputtering |
| Độ dày | 1–3 µm |
| ICR | Thấp |
| Ăn mòn | Tốt hơn TiN thuần |
| Độ cứng | **> 30 GPa** (cứng nhất) |

Hướng nghiên cứu mới, chưa thương mại hóa rộng rãi.

---

## 4. Bảng So Sánh Tổng Hợp

| Lớp mạ | Độ dày | ICR (mΩ·cm²) | Ăn mòn | Độ cứng | Kim loại quý | DOE | Thương mại |
|---|---|---|---|---|---|---|---|
| TiN | 0.5–4 µm | ~8–10 | ✅ | 20–25 GPa | Không | ✅ | Rộng rãi |
| CrN | 1–3 µm | < TiN | ✅ | 18–22 GPa | Không | ✅ | Rộng rãi |
| CrAlN | 1–3 µm | Tốt | ✅ | 25–30 GPa | Không | ✅ | Có |
| CrMoCN | 1–3 µm | **7.54** | ✅ | ~22 GPa | Không | ✅ | Nghiên cứu |
| **DLC (a-C)** | **< 300 nm** | << 10 | ✅ | 15–40 GPa | Không | ✅ | **Hauzer/IHI** |
| a-C:Cr | 1–2 µm | Thấp nhất C | ✅ | 15–20 GPa | Không | ✅ | Nghiên cứu |
| Au | > 10 nm | **0.9** | ✅ | ~200 HV | **Có** | ✅ | Lab/DOT |
| ZrN | 1–3 µm | ❌ dài hạn | ✅ ngắn hạn | 20–25 GPa | Không | ❌ | Không khuyến nghị |
| ZrON | 100–300 nm | Ổn định | ✅ | ~20 GPa | Không | ✅ | Nghiên cứu |
| **Naco BN** | **< 300 nm** | **< 1** | ✅ | N/A | Không | ✅✅ | **#1 thương mại** |
| HEN (TiVCrNbMo)N | 1–3 µm | Thấp | ✅ | **> 30 GPa** | Không | ✅ | Nghiên cứu |

---

## 5. Ai Dùng Gì Trong Thực Tế

| Ứng dụng | Lớp mạ | Lý do |
|---|---|---|
| Nghiên cứu phổ biến nhất | TiN, CrN | Dữ liệu nhiều, dễ so sánh |
| Sản xuất ô tô (Hauzer/IHI) | **DLC < 300 nm** | Mỏng nhất, không kim loại quý, scalable |
| Benchmark phòng lab | **Au** | ICR tốt nhất tuyệt đối |
| Thương mại hiện tại (top) | **Naco BN** | ICR < 1 mΩ·cm², không kim loại quý |
| Tránh dùng | ZrN đơn lớp | ICR thất bại dài hạn do ZrO₂ |

---

## 6. Lưu Ý Quan Trọng

1. **ICR đo tại 140 N/cm²** — áp lực lắp ráp stack thực tế. Đo ở áp lực khác sẽ cho kết quả khác.
2. **AST (Accelerated Stress Test)** — test 500h+ mới đánh giá được độ bền thực sự. Nhiều lớp mạ đạt DOE ban đầu nhưng suy giảm sau AST.
3. **N-DLC (DLC pha nitơ)** — nghiên cứu 2025 xác nhận làm **giảm** cả ICR lẫn chống ăn mòn. Không nên dùng.
4. **ZrN** — chỉ đạt DOE ngắn hạn. Dài hạn thất bại do oxy hóa bề mặt.
5. **Pinhole** — lỗ kim trong lớp mạ là nguyên nhân chính gây ăn mòn substrate dài hạn. Multilayer giảm thiểu vấn đề này.

---

## 7. Nguồn Tham Khảo

- DOE Technical Targets for PEM Fuel Cell Components — energy.gov
- RSC 2009 — "Metal separator plates for PEM fuel cells" — comprehensive review
- MDPI Coatings 2023 — TiN/a-C double layer on SS316L
- MDPI Sensors 2022 — TiN vs CrN comparison on SS410
- AVS Journal 2024 — CrN, CrAlN, CrTiN comparison
- Springer 2023 — CrMoCN coating
- SSRN 2025 — N-DLC study (nitrogen doping counterproductive)
- IHI/Hauzer — DLC commercial coating for automotive BPP
- IHI/Ionbond — DOT technology (Au/Pt sparse coating)
- Naco Technologies — Naco BN independent test results
- MDPI Applied Sciences 2019 — TiNb and TiNbN coatings
- University of Alberta thesis — ZrN/ZrON PEALD study
