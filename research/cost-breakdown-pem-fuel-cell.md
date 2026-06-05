# Chi Phí PEM Hydrogen Fuel Cell — Cost Breakdown Reference

> **Nguồn chính:** DOE Hydrogen Program Record #17007 (2017) — "Fuel Cell System Cost 2017"
> **Tác giả:** Strategic Analysis Inc. + Argonne National Laboratory
> **Hệ thống tham chiếu:** 80 kWnet automotive PEM fuel cell system
> **Cập nhật:** 2026-06-01

---

## 1. Định Nghĩa: $/kWnet

**$/kWnet** = đô la trên mỗi kilowatt điện **thực xuất** (net electrical output).

```
Stack tạo ra (gross):     ~88 kW
Máy nén khí:              ~5 kW  ┐
Bơm nước/làm mát:         ~2 kW  ├─ Parasitic loads (tự tiêu)
Điện tử + phụ trợ:        ~1 kW  ┘
─────────────────────────────────
Net output:               ~80 kW  ← đây là kWnet
```

> Dùng kWnet thay vì kWgross vì phản ánh đúng giá trị thực tế người dùng nhận được.

---

## 2. DOE Cost Targets

| Mục tiêu | Chi phí |
|---|---|
| DOE 2020 Target | **$40/kWnet** |
| DOE Ultimate Target | **$30/kWnet** |
| Thực tế 2017 (500k xe/năm) | ~$45/kWnet |
| Thực tế 2017 (1,000 xe/năm) | ~$179/kWnet |

---

## 3. Chi Phí Hệ Thống Theo Sản Lượng

Hệ thống 80 kWnet — sản xuất ô tô:

| Sản lượng (xe/năm) | Chi phí ($/kWnet) | Ghi chú |
|---|---|---|
| 1,000 | **$179** | Sản xuất nhỏ, chi phí cao |
| 10,000 | ~$100 | Bắt đầu có economy of scale |
| 100,000 | ~$53 | Sản xuất đại trà |
| 500,000 | **$45** | Quy mô ô tô toàn cầu |

> **Nhận xét:** Chi phí giảm ~4× khi tăng sản lượng từ 1,000 → 500,000 xe/năm.
> Đây là lý do tại sao hydrogen fuel cell chỉ cạnh tranh được ở quy mô sản xuất lớn.

---

## 4. Breakdown Chi Phí Stack (tại 100,000 xe/năm)

Tổng chi phí stack: ~$22/kWnet

| Thành phần | Chi phí ($/kWnet) | Tỷ lệ (%) | Ghi chú |
|---|---|---|---|
| **Tấm lưỡng cực (Bipolar Plates)** | **$8.4** | **38%** | Thành phần đắt nhất |
| **GDL + Electrode** | **$7.0** | **32%** | Gas Diffusion Layer + lớp xúc tác |
| **Màng Nafion (PEM)** | **$2.6** | **12%** | PFSA polymer membrane |
| **Xúc tác Platinum** | **$2.4** | **11%** | Pt loading 0.125 mg/cm² |
| Các thành phần khác | ~$1.6 | ~7% | Gasket, end plate, hardware |

```
Bipolar Plates  ████████████████████████████████████  38%
GDL + Electrode ████████████████████████████          32%
Nafion Membrane ████████████                          12%
Platinum        ███████████                           11%
Khác            ███                                    7%
```

> **Lưu ý quan trọng:** Tấm lưỡng cực (38%) đắt hơn platinum (11%) trong tổng chi phí stack.
> Đây là lý do tại sao tối ưu hóa lớp mạ PVD cho bipolar plate có tác động lớn hơn việc giảm Pt loading.

---

## 5. Chi Tiết Chi Phí Platinum

| Thông số | Giá trị |
|---|---|
| Pt loading (lab state-of-art 2017) | **0.125 mg/cm²** |
| Pt loading (Toyota Mirai thương mại) | ~0.3–0.4 mg/cm² |
| Tổng Pt/stack (lab) | **~10 g/stack** |
| Tổng Pt/stack (Toyota Mirai) | **~30 g/stack** |
| Giá tham chiếu Pt | **~$1,500/troy oz (~$48/gram)** |
| Chi phí Pt (lab, 10g) | ~$480/stack (~$6/kW) |
| Chi phí Pt (Mirai, 30g) | ~$1,440/stack (~$18/kW) |
| Chi phí Pt trong DOE record | **$2.4/kWnet** tại 100k xe/năm |

