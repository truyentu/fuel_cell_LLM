# Patent Startup/Shutdown Control Algorithm — PEM Fuel Cell

> **Mục đích:** Freedom-to-Operate (FTO) analysis cho phần mềm điều khiển startup/shutdown
> **Phạm vi:** Cold start, shutdown purge, startup sequence, voltage reversal prevention
> **Cập nhật:** 2026-06-01

---

## 1. Tại Sao Startup/Shutdown Là Vùng Patent Nguy Hiểm?

Mỗi lần startup/shutdown tạo ra **H₂/air front** trong anode — ranh giới giữa H₂ và không khí di chuyển qua kênh dẫn. Khi front này tồn tại:

```
Vùng anode có H₂  → hoạt động bình thường
Vùng anode có air → cathode bị đẩy lên ~1.44V → carbon corrosion
```

Đây là cơ chế **Reverse Current Decay** (Reiser et al., 2005). Tất cả các hãng lớn (GM, UTC/Audi, Toyota, Honda, Ballard) đều có patent bảo vệ MEA khỏi cơ chế này.

---

## 2. Cold Start / Freeze Start Patents

### 2.1 Honda — Dual Control Map Cold Start
| Thông tin | Chi tiết |
|---|---|
| **Patent** | CA2473213C |
| **Assignee** | Honda Motor Co. Ltd. |
| **Filed** | July 2004 |
| **Trạng thái** | **HẾT HẠN** (lapsed July 2015) |

**Claims chính:** Khi nhiệt độ stack ≤ 0°C, dùng "freeze control map" riêng với áp suất khí cao hơn bình thường. Chuyển về normal map khi nhiệt độ > 0°C.

**Kết luận:** Hết hạn — tự do dùng dual-map approach.

---

### 2.2 UTC Power — Freeze-Tolerant (Immiscible Fluid Displacement)
| Thông tin | Chi tiết |
|---|---|
| **Patent** | US6528194B1 |
| **Assignee** | UTC Power Corp |
| **Filed** | August 2001 |
| **Trạng thái** | **HẾT HẠN** (September 2021) |

**Claims chính:** Dùng chất lỏng không tan trong nước (perfluorocarbon, hydrofluoroether) để đẩy nước làm mát ra khỏi stack khi shutdown, tránh đóng băng.

**Kết luận:** Hết hạn — tự do dùng.

---

### 2.3 UTC Power — Vacuum-Assisted Sub-Freezing Startup
| Thông tin | Chi tiết |
|---|---|
| **Patent** | US7112379B2 |
| **Assignee** | UTC Power Corp |
| **Filed** | May 2003 |
| **Trạng thái** | **HẾT HẠN** (~May 2023) |

**Claims chính:** Dùng chân không để hút nước ra khỏi cathode trong quá trình khởi động dưới 0°C, tránh tắc nghẽn kênh dẫn do đá.

**Kết luận:** Hết hạn — tự do dùng.

---

### 2.4 GM — Coolant Flow Reversal During Freeze Startup
| Thông tin | Chi tiết |
|---|---|
| **Patent** | US7749632B2 |
| **Assignee** | GM Global Technology Operations |
| **Filed** | July 2006 |
| **Trạng thái** | **HẾT HẠN** (~July 2026 — vừa hết hạn) |

**Claims chính:** Bơm làm mát có thể đảo chiều dòng chảy qua stack khi freeze startup, giúp làm nóng đều hơn.

**Kết luận:** Vừa hết hạn — tự do dùng.

---

### 2.5 Toyota — AC Impedance Cold Start Water Management ⚠️
| Thông tin | Chi tiết |
|---|---|
| **Patent** | US11196066B2 |
| **Assignee** | Toyota Motor Corp |
| **Filed** | October 2018 |
| **Trạng thái** | **CÒN HIỆU LỰC** (~December 2038) |

**Claims chính:** Dùng đo **AC impedance** để ước tính hàm lượng nước trong màng, điều khiển quá trình startup dưới 0°C.

**Cách tránh:**
- Dùng **lookup table theo nhiệt độ** thay vì AC impedance
- Dùng **pressure drop monitoring** để suy ra trạng thái hydration
- Dùng **voltage response curve** (không phải AC impedance)

---

## 3. Shutdown Purge Sequence Patents

