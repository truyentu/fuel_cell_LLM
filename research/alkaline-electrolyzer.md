# Alkaline Water Electrolyzer — Thiết Kế, Chế Tạo, Chi Phí

> **Mục đích:** Research về alkaline electrolyzer để tự sản xuất hydrogen cho PEM fuel cell 80 kW
> **Cập nhật:** 2026-06-02
> **Ưu điểm chính:** Dùng Nickel thay Pt/Ir → rẻ hơn 10–100x so với PEM electrolyzer

---

## 1. Tính Toán Nhu Cầu H₂ Cho Stack 80 kW

| Thông số | Giá trị | Ghi chú |
|----------|---------|---------|
| FC output | 80 kW | Net electrical |
| FC efficiency (LHV) | ~50% | Typical PEM |
| LHV hydrogen | 33.33 kWh/kg | |
| H₂ consumption | **4.8 kg/h** | 80 ÷ (0.5 × 33.33) |
| Volumetric | **53.4 Nm³/h** | 4.8 × 11.126 |
| Per day (24h) | **115 kg/day** | |
| Per day (8h FC) | **38.4 kg/day** | |

### Electrolyzer sizing

| Scenario | H₂ rate | Electrolyzer input | H₂ storage |
|----------|---------|-------------------|------------|
| FC 24h, direct feed | 4.8 kg/h | ~264 kW | Buffer nhỏ |
| FC 12h, electrolyzer 24h | 2.4 kg/h | ~132 kW | ~57 kg |
| FC 8h, electrolyzer 24h | 1.6 kg/h | ~88 kW | ~38 kg |

**Khuyến nghị:** Electrolyzer 100–150 kW + bình chứa H₂ nếu FC chạy <24h/ngày.

---

## 2. Nguyên Lý Hoạt Động

### Phản ứng điện hóa

```
Cathode (−): 2H₂O + 2e⁻ → H₂↑ + 2OH⁻         (tạo hydrogen)
Anode (+):   4OH⁻ → O₂↑ + 2H₂O + 4e⁻           (tạo oxygen)
─────────────────────────────────────────────────
Tổng:        2H₂O → 2H₂ + O₂
```

- Điện thế tối thiểu (thermodynamic): **1.23 V/cell**
- Điện thế thực tế: **1.7–2.2 V/cell** (do overpotential + ohmic loss)
- Electrolyte: **25–30 wt% KOH** (dẫn OH⁻ ion)

### Cơ chế vận chuyển ion

```
Cathode side:                    Anode side:
H₂O + e⁻ → H₂ + OH⁻           OH⁻ → O₂ + H₂O + e⁻
                    ←── OH⁻ ──→
           (qua separator/diaphragm)
```

KOH không bị tiêu thụ — chỉ nước bị phân hủy.

---

## 3. Cấu Trúc Cell Stack

### 3.1 Hai kiểu thiết kế chính

#### Kiểu "Gap" truyền thống

```
[BP] — [Electrode] — [Gap 1-3mm] — [Diaphragm] — [Gap 1-3mm] — [Electrode] — [BP]
```
- Electrode cách separator 1–3 mm
- Electrolyte tuần hoàn tự do qua gap
- Bọt khí thoát tự nhiên
- Dễ chế tạo
- Current density thấp: 200–400 mA/cm²

#### Kiểu "Zero-Gap" (tiên tiến)

```
[BP] — [Porous Electrode] — [Separator] — [Porous Electrode] — [BP]
```
- Electrode ép trực tiếp vào separator
- Electrolyte chảy qua cấu trúc xốp của electrode
- Ohmic resistance thấp hơn nhiều
- Current density cao: 500–2000 mA/cm²
- Chế tạo phức tạp hơn (porosity + compression critical)

### 3.2 Bipolar Stack (Filter Press Design)

```
End Plate (+) → [Cell 1] → [Cell 2] → ... → [Cell N] → End Plate (-)
```