**Tại sao DOE record thấp hơn tính toán đơn giản?**
- DOE dùng Pt loading 0.125 mg/cm² (lab tối ưu, không phải thương mại)
- Giá Pt trong mô hình có thể khác giá spot
- Economies of scale trong mua nguyên liệu

---

## 6. Chi Tiết Chi Phí Tấm Lưỡng Cực

Tấm lưỡng cực chiếm **38% chi phí stack** — thành phần đắt nhất.

| Loại vật liệu | Chi phí tương đối | Ưu điểm | Nhược điểm |
|---|---|---|---|
| Graphite nguyên khối | Cao nhất | Ổn định, không cần mạ | Nặng, dày, gia công chậm |
| Composite (graphite + polymer) | Trung bình | Nhẹ hơn graphite | Độ dẫn thấp hơn |
| **Inox 316L + PVD coating** | **Thấp nhất** | Mỏng, nhẹ, dập được | Cần lớp mạ bảo vệ |
| Titanium + coating | Trung bình-cao | Nhẹ, bền | Ti đắt hơn inox |

**Chi phí lớp mạ PVD** (ước tính trong tổng $8.4/kW):
- Vật liệu inox: ~40–50%
- Gia công dập/tạo hình kênh: ~30–35%
- Lớp mạ PVD: ~15–25%
- Assembly: ~5–10%

---

## 7. Balance of Plant (BOP) — Hệ Thống Phụ Trợ

Tổng chi phí hệ thống = Stack + BOP + Assembly

| Hạng mục | Chi phí ($/kWnet) tại 100k xe/năm |
|---|---|
| Stack | ~$22 |
| Air supply (máy nén khí) | ~$10–12 |
| Thermal management (làm mát) | ~$5–7 |
| H₂ supply & humidification | ~$4–6 |
| Power electronics (DC/DC) | ~$5–7 |
| Assembly & testing | ~$3–5 |
| **Tổng hệ thống** | **~$53** |

---

## 8. So Sánh Với Các Năm Khác

| Năm | Chi phí ($/kWnet) tại 500k xe/năm | Nguồn |
|---|---|---|
| 2006 | ~$108 | DOE estimate |
| 2012 | ~$47 | DOE Program Record |
| 2017 | **~$45** | DOE Record #17007 |
| 2020 target | $40 | DOE target |
| Ultimate target | $30 | DOE target |

> Tiến bộ chủ yếu đến từ: giảm Pt loading, cải thiện màng Nafion, tối ưu bipolar plate.

---

## 9. Chi Phí Cho Hệ Thống Nhỏ Hơn (Vài kW — Vài Chục kW)

DOE Record #17007 tập trung vào 80 kW automotive. Với hệ thống nhỏ hơn:

| Công suất | Ứng dụng | Chi phí ước tính ($/kWnet) | Ghi chú |
|---|---|---|---|
| 1–5 kW | Portable, backup power | $500–2,000 | Sản lượng thấp, không có economy of scale |
| 5–25 kW | Forklift, small vehicle | $200–500 | Sản lượng trung bình |
| 25–80 kW | Automotive | $45–179 | Theo bảng DOE ở trên |
| > 100 kW | Heavy-duty truck, bus | $80–200 | Stack lớn hơn nhưng BOP phức tạp hơn |

> **Lưu ý:** Hệ thống nhỏ (vài kW) thường đắt hơn nhiều per kW vì:
> - Sản lượng thấp → không có economy of scale
> - BOP (máy nén, làm mát) không scale tuyến tính
> - Chi phí cố định (R&D, certification) chia cho ít đơn vị hơn

---

## 10. Key Insights

1. **Bipolar plate > Platinum** về chi phí: 38% vs 11% → tối ưu BPP có ROI cao hơn
2. **Sản lượng là yếu tố quyết định**: $179 → $45/kW khi tăng từ 1k → 500k xe/năm
3. **Platinum loading đã giảm mạnh**: từ ~0.4 mg/cm² (2006) xuống 0.125 mg/cm² (2017 lab)
4. **DOE target $30/kWnet** vẫn chưa đạt được ở quy mô thương mại (2017 data)
5. **Hệ thống nhỏ (< 25 kW)** có chi phí per kW cao hơn nhiều so với automotive scale

---

## 11. Số Tấm Lưỡng Cực & Kích Thước — Tính Từ First Principles