### 3.1 UTC/Reiser — Rapid Air Purge Shutdown
| Thông tin | Chi tiết |
|---|---|
| **Patent** | US20020076583A1 |
| **Assignee** | UTC Power Corp |
| **Filed** | December 2000 |
| **Trạng thái** | **BỊ TỪ CHỐI** (abandoned, never granted) |

**Không có rủi ro** — không bao giờ được cấp patent.

---

### 3.2 UTC/Reiser — Rapid H₂ Purge Startup (Fuel Purge)
| Thông tin | Chi tiết |
|---|---|
| **Patent** | US6887599B2 |
| **Assignee** | UTC → Audi AG (2015) |
| **Filed** | November 2002 |
| **Trạng thái** | **HẾT HẠN** (~November 2022) |

**Claims chính:** Trước khi kết nối tải, bơm H₂ liên tục để đẩy toàn bộ không khí ra khỏi anode trong < 1 giây. Không có H₂/air front → không có carbon corrosion.

**Kết luận:** Hết hạn — **rapid H₂ purge trước startup là tự do dùng**.

---

### 3.3 UTC/Reiser — H₂ Pump Shutdown (Cathode Passivation)
| Thông tin | Chi tiết |
|---|---|
| **Patent** | US6835479B2 |
| **Assignee** | UTC → Audi AG |
| **Filed** | June 2002 |
| **Trạng thái** | **HẾT HẠN** (May 2023) |

**Claims chính:** Khi shutdown, dùng nguồn điện ngoài để vận hành stack như một "hydrogen pump" — bơm H₂ vào cathode cho đến khi nồng độ H₂ ≥ 0.0001%.

**Kết luận:** Hết hạn — tự do dùng.

---

### 3.4 GM — Delayed Temperature-Gated Air Purge ⚠️
| Thông tin | Chi tiết |
|---|---|
| **Patent** | US7608352B2 |
| **Assignee** | GM Global Technology Operations |
| **Filed** | August 2007 |
| **Trạng thái** | **CÒN HIỆU LỰC** (~August 2027) |

**Claims chính:**
- Theo dõi nhiệt độ coolant trong quá trình shutdown
- **Trì hoãn** việc purge anode bằng air cho đến khi nhiệt độ stack < ngưỡng (~50°C)
- Ở nhiệt độ cao, H₂/air front phản ứng mạnh hơn → corrosion nhiều hơn → chờ nguội mới purge

**Cách tránh:**
- Dùng **N₂ purge** thay vì air purge (không tạo H₂/air front — prior art từ 1992)
- Dùng **H₂ recirculation purge** (tiêu thụ H₂ điện hóa thay vì đẩy bằng air)
- Dùng **hỗn hợp H₂/N₂ loãng** thay vì air thuần túy
- Dùng **cathode O₂ depletion** (bịt cathode, để O₂ tự tiêu thụ hết trước khi shutdown)

---

### 3.5 Ballard — Two-Step Dry/Rehumidify Shutdown
| Thông tin | Chi tiết |
|---|---|
| **Patent** | US20060121322A1 |
| **Assignee** | Ballard Power Systems |
| **Filed** | December 2004 |
| **Trạng thái** | **BỊ TỪ CHỐI** (abandoned) |

**Không có rủi ro** — không bao giờ được cấp patent.

---

## 4. Startup Sequence Patents

### 4.1 GM — Stack Shorting During H₂/Air Front ⚠️ (Quan trọng nhất)
| Thông tin | Chi tiết |
|---|---|
| **Patent** | US8828616B2 |
| **Assignee** | GM Global Technology Operations |
| **Filed** | October 2008 |
| **Trạng thái** | **CÒN HIỆU LỰC** (September 2031) |

**Claims chính:**
- Tại thời điểm startup: **đồng thời** đóng shunt switch (short mạch stack), đóng van cathode inlet/outlet, mở H₂
- Shunt switch đóng < 2 giây — đủ để H₂/air front đi qua anode
- Khi stack bị short, không có điện áp → không có reverse current → không có carbon corrosion

**Đây là patent quan trọng nhất cần tránh.**

**Cách tránh:**
- Dùng **resistive load** (điện trở hoặc DC-DC converter ở chế độ current-sink) thay vì short mạch trực tiếp — claims của GM chỉ cover "switch closure" (short), không cover resistive load
- Dùng **N₂ pre-purge** trước khi đưa H₂ vào → không có H₂/air front → không cần shunt switch
- Dùng **rapid H₂ purge** (expired US6887599B2) để đẩy air trước khi kết nối tải
- Dùng **cathode O₂ depletion** trước startup: bịt cathode, duy trì H₂ nhỏ để crossover tiêu thụ O₂ còn lại

