# Open-Source Tools & Databases — AI for Materials Science

Date: 2026-06-04
Purpose: Tổng hợp kết quả deep research về open-source availability của các tools/databases
         được sử dụng trong papers AI Scientist notebook

---

## 1. Synthesis Recipe Database (A-Lab / Ceder Group)

### Text-Mined Synthesis Dataset

| Item | Detail |
|------|--------|
| Repo | [CederGroupHub/text-mined-synthesis_public](https://github.com/CederGroupHub/text-mined-synthesis_public) |
| Size | 19,488 → 29,900 → 33,343 recipes (nhiều versions) |
| Source | Extracted từ 24,304 → 53,538 papers |
| Format | Structured JSON |
| License | Open Source |
| Content | Precursors, temperature, time, operations, target material |

### Materials Project Synthesis Explorer

| Item | Detail |
|------|--------|
| URL | [docs.materialsproject.org/synthesis-explorer](https://docs.materialsproject.org/apps/explorer-apps/synthesis-explorer/background) |
| Access | Free API (cần API key, miễn phí) |
| Content | Searchable synthesis recipes by formula, precursor, keywords |

### Thực Tế A-Lab Dùng Database Này Như Thế Nào

```
A-Lab KHÔNG crawl papers real-time.
A-Lab dùng pre-built database (33K recipes) + NLP similarity matching:

1. Target material → NLP encode → vector
2. Cosine similarity vs 33K recipes trong DB
3. Tìm material tương tự nhất → copy recipe → adjust precursors
4. XGBoost predict temperature
5. Robot execute

Key insight: Database PHẢI CÓ SẴN trước khi AI chạy.
```

---

## 2. ChemCrow (LLM Chemistry Agent)

### Open Source Status

| Item | Detail |
|------|--------|
| Repo | [ur-whitelab/chemcrow-public](https://github.com/ur-whitelab/chemcrow-public) |
| Install | `pip install chemcrow` |
| Framework | LangChain-based |
| License | Open Source |
| LLM | GPT-4 (default) — có thể swap sang local LLM |

### 18 Tools Included

| Category | Tools |
|----------|-------|
| General | WebSearch (SerpAPI), LitSearch (paper-qa + FAISS), Python REPL, Human |
| Molecule | Name2SMILES, SMILES2Price, Name2CAS, Similarity, ModifyMol, PatentCheck, FuncGroups, SMILES2Weight |
| Reaction | NameRXN, ReactionPredict (IBM RXN4Chemistry), ReactionPlanner, ReactionExecute (RoboRXN) |
| Safety | ControlledChemicalCheck (OPCW), ExplosiveCheck (PubChem GHS), SafetySummary |

### Thực Tế ChemCrow Lấy Data Như Thế Nào

```
ChemCrow KHÔNG auto-crawl papers.
3 nguồn data thực tế:

1. WebSearch: SerpAPI → snippets trang 1 Google (KHÔNG full papers)
2. LitSearch: Vector search trên PRE-LOADED PDFs (FAISS + OpenAI Embeddings)
   → User PHẢI upload PDFs trước (GIỐNG NotebookLM!)
3. Chemistry APIs: Query trực tiếp PubChem, RXN4Chemistry, ZINC20, OPCW
   → Structured data, không phải papers

Key insight: LitSearch = NotebookLM equivalent (pre-loaded documents + vector search)
```

---

## 3. MatBERT / MatSciBERT (Materials NER)

### Available Models on HuggingFace

| Model | Source | Link | Size | Notes |
|-------|--------|------|------|-------|
| **MatSciBERT** | IIT Delhi | [m3rg-iitd/matscibert](https://huggingface.co/m3rg-iitd/matscibert) | ~110M | Best for NER, download trực tiếp |
| **MaterialsBERT** | Pranav S. | [pranav-s/MaterialsBERT](https://huggingface.co/pranav-s/MaterialsBERT) | ~110M | Fine-tuned từ PubMedBERT |
| **MatBERT** (Berkeley original) | LBNL | [github/lbnlp/matbert](https://github.com/lbnlp/matbert) | ~110M | Weights cần request |
| **SMatBERT-NER** | Springer | [perevalov/SMatBERT-NER](https://huggingface.co/perevalov/SMatBERT-NER-multilingual) | ~110M | Pre-trained NER (SUBSTANCE, PROPERTY) |

### MatBERT Là Gì (Clarification)

```
MatBERT KHÔNG PHẢI database 2 triệu papers.
MatBERT = model weights (~400MB) đã HỌC từ 2M papers.

Nó KHÔNG chứa text gốc papers.
Nó CHỈ hiểu ngôn ngữ materials science cực tốt.

Use case:
  Input: raw text từ paper ("calcined at 350°C for 2h under Ar flow")
  Output: structured JSON {"action": "calcine", "temp": 350, "time": 2, "gas": "Ar"}

Cần: CÓ SẴN text/papers → MatBERT extract → JSON
Không thể: hỏi MatBERT "cho tôi recipe Ni3Mo" (nó không nhớ)
```

---

## 4. GNN Force Fields (CHGNet, M3GNet)

| Model | Install | Link | Use case |
|-------|---------|------|----------|
| **CHGNet** | `pip install chgnet` | [CederGroup/chgnet](https://github.com/CederGroupHub/chgnet) | Predict energy, forces, stress |
| **M3GNet** | `pip install matgl` | [materialsvirtuallab/matgl](https://github.com/materialsvirtuallab/matgl) | Interatomic potentials, MD |
| **MACE** | `pip install mace-torch` | [ACEsuit/mace](https://github.com/ACEsuit/mace) | Foundation model, NEB, MD |

---

## 5. GNoME Data (Google DeepMind)

| Item | Detail |
|------|--------|
| Repo | [google-deepmind/materials_discovery](https://github.com/google-deepmind/materials_discovery) |
| Data | 520,000+ stable crystal structures |
| Format | .cif files |
| License | Open (Apache 2.0) |
| Framework | JAX (không phải PyTorch) |

---

## 6. Coscientist

| Item | Detail |
|------|--------|
| Paper | Nature 624, 570–578 (2023) |
| Code | ⚠️ Không fully open-source (paper only, no public repo) |
| Architecture | GPT-4 + 5 modules (Planner, Google, Python, Documentation, Experiment) |
| Hardware | Opentrons OT-2 liquid handler + Emerald Cloud Lab |

---

## 7. Other Useful Open Resources

| Resource | URL | Content |
|----------|-----|---------|
| Materials Project | materialsproject.org | 150K+ materials, free API |
| ICSD | icsd.products.fiz-karlsruhe.de | Crystal structures (paid) |
| COD | crystallography.net | 500K+ experimental structures (free) |
| OpenAlex | openalex.org | 250M+ papers metadata (free API) |
| Semantic Scholar | semanticscholar.org | Academic search API (free) |
| PubChem | pubchem.ncbi.nlm.nih.gov | Chemical properties (free) |

---

## Summary: Availability Matrix

```
✅ = download ngay, chạy được
⚠️ = có nhưng cần setup/request
❌ = không public

Tool/Data                    Open?    Local?    GPU needed?
─────────────────────────────────────────────────────────
SynTERRA (33K recipes)       ✅       ✅        ❌ (JSON files)
ChemCrow (agent framework)   ✅       ✅        ❌ (CPU ok, cần LLM API)
MatSciBERT (NER model)       ✅       ✅        ❌ (CPU ok, 400MB)
CHGNet (force field)         ✅       ✅        ✅ (GPU recommended)
M3GNet (force field)         ✅       ✅        ✅ (GPU recommended)
MACE (force field)           ✅       ✅        ✅ (GPU recommended)
GNoME data (520K structures) ✅       ✅        ❌ (data only)
GNoME model (JAX)            ✅       ⚠️       ✅ (JAX + GPU)
Materials Project API        ✅       ✅        ❌
Coscientist code             ❌       —         —
```

---

## Key Corrections (Gemini Claims vs Reality)

| Gemini claimed | Reality from papers |
|---------------|-------------------|
| "A-Lab crawl papers real-time via API" | ❌ Uses pre-built DB (33K recipes, built offline) |
| "ChemCrow auto-fetch thousands of papers" | ❌ LitSearch = vector search on PRE-LOADED PDFs |
| "MatBERT stores 2M papers" | ❌ MatBERT = model weights only, no text storage |
| "Need to replace NotebookLM with MatBERT" | ⚠️ NotebookLM ≈ ChemCrow's LitSearch (same concept!) |

### Actual Data Flow in Papers

```
A-Lab:     Pre-built DB → NLP similarity → recipe → robot → XRD → feedback
ChemCrow:  Pre-loaded PDFs → FAISS vector search → LLM reasoning → API calls → robot
Coscientist: Web search snippets → LLM → code → hardware API → measurement → loop

NONE of them "auto-crawl" papers in real-time during operation.
All require PRE-PREPARED knowledge bases.
```

---

## Implications Cho Pipeline Chúng Ta

```
1. NotebookLM = VALID approach (giống LitSearch của ChemCrow)
   → Giữ lại, không cần thay thế

2. Nâng cấp = build local FAISS DB (giống ChemCrow chính xác hơn)
   → Upload PDFs → embed → vector search → structured output

3. SynTERRA DB = FREE recipe lookup cho Ni-alloys
   → Download từ GitHub → query synthesis conditions

4. MatSciBERT = THÊM VÀO pipeline (extract structured data từ papers)
   → Input: paper text → Output: JSON (temp, precursor, time)
   → Supplement NotebookLM, không thay thế

5. CHGNet/MACE = ĐÃ CÓ trong engine (Level 2)
   → Giữ nguyên

REVISED STACK:
  NotebookLM (human-curated papers, manual query) +
  SynTERRA DB (33K recipes, auto-lookup) +
  MatSciBERT (auto-extract từ new papers) +
  MACE + OC20 + BoTorch (compute engine) +
  Claude API (reasoning + orchestration)
```

---

## 8. GNN Force Fields — Cách Papers Dùng Thực Tế

### Input / Output Format

```
INPUT:
  Crystal structure → Graph representation:
  - Nodes = atoms (one-hot element encoding)
  - Edges = interatomic distances (cutoff 4-5 Å)
  - Cell = lattice vectors (cho periodic systems)

OUTPUT (tùy task):
  - Energy: float (eV) → judge stability
  - Forces: (N, 3) array (eV/Å) → relax structure, run MD
  - Stress: (6,) Voigt → cell optimization
  - Binding energies: O*, OH*, OOH* → catalytic activity prediction
```

### Workflow Chung Trong Tất Cả Papers

```
Step 1: GENERATE candidates (millions)
  Methods: random substitution, CVAE, diffusion model, combinatorial

Step 2: GNN FILTER (milliseconds per structure)
  Predict energy → on convex hull? → loại 99% unstable
  Predict forces → relax → check if structure intact

Step 3: DFT VERIFY (hours per structure)
  Only top 1% → run DFT (VASP/QE/JDFTx)
  Confirm energy, stability, properties

Step 4: FEEDBACK (active learning flywheel)
  DFT results → retrain GNN → more accurate → loop
```

### 4 Ví Dụ Cụ Thể Từ Papers

#### Example 1: GNoME — Screen 2.2M Crystals (Google DeepMind)

```
1 billion candidates generated (substitution + random search)
    ↓
GNoME GNN filter: predict formation energy, check convex hull
    ↓
2.2 million predicted stable (passed filter)
    ↓
DFT verify subset → 736 independently synthesized by other labs!
    ↓
BONUS: Train NequIP potential on GNoME data
    → Zero-shot MD at 1000K
    → Screen superionic conductors for batteries
```

#### Example 2: m-PaiNN — ORR/OER Catalyst Design

```
30,000 unrelaxed multimetallic surfaces generated
    ↓
m-PaiNN (equivariant GNN) predict per-site:
  - O* binding energy
  - OH* binding energy
  - Band center energy
  - Bader charge
    ↓
Active Learning loop (exploration + exploitation):
  - Exploration: pick high-uncertainty structures → DFT → retrain
  - Exploitation: Bayesian optimize toward best overpotential
    ↓
Output: Co-Fe, Co-Co, Co-Zn = best bimetallic SAC sites
  → Matched experimental data!
```

#### Example 3: CVAE + NNP (UMA-s-1p1) — Pt-Ni Fuel Cell Catalyst

```
CVAE generate Pt-Ni alloy "skin" structures (novel compositions)
    ↓
NNP (UMA-s-1p1) rapidly calculate:
  - ORR overpotential (η)
  - Alloy formation energy (E_form)
    ↓
Score: want LOW η AND LOW E_form (active + stable)
    ↓
Feed scores back → CVAE bias generation toward better region
    ↓
Iterative loop: CVAE → NNP → filter → CVAE → converge
    ↓
Output: optimal Pt-rich skin structures for fuel cell cathode
  → Bypassed DFT bottleneck completely during search
```

#### Example 4: MatterGen + MatterSim — Inverse Design

```
User specifies: "I want bulk modulus > 200 GPa, magnetic"
    ↓
MatterGen (diffusion model) generates crystal structures
    ↓
MatterSim (MLIP) pre-relax: check energy above convex hull
    ↓
Filter: keep only structures within 50 meV of hull
    ↓
DFT verify top candidates → confirm properties
    ↓
1 structure (TaCr₂O₆) physically synthesized + measured
  → Properties within 20% of AI prediction!
```

### Uncertainty Handling (Deep Ensemble)

```
GNoME approach:
  10 GNNs trained independently (different random seeds)
  For each structure: predict energy × 10
  Median = prediction
  IQR (interquartile range) = uncertainty

  High IQR → "model not sure" → need DFT verification
  Low IQR → "model confident" → trust prediction

Also: test-time augmentation
  Scale lattice vectors isotropically → re-predict
  If energy changes drastically → out-of-distribution → flag
```

### So Sánh Models

| Model | Framework | Trained on | Best for |
|-------|-----------|-----------|----------|
| GNoME | JAX | Materials Project + generated | Bulk crystal stability |
| NequIP | PyTorch | DFT forces | MD simulations, potentials |
| m-PaiNN | PyTorch | DFT (multi-target) | Catalysis site properties |
| UMA-s-1p1 | PyTorch | OC20 + custom | Alloy surface screening |
| CHGNet | PyTorch | Materials Project | General force field |
| M3GNet | PyTorch (matgl) | Materials Project | General force field |
| MACE | PyTorch | MP + custom | Foundation model, NEB, MD |
| MatterSim | PyTorch | Microsoft data | Pre-relaxation filter |

### Mapping Sang Pipeline Chúng Ta

| Papers approach | Our engine equivalent | File |
|----------------|----------------------|------|
| GNoME filter 99% | `phases/coarse_filter.py` (MACE single-point) | ✅ |
| m-PaiNN predict binding | `runners/oc20_runner.py` (H adsorption) | ✅ |
| NNP in CVAE loop | `runners/mace_runner.py` (NEB + MD) | ✅ |
| MatterSim pre-relax | `phases/coarse_filter.py` | ✅ |
| Deep ensemble | `runners/mace_ensemble.py` (3 sizes) | ✅ |
| Active learning feedback | `phases/dft_feedback.py` | ✅ |
| Bayesian optimization | `optimizer/botorch_loop.py` | ✅ |

**Kết luận: Engine chúng ta đã implement đúng pattern mà papers dùng.**

---

## 9. GNoME vs MACE vs OC20 — Khác Bài Toán, Dùng Song Song

### Phân Biệt Cốt Lõi

```
GNoME/CHGNet:  "Chất này CÓ TỒN TẠI ĐƯỢC không?" (bulk crystal stability)
OC20:          "Bề mặt này XÚC TÁC TỐT không?"   (surface + adsorbate catalysis)
MACE:          "Nguyên tử CHỊU LỰC bao nhiêu?"    (general force field, any system)
```

| | GNoME/CHGNet | OC20 | MACE |
|---|---|---|---|
| Bài toán | Crystal stable? | Catalyst activity? | Physics simulation |
| Dataset | 520K bulk crystals | 1.2M surface+adsorbate | Materials Project 150K |
| Input | Bulk crystal (3D periodic) | Slab + molecule (H, O, OH) | Any atoms |
| Output | Formation energy → stable/unstable | Adsorption energy → active/inactive | Energy, forces, stress |
| Focus | Tìm VẬT LIỆU MỚI tồn tại | Tìm CATALYST tốt | MÔ PHỎNG vật lý (NEB, MD) |
| Framework | JAX (GNoME) / PyTorch (CHGNet) | PyTorch | PyTorch |

### 520K GNoME Dataset = Gì Chính Xác

```
520K = BULK CRYSTALS (periodic, infinite, perfect)

Chứa:    NiMo₃, Ni₂CoO₄, Li₃PS₄... → stable? Yes/No
KHÔNG:   Surface + H adsorbate (OC20 domain)
KHÔNG:   Ni@C interface + defects (MACE domain)
KHÔNG:   NEB barriers, MD trajectories
```

### Tại Sao Cần CẢ 3 Cho Ni@X (Không Chọn 1)

| Câu hỏi R&D | Tool đúng | GNoME giúp? | OC20 giúp? | MACE giúp? |
|-------------|-----------|-------------|------------|------------|
| NiMo alloy tồn tại được? | CHGNet/GNoME | ✅ | ❌ | ❌ |
| NiMo bề mặt HOR tốt? | OC20 | ❌ | ✅ | ❌ |
| H₂ qua carbon shell? | MACE NEB | ❌ | ❌ | ✅ |
| O₂ bị chặn? | MACE NEB | ❌ | ❌ | ✅ |
| Shell vỡ ở 70°C? | MACE MD | ❌ | ❌ | ✅ |

### Pipeline Tuần Tự: 3 Tools Nối Tiếp

```
1000 candidates (random Ni-X combinations)
    ↓
[CHGNet/GNoME] Filter: loại alloy unstable → 300 survive
    ↓
[OC20] Rank: predict H adsorption → HOR activity ranking → Top 50
    ↓
[MACE] Simulate: NEB H₂/O₂ barrier + MD stability → Top 5
    ↓
[JDFTx] Validate: physics trong KOH → Top 3
    ↓
Lab synthesis + test
```

### GNoME Model vs GNoME Data

```
GNoME DATA (520K structures): ✅ Free download, dùng làm lookup table
  → "NiMo₃ có trong list stable không?" → search JSON

GNoME MODEL (GNN on JAX): ⚠️ Khó dùng (JAX, heavy setup)
  → Thay bằng CHGNet (PyTorch, pip install, CÙNG khả năng)
  → CHGNet train trên Materials Project = subset của GNoME data
  → CHGNet = "GNoME dễ dùng" version
```

---

## 10. Galactica + ChemLLM — Đánh Giá Cho Pipeline

### Galactica (Meta AI) — ❌ KHÔNG DÙNG

| Item | Detail |
|------|--------|
| Status | Demo rút sau 3 ngày (Nov 2022), weights vẫn trên HuggingFace |
| Sizes | 1.3B, 6.7B, 30B, 120B |
| Training | 106B tokens (papers, textbooks, SMILES, proteins) |
| Download | [facebook/galactica-6.7b](https://huggingface.co/facebook/galactica-6.7b) |
| Problem | **Hallucinate nghiêm trọng** — generate plausible nonsense |
| Maintained | ❌ Dead since 2022, không update |

```
Verdict: ❌ KHÔNG dùng cho R&D pipeline
  - Hallucination = disaster cho scientific decisions
  - 4 năm không update
  - Claude/GPT-4 vượt trội hoàn toàn
```

### ChemLLM (Shanghai AI Lab) — ⚠️ Dùng Như TOOL, Không Thay Claude

| Item | Detail |
|------|--------|
| Status | ✅ Active, maintained (latest: May 2026) |
| Versions | ChemLLM-7B-Chat v1.5-DPO (RLHF) |
| Family | ChemLLM (text) + ChemVLM-8B/26B (multimodal) |
| Download | [AI4Chem/ChemLLM-7B-Chat](https://huggingface.co/AI4Chem/ChemLLM-7B-Chat) |
| VRAM | 7B: ~14GB FP16, ~6GB 4-bit quantized |
| Performance | ≈ GPT-4 trên chemical tasks |

```
Pros:
  - Chemistry-native (trained chuyên hóa học)
  - Open source, chạy local
  - Có RLHF (ít hallucinate hơn Galactica)
  - Multimodal version đọc cả hình cấu trúc

Cons:
  - Focus ORGANIC (SMILES) — inorganic/crystal chưa chắc mạnh
  - Multi-step reasoning kém Claude
  - Context window nhỏ

Verdict: ⚠️ Dùng như TOOL (predict reactions, SMILES conversion)
         ❌ KHÔNG thay Claude làm orchestrator/brain
```

### Final Architecture Decision

```
BRAIN (orchestration + reasoning): Claude API
  - Multi-step reasoning tốt nhất
  - Anti-hallucination tốt nhất
  - General intelligence

TOOLS (specific tasks):
  - ChemLLM: reaction prediction, SMILES lookup (nếu cần)
  - MatSciBERT: NER extraction từ papers
  - CHGNet: stability prediction (thay GNoME model)
  - OC20: catalytic activity prediction
  - MACE: NEB barriers + MD simulation
  - BoTorch: Bayesian optimization
  - SynTERRA: synthesis recipe lookup

Claude = Brain (giống GPT-4 trong ChemCrow)
Tools = Hands (giống 18 tools trong ChemCrow)
```