> Full report SA 2017 không accessible công khai (DOE chỉ publish bản tóm tắt 12 trang).
> Các thông số dưới đây được tính từ các giá trị đã xác nhận trong DOE Record #17007.

### Thông số đầu vào (đã xác nhận từ DOE Record #17007)

| Thông số | Giá trị | Nguồn |
|---|---|---|
| Gross power | 87,900 W | DOE Record #17007 |
| Power density | 1,095 mW/cm² | DOE Record #17007 |
| Cell voltage | 0.663 V | DOE Record #17007 |
| Active-to-total area ratio | 0.625 | DOE Record #17007 |
| SS316L thickness (half-plate) | 3 mil = **0.0762 mm** | DOE Record #17007 |
| BPP material cost | $13.19/kg | DOE Record #17007 |
| Active area per cell (SA baseline) | **~400 cm²** | SA methodology 2014–2016 |

### Tính toán

**Bước 1 — Current density:**
```
J = Power density / Cell voltage
J = 1,095 mW/cm² ÷ 0.663 V = 1,651.6 mA/cm²
```

**Bước 2 — Tổng diện tích active cần thiết:**
```
Total active area = Gross power / (V_cell × J)
                  = 87,900 W / (0.663 V × 1.6516 A/cm²)
                  = 87,900 / 1.095 W/cm²
                  = 80,274 cm²
```

**Bước 3 — Số cell:**
```
N_cells = 80,274 cm² ÷ 400 cm²/cell ≈ 201 cells
```

**Bước 4 — Kích thước tấm:**
```
Total plate area = 400 cm² ÷ 0.625 = 640 cm²
Kích thước điển hình: ~200 mm × 320 mm (hoặc ~253 mm × 253 mm nếu vuông)
```

**Bước 5 — Số tấm SS316L:**
```
Mỗi bipolar plate = 2 half-plates SS316L hàn laser
→ 201 bipolar plates × 2 = 402 half-plates SS316L được dập
(+ 2 end plates bằng vật liệu khác, không tính)
```

**Bước 6 — Khối lượng SS316L:**
```
Mỗi half-plate: 640 cm² × 0.00762 cm × 8.0 g/cm³ = 39.0 g
Mỗi bipolar plate (2 half-plates): 78.0 g
Tổng: 201 × 78.0 g = 15,678 g ≈ 15.7 kg/stack
```

### Kết quả tổng hợp

| Thông số | Giá trị |
|---|---|
| Active area/cell | **~400 cm²** |
| Tổng diện tích active | **~80,274 cm²** |
| **Số cell** | **~201 cells** |
| Total plate area/cell | **640 cm²** |
| Kích thước tấm (ước tính) | **~200 mm × 320 mm × 0.152 mm** |
| **Số bipolar plates SS316L** | **201 tấm** (mỗi tấm = 2 half-plates hàn) |
| Tổng half-plates dập | **402 half-plates** |
| Độ dày mỗi half-plate | **0.0762 mm (3 mil)** |
| **Khối lượng SS316L/stack** | **~15.7 kg** |

### Cross-check chi phí

```
Chi phí vật liệu SS316L = 15.7 kg × $13.19/kg = $207/stack
Chi phí vật liệu/kWnet = $207 ÷ 80 kW = $2.59/kWnet

Tổng BPP cost (DOE record) = $8.4/kWnet
→ Vật liệu chiếm ~31% tổng BPP cost ✓ (hợp lý, phần còn lại là dập + mạ + hàn)
```

> **Lưu ý:** Nếu SA 2017 dùng active area khác (ví dụ 300 cm²), số cell sẽ là ~268.
> Giá trị 400 cm² là xác suất cao nhất dựa trên SA methodology nhất quán từ 2014–2016.

---

## 12. Nguồn Tham Khảo

- **DOE Hydrogen Program Record #17007** (2017) — "Fuel Cell System Cost 2017"
  - Tác giả: Brian D. James (Strategic Analysis Inc.), Jennie M. Huya-Kouadio, Cassidy Houchins, Daniel A. DeSantis
  - Cộng tác: Argonne National Laboratory
  - URL: energy.gov/eere/fuelcells/hydrogen-program-records
- DOE Technical Targets for PEM Fuel Cell Components — energy.gov
- Toyota Mirai technical specifications (Pt loading reference)
- NREL — Fuel Cell Cost Analysis reports