---

### 4.2 GM — Asymmetric Electrode for Startup/Shutdown Tolerance
| Thông tin | Chi tiết |
|---|---|
| **Patent** | US9401523B2 |
| **Assignee** | GM Global Technology Operations |
| **Filed** | January 2007 |
| **Trạng thái** | **HẾT HẠN** (fee lapsed trước 2034) |

**Kết luận:** Hết hạn — tự do dùng. Đây là patent về MEA design, không phải control algorithm.

---

## 5. Voltage Reversal / Fuel Starvation Prevention

### 5.1 Ballard — Reversal-Tolerant Anode (WO2001015249A2)
| Thông tin | Chi tiết |
|---|---|
| **Patent** | WO2001015249A2 |
| **Assignee** | Ballard + Johnson Matthey + Siemens |
| **Filed** | August 2000 |
| **Trạng thái** | **HẾT HIỆU LỰC** (lapsed) |

**Claims chính:** Anode catalyst layer với ionomer giữ > 30% nước → khi fuel starvation, ưu tiên oxy hóa nước thay vì carbon support.

**Kết luận:** Hết hiệu lực — reversal-tolerant anode là tự do dùng.

---

### 5.2 Ballard — Cell Voltage Monitoring (US6936370B2)
| Thông tin | Chi tiết |
|---|---|
| **Patent** | US6936370B2 |
| **Assignee** | Ballard Power Systems |
| **Filed** | ~2002 |
| **Trạng thái** | **HẾT HẠN** (~2022) |

**Claims chính:** Theo dõi điện áp từng cell riêng lẻ; phát hiện voltage reversal; tự động giảm tải hoặc shutdown khi phát hiện.

**Kết luận:** Hết hạn — individual cell voltage monitoring là tự do dùng.

---

## 6. Vùng An Toàn — Không Bị Patent

### ✅ N₂ / Inert Gas Purge (Prior Art từ 1992)
Purge anode bằng N₂ khi shutdown là **prior art** được xác nhận từ 1992 (OSTI Technical Report 5292715, UTC patents US5,013,617 và US5,045,414). Không có H₂/air front → không có carbon corrosion. **Đây là cách tránh đơn giản và an toàn nhất.**

### ✅ Ngắt tải trước khi dừng khí
Ngắt điện tải trước khi dừng cấp khí là thao tác cơ bản, không bị patent.

### ✅ Resistive Load Clamping (không phải short mạch)
Kết nối điện trở hoặc DC-DC converter ở chế độ current-sink qua stack trong quá trình startup — không bị GM US8828616B2 (patent đó chỉ cover "switch" / short mạch trực tiếp).

### ✅ Cathode O₂ Depletion (Passive Sealing)
Bịt cathode outlet khi shutdown, để O₂ còn lại tự tiêu thụ bởi crossover H₂ → cathode O₂ → ~0 → bịt anode. Không có patent cụ thể nào cover phương pháp này.

### ✅ Current Ramp-Up Sau Startup
Tăng dần dòng điện sau khi startup (thay vì yêu cầu full power ngay) để màng kịp hydrate. Không có patent active nào cover standalone current ramp-up sequence.

### ✅ Thermal Pre-Heating (General)
Dùng heater điện, coolant pre-heating, hoặc waste heat để làm nóng stack trước startup. Các patent cụ thể (coolant reversal, vacuum, immiscible fluid) đã hết hạn. General thermal management không bị patent.

---

## 7. Bảng Tổng Hợp — Tất Cả Patent Liên Quan