Mỗi cell gồm:
- **Bipolar plate**: dẫn điện giữa cells + flow channels
- **Frame/gasket**: seal, định nghĩa thể tích electrolyte
- **Anode**: nickel mesh/foam
- **Separator**: Zirfon hoặc tương đương
- **Cathode**: nickel foam hoặc Raney-Ni

Cells nối tiếp điện (voltage cộng), nhưng kết nối thủy lực chung qua electrolyte loop.

### 3.3 Monopolar vs Bipolar

| | Monopolar | Bipolar |
|---|---|---|
| Kết nối điện | Song song | Nối tiếp qua BP |
| Voltage | Thấp (~2V) | Cao (N × 2V) |
| Current | Rất cao | Trung bình |
| Efficiency | Thấp hơn | Cao hơn |
| Chế tạo | Đơn giản | Phức tạp hơn |
| Công nghiệp | Hiếm, nhỏ | **Tiêu chuẩn** |

---

## 4. Thông Số Vận Hành

| Parameter | Conventional | Zero-Gap Advanced |
|-----------|-------------|-------------------|
| Electrolyte | 25–30 wt% KOH | 25–30 wt% KOH |
| Nhiệt độ | 60–80°C | 70–90°C |
| Áp suất | 1 bar (atmospheric) | 3–35 bar (pressurized) |
| Cell voltage | 1.85–2.2 V | 1.7–2.0 V |
| Current density | 200–400 mA/cm² | 400–2000 mA/cm² |
| Faradaic efficiency | 95–98% | 97–99% |
| System efficiency (LHV) | 63–70% | 68–76% |
| Specific energy | 55–65 kWh/kg H₂ | 50–56 kWh/kg H₂ |
| H₂ purity (raw) | 99.0–99.5% | 99.5–99.8% |
| Stack lifetime | 60,000–90,000 h | 60,000–80,000 h |
| System lifetime | 20–30 năm | 20–30 năm |
| Degradation rate | ~2–3 µV/h/cell | ~1–2 µV/h/cell |

### KOH Electrolyte

- **30 wt% KOH** là tiêu chuẩn công nghiệp
- Ionic conductivity đạt peak ở 30–35% tại 80°C
- Thấp hơn → resistance cao
- Cao hơn → viscosity + corrosion tăng
- KOH tốt hơn NaOH: conductivity cao hơn, ít ăn mòn Ni hơn
- Cần KOH purity 99.9%+ và DI water

---

## 5. Vật Liệu & Linh Kiện

### 5.1 Electrode — Cathode (HER)

| Vật liệu | Hoạt tính | Chi phí | Ghi chú |
|-----------|-----------|---------|---------|
| Nickel mesh/foam (plain) | Baseline | Thấp ($5–20/m²) | Commercial sẵn |
| Raney nickel (NiAl → leach Al) | Cao | Trung bình | ~3x thấp hơn overpotential vs plain Ni |
| NiMo alloy | Cao | Trung bình | Best HER alkaline |
| NiFeS trên Ni foam | Rất cao | Thấp | Electrodeposited |
| NiFe-LDH | Rất cao | Thấp | Layered double hydroxide |
| Electrodeposited NiCo | Cao | Thấp | Đơn giản |

### 5.2 Electrode — Anode (OER)

| Vật liệu | Hoạt tính | Chi phí | Ghi chú |
|-----------|-----------|---------|---------|
| Nickel mesh (plain) | Baseline | Thấp | ~350 mV overpotential |
| Nickel foam (oxidized in-situ) | Tốt | Thấp | Tạo NiOOH active layer khi vận hành |
| NiFeOₓ / NiFe-LDH | **Cao** | **Thấp** | **Best non-noble OER catalyst alkaline** |
| NiCo₂O₄ spinel | Cao | Thấp | Electrodeposited hoặc sputtered |
| IrO₂ (PEM standard) | Best | Rất đắt | **KHÔNG CẦN cho alkaline** |

