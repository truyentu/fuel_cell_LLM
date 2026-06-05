Bảng So Sánh Tổng Quan
Thông số	Máy in textile (hiện tại)	Yêu cầu cho MEA	Cần nâng cấp?
Lưới (mesh)	Polyester 60–230 mesh	SS 325–400 mesh	⚠️ THAY MỚI
Khung	Nhôm/gỗ, tension thấp	Nhôm/thép, high tension	⚠️ THAY MỚI
Squeegee	Polyurethane 60–70 Shore A	Polyurethane 70–80 Shore A	⚠️ NÂNG CẤP
Tốc độ squeegee	50–200 mm/s	50–150 mm/s (chậm hơn)	✓ OK (giảm speed)
Áp lực squeegee	Không chính xác	Controlled ±0.1 kg/cm	⚠️ CẦN SENSOR
Snap-off distance	2–5 mm (manual)	0.5–2 mm (precision)	⚠️ CẦN MICROMETER
Registration (alignment)	±0.5–1.0 mm	±0.1 mm	⚠️ CẦN CCD CAMERA
Bàn in (table)	Bình thường	Vacuum + heated (60–80°C)	⚠️ THAY MỚI
Môi trường	Mở, bụi OK	Clean room, humidity control	⚠️ CẦN PHÒNG SẠCH
Ink system	Mở (thùng mực)	Kín (tránh bay hơi)	⚠️ CẦN ENCLOSED
Repeatability	±10–20%	±5%	⚠️ CẦN AUTOMATION
1. LƯỚI (MESH) — Thay đổi lớn nhất
Textile:


Polyester mesh, 60–230 threads/inch
Wire diameter: 40–80 µm
Opening: 50–200 µm
Wet film: 20–100 µm
Tension: 15–25 N/cm
MEA:


Stainless steel mesh, 325–400 threads/inch
Wire diameter: 20–30 µm
Opening: 30–50 µm
Wet film: 5–20 µm (mỏng hơn 5–10x!)
Tension: 30–45 N/cm (cao hơn 2x)
Calendered (cán phẳng) để đồng đều
Tại sao phải stainless steel:

Polyester giãn theo thời gian → film thickness thay đổi
SS giữ tension ổn định qua hàng nghìn lần in
SS chịu được solvent trong catalyst ink (alcohol, Nafion dispersion)
SS cho opening chính xác hơn → film đều hơn
Supplier lưới SS: HAVER & BOECKER, NBC Meshtec, Murakami, SAATI

2. KHUNG + TENSION — Phải chính xác hơn
Textile: Tension 15–25 N/cm, sai số ±3 N/cm OK

MEA:

Tension 30–45 N/cm (SS mesh cần tension cao hơn)
Sai số ±1 N/cm (đo bằng tension meter)
Khung phải rigid (nhôm đúc hoặc thép, không phải nhôm hàn)
Tension phải đồng đều 4 cạnh (ảnh hưởng trực tiếp đến film thickness)
Cần thêm: Tension meter (Newman hoặc Tetko) — $500–2,000

3. SQUEEGEE — Cứng hơn, chính xác hơn
Textile: 60–70 Shore A, edge không cần quá sắc

MEA:

70–80 Shore A (cứng hơn → ít biến dạng → film đều hơn)
Edge phải sắc và thẳng (mài lại sau mỗi 500–1,000 lần in)
Góc squeegee: 60–75° (controlled, không phải "cảm tay")
Áp lực đồng đều — đây là yếu tố quan trọng nhất
Nâng cấp cần thiết:

Squeegee holder có load cell (đo áp lực real-time)
Hoặc: pneumatic pressure control (±0.1 kg/cm)
Máy textile thường dùng spring hoặc trọng lượng → không đủ chính xác
4. BÀN IN (PRINT TABLE) — Thay đổi lớn
Textile: Bàn phẳng, có keo dính giữ vải

MEA cần:


┌─────────────────────────────────────┐
│         VACUUM TABLE                │ ← Hút chân không giữ substrate phẳng
│  ┌───────────────────────────────┐  │
│  │    Heating element            │  │ ← 60–80°C (flash dry giữa passes)
│  │    (uniform ±2°C)             │  │
│  └───────────────────────────────┘  │
│  Flatness: ±0.05 mm                │ ← Phẳng hơn 10x so với textile table
│  Vacuum: -0.3 to -0.8 bar          │
└─────────────────────────────────────┘
Tại sao cần vacuum:

PTFE decal (substrate) rất nhẹ, trơn → không dính bằng keo
GDL (carbon paper) mỏng, dễ cong → cần hút phẳng
Bất kỳ nếp nhăn nào = catalyst layer không đều = cell performance giảm
Tại sao cần heated:

Flash dry giữa các pass (in 2–3 lớp)
Giúp solvent bay hơi nhanh → tránh smearing khi in lớp tiếp
60–80°C đủ để dry nhưng không làm hỏng ink
5. INK SYSTEM — Vấn đề lớn nhất theo Fraunhofer
Từ paper 2022 (Challenges of fabricating catalyst layers):

"The main challenge of screen printing process development lies in the paste optimization to prevent evaporation effects over time, ensuring sufficient wetting of the paste on the substrate."

Từ paper 2024:

"Applying such low boiling point inks to printing methods that expose catalyst inks to air, like flatbed screen printing, results in an instable and nonscalable production process due to the successive evaporation of these solvents."