| Patent | Assignee | Nội dung | Trạng thái | Hết hạn |
|---|---|---|---|---|
| US6887599B2 | UTC → Audi | Rapid H₂ purge startup | **HẾT HẠN** | ~Nov 2022 |
| US6835479B2 | UTC → Audi | H₂-pump shutdown | **HẾT HẠN** | May 2023 |
| US6528194B1 | UTC Power | Freeze-tolerant (immiscible fluid) | **HẾT HẠN** | Sep 2021 |
| US7112379B2 | UTC Power | Vacuum freeze startup | **HẾT HẠN** | ~May 2023 |
| CA2473213C | Honda | Cold start dual control map | **HẾT HẠN** | Jul 2015 |
| US7749632B2 | GM | Coolant flow reversal freeze start | **HẾT HẠN** | ~Jul 2026 |
| US9401523B2 | GM | Asymmetric electrode startup tolerance | **HẾT HẠN** | fee lapsed |
| WO2001015249A2 | Ballard | Reversal-tolerant anode | **HẾT HIỆU LỰC** | lapsed |
| US6936370B2 | Ballard | Cell voltage monitoring reversal | **HẾT HẠN** | ~2022 |
| US20020076583A1 | UTC | Air purge shutdown | **BỊ TỪ CHỐI** | — |
| US20060121322A1 | Ballard | Dry/rehumidify shutdown | **BỊ TỪ CHỐI** | — |
| **US7608352B2** | **GM** | **Delayed temperature-gated air purge** | **⚠️ CÒN HIỆU LỰC** | **~Aug 2027** |
| **US8828616B2** | **GM** | **Stack shunt switch startup** | **⚠️ CÒN HIỆU LỰC** | **Sep 2031** |
| **US11196066B2** | **Toyota** | **AC impedance cold start** | **⚠️ CÒN HIỆU LỰC** | **~Dec 2038** |

---

## 8. Chiến Lược Thiết Kế An Toàn

### Phương án đề xuất (tránh tất cả patent còn hiệu lực):

```
STARTUP:
  1. Pre-purge anode bằng N₂ (prior art ✓)
  2. Mở H₂ → đẩy N₂ ra
  3. Kết nối resistive load (không phải short switch) ✓
  4. Ramp up current dần dần ✓
  5. Chuyển sang normal operation

SHUTDOWN:
  1. Giảm tải dần
  2. Ngắt tải điện
  3. Purge anode bằng N₂ (không phải air) ✓
     → Không tạo H₂/air front → không cần temperature-gating
  4. Bịt tất cả van
  5. Xả áp

COLD START (môi trường nhiệt đới — không cần):
  → Nếu cần: dùng thermal pre-heating + lookup table theo nhiệt độ ✓
  → Không dùng AC impedance measurement (Toyota US11196066B2)
```

### Tại sao N₂ purge là lựa chọn tốt nhất:
- Prior art từ 1992 — không ai có thể patent
- Tránh được **cả 2 patent còn hiệu lực** của GM (US7608352B2 và US8828616B2)
- Không cần shunt switch phức tạp
- Không cần temperature monitoring cho purge timing
- Chi phí: bình N₂ nhỏ hoặc N₂ generator

---

## 9. Prior Art Học Thuật (Tham Khảo Khi Cần Phản Bác Patent)

| Tài liệu | Năm | Nội dung |
|---|---|---|
| Reiser et al., *Electrochem. Solid-State Lett.* | 2005 | Mô tả cơ chế Reverse Current Decay — academic disclosure |
| OSTI Technical Report 5292715 | 1992 | N₂ purge là standard practice — prior art cho tất cả air-purge patents |
| UTC patents US5,013,617 và US5,045,414 | ~1991 | N₂ purge được cite là prior art ngay trong patent của UTC |
| Cho et al., *J. Power Sources* | ~2003 | Cold start academic prior art |
| Yan et al., *J. Power Sources* | ~2006 | Cold start characteristics — academic prior art |

---

## 10. Nguồn Tham Khảo

- [US8828616B2](https://patents.google.com/patent/US8828616B2/en) — GM, stack shunt switch startup (~2031)
- [US7608352B2](https://patents.google.com/patent/US7608352B2/en) — GM, delayed temperature-gated air purge (~2027)
- [US11196066B2](https://patents.google.com/patent/US11196066B2/en) — Toyota, AC impedance cold start (~2038)
- [US6887599B2](https://patents.google.com/patent/US6887599B2/en) — UTC/Audi, rapid H₂ purge startup (hết hạn 2022)
- [US6835479B2](https://patents.google.com/patent/US6835479B2/en) — UTC/Audi, H₂-pump shutdown (hết hạn 2023)
- [US6528194B1](https://patents.google.com/patent/US6528194B1/en) — UTC Power, freeze-tolerant (hết hạn 2021)
- [WO2001015249A2](https://patents.google.com/patent/WO2001015249A2/en) — Ballard, reversal-tolerant anode (hết hiệu lực)
- Reiser et al. (2005) — "A Reverse-Current Decay Mechanism for Fuel Cells," *Electrochem. Solid-State Lett.*
- OSTI Report 5292715 (1992) — N₂ purge prior art