**Key insight:** Alkaline dùng **Ni-based non-precious metal** → chi phí catalyst giảm 100x so với PEM.

### 5.3 Electrode tự chế tạo

```
1. Mua nickel foam thương mại (pore 450–580 µm, porosity ~97%)
2. Làm sạch: acetone (dầu mỡ) → 10% HCl etch → DI water rinse
3. Optional coating (tăng hoạt tính):
   a. Electrodeposit NiMo hoặc NiFe từ dung dịch mạ
   b. Hoặc: Raney-Ni (spray NiAl alloy → leach Al trong 20% NaOH ở 80°C)
4. Sấy, cắt theo kích thước cell
```

### 5.4 Separator / Diaphragm

| Vật liệu | Availability | Chi phí | Performance | Ghi chú |
|-----------|-------------|---------|-------------|---------|
| **Zirfon PERL (Agfa)** | Commercial | ~$50–100/m² | Excellent | **Tiêu chuẩn CN**; ZrO₂/polysulfone; 0.5 mm |
| Asbestos | CẤM | — | OK | Gây ung thư, KHÔNG DÙNG |
| PPS + ZrO₂ composite | R&D | Trung bình | Tốt | Alternative Zirfon |
| NiO diaphragm | Specialty | Cao | Tốt | Sintered |

**Zirfon PERL** là lựa chọn duy nhất thực tế cho alkaline electrolyzer hiện đại:
- ZrO₂ nanoparticles trong matrix polysulfone
- Dày 0.5 mm, porosit ~55%
- Ionic resistance thấp
- Chịu được 30% KOH ở 90°C
- Tuổi thọ >40,000 giờ

### 5.5 Bipolar Plate

| Vật liệu | Chi phí | Ghi chú |
|-----------|---------|---------|
| Nickel-plated steel | Thấp | Phổ biến nhất, dễ gia công |
| Pure nickel plate | Trung bình | Best corrosion resistance |
| Stainless steel 316L | Thấp | OK cho short-term, corrosion concern long-term |
| Nickel-clad steel | Trung bình | Compromise |

**Tiêu chuẩn:** Thép mạ Nickel 10–50 µm. Flow channels CNC hoặc stamping.

### 5.6 Frame / Gasket

- Frame: PP (polypropylene), PEEK, hoặc PTFE — chịu KOH
- Gasket: EPDM hoặc Viton — chịu KOH ở 80°C
- **KHÔNG dùng:** silicone (bị KOH ăn), NBR rubber

---

## 6. Nhà Sản Xuất Chính

| Công ty | Quốc gia | Sản phẩm | Công suất | Ghi chú |
|---------|----------|----------|-----------|---------|
| **Nel ASA** | Na Uy | A-series (A150, A300, A500) | 1.5–3.9 MW | Lâu đời nhất (Norsk Hydro legacy) |
| **thyssenkrupp nucera** | Đức | 20 MW modules | 20+ MW | Scalable, GW-level projects |
| **McPhy** | Pháp | McLyzer | 0.4–4 MW | Pressurized (30 bar) |
| **Sunfire** | Đức | HyLink Alkaline | Multi-MW | Zero-gap advanced |
| **LONGi Hydrogen** | Trung Quốc | ALK series | 1–2 MW | Giá thấp nhất |
| **Peric Hydrogen** | Trung Quốc | — | 1–5 MW | Cost-effective |
| **Cockerill Jingli** | Trung Quốc/Bỉ | — | Multi-MW | Joint venture |
| **John Cockerill** | Bỉ | — | 5–20 MW | European quality |

---

## 7. Chi Phí

### 7.1 CAPEX — Stack vs System

| Component | % tổng CAPEX | Chi phí ước tính |
|-----------|-------------|-----------------|
| Stack (cells) | 40–50% | $150–300/kW |
| Power electronics (rectifier) | 15–20% | $50–100/kW |
| Gas processing (drying, purification) | 10–15% | $30–60/kW |
| Water treatment (deionizer) | 5% | $15–30/kW |
| Piping, valves, instrumentation | 10–15% | $30–60/kW |
| Installation, commissioning | 5–10% | $20–40/kW |
| **TỔNG system** | 100% | **$350–600/kW** |