Vấn đề: Catalyst ink chứa alcohol (boiling point 65–82°C) → bay hơi nhanh khi tiếp xúc không khí trên screen → viscosity thay đổi liên tục → film thickness không ổn định.

Giải pháp Fraunhofer (paper 2024):

Phát triển ink formulation mới với high boiling point solvents (thay alcohol bằng glycol ethers, NMP, hoặc hỗn hợp)
Hoặc: enclosed ink system — hộp kín bao quanh vùng in, giảm bay hơi
Hoặc: humidified environment — kiểm soát RH trong vùng in
Nâng cấp cần thiết:

Enclosed flood/print chamber (che kín vùng mực trên screen)
Hoặc: ink recirculation system (bơm mực tuần hoàn, giữ fresh)
Humidity control trong phòng in: 50% RH ±5%
Temperature control: 20–25°C ±2°C
6. SNAP-OFF DISTANCE — Chính xác hơn
Textile: 2–5 mm, điều chỉnh bằng tay, sai số ±1 mm OK

MEA:

0.5–2.0 mm
Điều chỉnh bằng micrometer (±0.1 mm)
Ảnh hưởng trực tiếp đến wet film thickness và mesh mark

Snap-off quá lớn → mesh mark rõ (sọc lưới trên film)
Snap-off quá nhỏ → ink không release clean → film dày không đều
Tối ưu: 1.0–1.5 mm cho SS 325 mesh
7. REGISTRATION / ALIGNMENT — CCD Camera
Textile: ±0.5–1.0 mm OK (mắt thường align)

MEA:

±0.1 mm (active area phải chính xác)
Cần CCD camera alignment system (2–4 camera)
Fiducial marks trên substrate
Auto-correction trước mỗi lần in
Tại sao quan trọng: Nếu catalyst layer lệch >0.5 mm so với subgasket window → gas crossover hoặc inactive area → cell performance giảm.

Cost: CCD alignment system $5–20K (add-on cho máy hiện có)

8. MÔI TRƯỜNG — Clean Room
Textile: Bụi, sợi vải bay → không ảnh hưởng

MEA:

Bụi = pinhole = cell chết
Cần clean room Class 10,000 (ISO 7) minimum
Hoặc: laminar flow hood trên vùng in
Humidity: 50% RH ±5% (Nafion membrane nhạy cảm với humidity)
Temperature: 22°C ±2°C
Cost phòng sạch:

Laminar flow hood (local): $5–15K
Clean room nhỏ (3×4m): $20–50K
Full clean room (6×8m): $50–150K
9. DRYING SYSTEM — Thêm mới
Textile: Flash dryer (IR) hoặc tunnel dryer — nhiệt độ không critical

MEA:

IR dryer hoặc convection oven
Multi-zone temperature control: 60°C → 80°C → 100°C
Thời gian sấy: 10–30 phút (sau pass cuối)
Flash dry giữa passes: 30–60 giây tại 60–80°C (trên heated table)
KHÔNG được sấy quá nhanh → nứt (mud-cracking)
10. QC SYSTEM — Thêm mới hoàn toàn
Textile: Mắt nhìn, OK/NG

MEA cần:

QC	Thiết bị	Giá	Tần suất
Pt loading	Cân phân tích 0.01 mg	$3–5K	Mỗi tấm
Thickness	Micrometer hoặc profilometer	$1–5K	Mỗi tấm
Visual defects	Kính lúp hoặc microscope	$1–3K	Mỗi tấm
Pt mapping (optional)	XRF analyzer	$30–80K	Sampling
Performance	Single cell test station	$30–80K	Sampling 5–10%
Tổng Kết — Checklist Nâng Cấp
Phải thay mới (không dùng lại được từ textile):
 Lưới: SS 325–400 mesh, calendered
 Khung: rigid aluminum, high tension
 Bàn in: vacuum + heated table (flatness ±0.05 mm)
 Drying system: IR + convection multi-zone
Nâng cấp/thêm vào máy hiện có:
 Squeegee: 75–80 Shore A, precision holder với load cell
 Snap-off: micrometer adjustment
 Ink system: enclosed chamber hoặc humidified
 Registration: CCD camera alignment (±0.1 mm)
 Phòng sạch hoặc laminar flow hood
Thêm mới (không có trong textile):
 QC: cân phân tích, micrometer, microscope
 Hot press (cho decal transfer): $15–40K
 Single cell test station: $30–80K
Ước Tính Chi Phí Nâng Cấp
Hạng mục	Giá ước tính	Ghi chú
SS mesh screens (5–10 cái)	$2–5K	325–400 mesh, custom size
Rigid frames + tension system	$2–5K	
Vacuum heated table	$10–30K	Custom hoặc mua
Squeegee upgrade + load cell	$3–8K	
Snap-off micrometer	$1–2K	
CCD alignment (optional)	$5–20K	
Enclosed ink system	$2–5K	Custom fabrication
Laminar flow hood	$5–15K	
Humidity + temp control	$3–8K	
IR dryer	$5–15K	
QC equipment (cân, micrometer)	$5–10K	
Hot press	$15–40K	Carver hoặc tương đương
TỔNG (không có test station)	$60–160K	
Single cell test station (optional)	$30–80K	Scribner 850e
So với mua máy mới chuyên dụng ($50–150K từ THIEME/Systematic Automation): Nâng cấp có thể tương đương hoặc rẻ hơn một chút, nhưng ưu điểm là bạn hiểu máy, tự maintain được, và customize theo nhu cầu.