### 7.2 Chi phí theo thời gian

| Năm | Alkaline $/kW (system) | PEM $/kW (system) |
|-----|----------------------|-------------------|
| 2020 | $500–800 | $1000–1500 |
| 2023 | $400–600 | $700–1200 |
| 2025 | $300–500 | $500–900 |
| 2030 (target) | $200–350 | $300–500 |

### 7.3 Chi phí sản xuất H₂ (LCOH)

```
LCOH = (CAPEX × CRF + OPEX) / H₂ produced

Với:
- CAPEX: $400/kW
- Lifetime: 80,000 h
- Electricity: $0.05/kWh (industrial)
- Efficiency: 55 kWh/kg H₂
- Capacity factor: 90%

LCOH ≈ $3.0–4.0/kg H₂

Nếu electricity $0.03/kWh (renewable surplus):
LCOH ≈ $2.0–2.5/kg H₂
```

### 7.4 So sánh chi phí catalyst

| | PEM Electrolyzer | Alkaline Electrolyzer |
|---|---|---|
| Anode catalyst | IrO₂ ($150K/kg) | NiFe ($10–50/kg) |
| Cathode catalyst | Pt ($30K/kg) | Ni/NiMo ($10–50/kg) |
| Membrane/Separator | Nafion (~$500/m²) | Zirfon (~$50–100/m²) |
| **Catalyst cost/m²** | **$200–2000/m²** | **$5–50/m²** |

→ Alkaline rẻ hơn **40–100x** về catalyst + separator.

---

## 8. So Sánh Alkaline vs PEM Electrolyzer

| Parameter | Alkaline | PEM |
|-----------|----------|-----|
| Catalyst | Ni, NiFe (rẻ) | Ir, Pt (đắt, hiếm) |
| Electrolyte | 30% KOH (liquid) | Nafion membrane (solid) |
| Separator | Zirfon ($50–100/m²) | Nafion ($500/m²) |
| Current density | 200–2000 mA/cm² | 1000–4000 mA/cm² |
| System efficiency | 63–76% | 60–72% |
| Response time | Giây–phút | Milliseconds |
| Pressure | 1–35 bar | 1–80 bar |
| Startup time | Phút | Giây |
| Lifetime stack | 60,000–90,000 h | 40,000–80,000 h |
| CAPEX | $300–600/kW | $500–1500/kW |
| H₂ purity (raw) | 99.5% | 99.99% |
| Footprint | Lớn hơn | Nhỏ hơn |
| **DIY feasibility** | **Cao** | **Rất thấp** |

### Alkaline thắng ở:
- Chi phí (rẻ hơn 2–3x)
- Tuổi thọ (dài hơn)
- Vật liệu (dễ mua, không cần PGM)
- DIY feasibility (Ni foam + KOH + Zirfon)

### PEM thắng ở:
- Compact (footprint nhỏ)
- Dynamic response (theo kịp renewable energy fluctuation)
- H₂ purity cao hơn
- Pressurized output (không cần compressor)

---

## 9. Khả Năng Tự Chế Tạo (DIY Feasibility)

### 9.1 Đánh giá độ khó

| Component | Tự làm? | Độ khó | Ghi chú |
|-----------|---------|--------|---------|
| Electrode (Ni foam) | Mua | ⭐ | Commodity, Alibaba |
| Electrode coating (NiMo, NiFe) | Tự mạ | ⭐⭐⭐ | Electrodeposition, cần kinh nghiệm |
| Separator (Zirfon) | Mua | ⭐ | Agfa bán thương mại |
| Bipolar plate | Tự CNC | ⭐⭐⭐ | Thép mạ Ni, CNC flow channels |
| Frame (PP/PEEK) | Tự CNC/injection | ⭐⭐ | |
| Gasket (EPDM) | Mua/cắt | ⭐ | |
| End plate | Tự CNC | ⭐⭐ | Thép hoặc nhôm, bolt pattern |
| Electrolyte (KOH) | Mua | ⭐ | Hóa chất công nghiệp |
| BOP (pump, heat exchanger) | Mua | ⭐⭐ | Off-the-shelf components |
| Rectifier (AC→DC) | Mua | ⭐⭐ | Industrial power supply |
| Control system | Tự thiết kế | ⭐⭐⭐ | PLC hoặc MCU |
| Gas/water separator | Tự chế | ⭐⭐ | Stainless steel vessel |

### 9.2 Bill of Materials (cho 10 kW stack prototype)

| Component | Spec | Số lượng | Giá ước tính |
|-----------|------|----------|-------------|
| Ni foam electrode | 1.6mm, 97% porosity, 300×300mm | 40 tấm | $200–400 |
| Zirfon PERL separator | 500×500mm sheets | 20 tấm | $500–1000 |
| Bipolar plates (Ni-plated steel) | 4mm, CNC channels | 20 tấm | $500–1000 |
| PP frames | CNC machined | 20 cái | $300–500 |
| EPDM gaskets | Die-cut | 40 cái | $100–200 |
| End plates (steel) | 20mm, bolt holes | 2 cái | $200–300 |
| Tie rods + nuts (SS) | M12 | 8 bộ | $50–100 |
| KOH (99.9%) | 25 kg | 1 thùng | $50–100 |
| Pump (KOH resistant) | Magnetic drive, PP housing | 2 cái | $300–600 |
| Heat exchanger | SS plate type | 1 cái | $200–400 |
| Rectifier (DC power supply) | 10 kW, 0–100V, 0–200A | 1 cái | $500–1500 |
| Instrumentation (T, P, flow) | — | 1 set | $300–500 |
| Gas-liquid separator (SS) | 5L volume | 2 cái | $200–400 |
| Piping + valves (PP/SS) | — | 1 set | $300–500 |
| **TỔNG 10 kW prototype** | | | **$4,000–7,500** |

→ **~$400–750/kW** cho prototype. Giảm xuống $200–400/kW khi optimize + volume.

### 9.3 Quy trình chế tạo stack

```
1. CNC bipolar plates (thép → mạ Ni → CNC flow channels)
2. CNC frames (PP hoặc PEEK)
3. Cắt die gaskets (EPDM)
4. Chuẩn bị electrodes:
   a. Cắt Ni foam theo kích thước
   b. Làm sạch (acetone → HCl → rinse)
   c. Optional: electrodeposit NiMo hoặc NiFe coating
5. Cắt Zirfon separator theo kích thước
6. Assembly stack:
   End plate → [frame + gasket + cathode + separator + anode + frame + gasket + BP] × N → End plate
7. Torque bolts (đều, cross pattern)
8. Leak test (áp lực N₂)
9. Fill electrolyte (30% KOH)
10. Commissioning: low current → ramp up
```

---

## 10. System (Balance of Plant)

```
                    ┌─────────────┐
    DC Power ──────→│  STACK      │──→ H₂ (wet) → Gas/Liq Sep → Dryer → H₂ (dry) → Storage
                    │  (cells)    │──→ O₂ (wet) → Gas/Liq Sep → Vent
                    └──────┬──────┘
                           │
                    KOH loop (pump)
                           │
                    ┌──────┴──────┐
                    │ Heat Exch.  │ ← Cooling water
                    └──────┬──────┘
                           │
                    ┌──────┴──────┐
                    │  KOH Tank   │ ← DI Water makeup
                    └─────────────┘
```

### BOP components:
- **Circulation pump**: magnetic drive, PP/PVDF housing (KOH resistant)
- **Heat exchanger**: plate type, SS316L
- **KOH tank**: PP lined steel hoặc HDPE
- **Gas-liquid separator**: SS316L, gravity separation
- **Water deionizer**: mixed-bed resin (feed water <1 µS/cm)
- **H₂ dryer**: desiccant (silica gel) hoặc refrigeration
- **Safety**: H₂ detector, pressure relief, check valves, N₂ purge

---

## 11. An Toàn

### Rủi ro chính:
1. **H₂/O₂ explosive mixture** — LEL H₂ = 4% in air
2. **KOH corrosive** — gây bỏng da, mù mắt
3. **Áp suất** — bình chứa H₂
4. **Điện** — high DC current (hàng trăm Ampere)

### Biện pháp:
- Ventilation tốt (H₂ nhẹ, bay lên → vent trên cao)
- H₂ leak detector (catalytic hoặc semiconductor sensor)
- Check valve ngăn O₂ chảy ngược
- Pressure relief valve (PRV) trên mỗi bình
- PPE: kính bảo hộ, găng tay, apron khi xử lý KOH
- Emergency shower/eyewash gần vị trí làm việc
- N₂ purge trước start và sau shutdown

---

## 12. Xu Hướng 2024–2026

1. **Zero-gap design** trở thành tiêu chuẩn (thay thế finite-gap)
2. **High current density** — 1000–2000 mA/cm² (tiệm cận PEM)
3. **Pressurized operation** — 30–35 bar (loại bỏ H₂ compressor)
4. **Advanced separators** — thay thế Zirfon, mỏng hơn, resistance thấp hơn
5. **GW-scale manufacturing** — thyssenkrupp nucera, Nel, LONGi
6. **Cost target $200/kW** — 2030
7. **Ni-based nanostructured electrodes** — NiFe-LDH, NiMoS, tăng hoạt tính 5–10x

---

## 13. Kết Luận — Chiến Lược Cho Bạn

### Phase 1: Mua H₂ bình công nghiệp
- Focus 100% vào stack fuel cell + BOP
- H₂ industrial grade 99.999% sẵn có
- Chi phí: ~$10–15/kg (nhỏ lẻ)

### Phase 2: Self-build alkaline electrolyzer (10 kW prototype)
- Khi đã validate fuel cell stack
- Investment: $5–8K cho 10 kW prototype
- Sản xuất: ~0.2 kg H₂/h (đủ test fuel cell)
- Thời gian: 2–3 tháng chế tạo + commissioning

### Phase 3: Scale up electrolyzer (100–300 kW)
- Khi cần H₂ liên tục cho 80 kW FC
- Investment: $50–150K
- Sản xuất: 2–5 kg H₂/h
- Cần: renewable electricity source (solar/wind) để H₂ thực sự "green"

### So sánh với mua PEM electrolyzer:

| | Tự chế Alkaline | Mua PEM electrolyzer |
|---|---|---|
| CAPEX 100 kW | $40–80K | $70–150K |
| Catalyst cost | ~$0 (Ni) | $5,000–20,000 (Ir + Pt) |
| DIY feasible | ✓ | ✗ (cần Nafion + Ir) |
| Maintenance | Đơn giản (KOH + Ni) | Phức tạp (membrane thay) |
| Footprint | Lớn hơn 2–3x | Nhỏ |
| Response time | Chậm (phút) | Nhanh (giây) |

---

## Nguồn Tham Khảo

- Nel ASA Alkaline Electrolyzer: [nel.com](https://nel.com)
- thyssenkrupp nucera: [nucera.com](https://www.nucera.com)
- McPhy McLyzer: [mcphy.com](https://mcphy.com)
- Zirfon PERL (Agfa): [agfa.com](https://www.agfa.com/specialty-products/solutions/membranes/zirfon/)
- Fraunhofer ISE Electrolyzer research
- IRENA Green Hydrogen Cost Reduction Report 2020
- IEA Global Hydrogen Review 2024
- DOE Hydrogen Program Record: Electrolyzer Cost
