# Level 2 — Tool APIs Reference

Date: 2026-06-02
Purpose: Input/output format của các tools cho compute pipeline

---

## Tổng Quan 4 Tools

| Tool | Vai trò | Install | GPU? | Tốc độ |
|------|---------|---------|------|--------|
| **MACE** | Simulate energy/forces nguyên tử (thay DFT) | `pip install mace-torch` | Nên có | ~ms/structure |
| **fairchem (OC20)** | Predict adsorption energy (catalyst screening) | `pip install fairchem-core` | Cần | ~100ms-1s/structure |
| **BoTorch** | Bayesian optimization (chọn thí nghiệm thông minh) | `pip install botorch` | Optional | Instant |
| **JDFTx** | DFT chính xác TRONG dung dịch (validate) | Compile from source | Nên có | Giờ-ngày/structure |

---

## Tool 1: MACE

### Install
```bash
pip install mace-torch
```

### Input: ASE Atoms object
```python
from ase import Atoms
atoms = Atoms(
    symbols=['Ni', 'C', 'C', ...],  # atomic symbols
    positions=[[0,0,0], [1.2,0,0], ...],  # Å
    cell=[[10,0,0],[0,10,0],[0,0,10]],  # lattice vectors Å
    pbc=True  # periodic boundary conditions
)
```

### Minimal Working Example
```python
from mace.calculators import mace_mp
from ase.build import bulk

calc = mace_mp(model="medium", device="cuda")
atoms = bulk("Ni", "fcc", a=3.52, cubic=True)
atoms.calc = calc

energy = atoms.get_potential_energy()  # eV
forces = atoms.get_forces()            # (N,3) eV/Å
stress = atoms.get_stress()            # (6,) eV/Å³
```

### NEB Diffusion Barrier (H₂ qua carbon shell)
```python
from mace.calculators import mace_mp
from ase.mep import NEB
from ase.mep.neb import NEBTools
from ase.optimize import MDMin

calc_factory = lambda: mace_mp(model="medium", device="cuda")

initial = read("initial.traj")  # H₂ outside shell
final = read("final.traj")      # H₂ inside shell

n_images = 5
images = [initial] + [initial.copy() for _ in range(n_images)] + [final]
for image in images[1:-1]:
    image.calc = calc_factory()

neb = NEB(images, climb=True)
neb.interpolate(method="idpp")
opt = MDMin(neb, trajectory="neb.traj")
opt.run(fmax=0.05)

barrier, dE = NEBTools(images).get_barrier()  # eV
print(f"H₂ diffusion barrier: {barrier:.3f} eV")
```

### MD Simulation (Shell stability at 70°C)
```python
from ase.md.langevin import Langevin
from ase import units

calc = mace_mp(model="medium", device="cuda")
atoms.calc = calc

dyn = Langevin(atoms, timestep=1.0*units.fs, temperature_K=343, friction=0.01/units.fs)
dyn.run(steps=10000)  # 10 ps
```

### Output Format
| Property | Method | Type | Units |
|----------|--------|------|-------|
| Energy | `get_potential_energy()` | float | eV |
| Forces | `get_forces()` | ndarray (N,3) | eV/Å |
| Stress | `get_stress()` | ndarray (6,) | eV/Å³ |

### Models Available
| Model | Coverage |
|-------|----------|
| `mace_mp` (medium) | 89 elements, inorganic |
| `mace_off` | Organic molecules |
| `mace_omat` | Open Materials dataset |

---

## Tool 2: fairchem (OC20)

### Install
```bash
pip install fairchem-core
# UMA model cần HuggingFace access:
huggingface-cli login
```

### Minimal Example — Adsorption Energy
```python
from ase.build import fcc111, add_adsorbate
from ase.optimize import LBFGS
from fairchem.core import FAIRChemCalculator, pretrained_mlip

predictor = pretrained_mlip.get_predict_unit("uma-s-1p2", device="cuda")

# Build Ni(111) slab
slab = fcc111("Ni", size=(2,2,5), vacuum=20.0)
slab.calc = FAIRChemCalculator(predictor, task_name="oc20")
opt = LBFGS(slab)
opt.run(fmax=0.05)
slab_e = slab.get_potential_energy()

# Slab + H adsorbate
adslab = slab.copy()
add_adsorbate(adslab, "H", height=1.0, position="fcc")
adslab.calc = FAIRChemCalculator(predictor, task_name="oc20")
opt = LBFGS(adslab)
opt.run(fmax=0.05)
adslab_e = adslab.get_potential_energy()

ads_energy = adslab_e - slab_e - ref_H  # eV
```

### task_name Options
| task_name | Dùng cho |
|-----------|----------|
| `oc20` | Catalyst surfaces (RPBE level) |
| `omat` | Bulk materials (PBE level) |
| `omol` | Molecules |

### Gotchas
- v1 (`OCPCalculator`) vs v2 (`FAIRChemCalculator`) API khác nhau hoàn toàn
- `task_name` quyết định reference frame — không mix energies giữa tasks
- Tags: 0=bulk, 1=surface, 2=adsorbate

---

## Tool 3: BoTorch

### Install
```bash
pip install botorch
```

### Full Optimization Loop
```python
import torch
from botorch.models import SingleTaskGP
from botorch.models.transforms import Normalize, Standardize
from botorch.fit import fit_gpytorch_mll
from botorch.acquisition import LogExpectedImprovement
from botorch.optim import optimize_acqf
from gpytorch.mlls import ExactMarginalLogLikelihood

# --- Define search space ---
d = 3  # n_layers, vacancy%, N_doping%
bounds = torch.tensor([
    [1.0, 0.0, 0.0],   # lower bounds
    [3.0, 20.0, 10.0],  # upper bounds
], dtype=torch.double, device="cuda")

# --- Initial random samples ---
train_X = torch.rand(8, d, dtype=torch.double, device="cuda")
train_X = bounds[0] + (bounds[1] - bounds[0]) * train_X  # scale to bounds
train_Y = simulate_batch(train_X)  # YOUR SIMULATOR (returns (n,1) tensor)

# --- Optimization loop ---
for i in range(20):
    gp = SingleTaskGP(train_X, train_Y,
                      input_transform=Normalize(d=d),
                      outcome_transform=Standardize(m=1))
    mll = ExactMarginalLogLikelihood(gp.likelihood, gp)
    fit_gpytorch_mll(mll)

    acq = LogExpectedImprovement(model=gp, best_f=train_Y.max())
    candidate, _ = optimize_acqf(acq, bounds=bounds, q=1,
                                  num_restarts=10, raw_samples=64)

    new_Y = simulate_batch(candidate)
    train_X = torch.cat([train_X, candidate])
    train_Y = torch.cat([train_Y, new_Y])

best_idx = train_Y.argmax()
print(f"Optimal: {train_X[best_idx].tolist()}")
```

### Input
- `train_X`: tensor (n, d) — parameter combinations already tested
- `train_Y`: tensor (n, 1) — objective value (MAXIMIZE)
- `bounds`: tensor (2, d) — [lower; upper]

### Output
- `candidate`: tensor (q, d) — next point(s) to evaluate
- BoTorch MAXIMIZES — negate Y to minimize

### Gotchas
- Luôn dùng `dtype=torch.double` (float32 → GP instability)
- `fit_gpytorch_mll` phải gọi MỖI iteration
- `LogExpectedImprovement` > `ExpectedImprovement` (numerical stability)

---

## Tool 4: JDFTx

### Install (compile from source)
```bash
sudo apt-get install g++ cmake libgsl-dev libopenmpi-dev libfftw3-dev liblapack-dev
git clone https://github.com/shankar1729/jdftx.git
mkdir build && cd build
cmake -D EnableCUDA=yes ../jdftx/jdftx
make -j4
```

### Input Format (plain text `.in` file)
```
# Ni slab in KOH electrolyte
lattice \
    7.41  0.00  0.00 \
    0.00  7.41  0.00 \
    0.00  0.00 30.00

ion-species GBRV/$ID_pbe.uspp
elec-cutoff 20 100
elec-ex-corr gga-PBE
coulomb-interaction Slab 001

# Atomic positions
coords-type cartesian
ion Ni  0.00  0.00  0.00  1
ion Ni  3.70  0.00  0.00  1
# ... more atoms ...

# Solvation (KOH electrolyte)
fluid LinearPCM
pcm-variant CANDLE
fluid-solvent H2O
fluid-cation K+ 1.0
fluid-anion OH- 1.0

# Fixed electrode potential (0.3V vs SHE)
target-mu -0.1743

ionic-minimize nIterations 50
dump End State Forces BoundCharge
```

### Python Helper — Voltage → target-mu
```python
def she_to_mu(V_she, V_ref=4.44):
    """Convert V vs SHE → JDFTx target-mu (Hartrees)"""
    return -(V_ref + V_she) / 27.2114

# Ni oxidation threshold:
print(she_to_mu(0.3))  # 0.3V vs SHE → -0.1743 Ha
```

### Run
```bash
mpirun -np 4 jdftx -i solvated.in -o solvated.out
```

### Output
- `solvated.out`: energy, forces, convergence
- Binary files: wavefunction, electron density, bound charge (solvation)
- Parse with scripts hoặc grep

### Timing & Resources
| System | Atoms | Time | Hardware |
|--------|-------|------|----------|
| Molecule | 3-10 | Phút | 4 CPU cores |
| Surface slab | 20-50 | 1-4 giờ | 16-32 cores hoặc 1 GPU |
| Slab + solvation | 20-50 | 2-8 giờ | 16-32 cores hoặc 1 GPU |

### Không có Python API
- Viết input file bằng Python (string template)
- Chạy subprocess
- Parse output file

---

## Pipeline Kết Hợp

```
BoTorch suggest config (n_layers=2, vacancy=10%, N_doping=5%)
    ↓
Pymatgen/ASE generate Ni@C structure với params đó
    ↓
MACE: NEB → H₂ barrier? O₂ barrier? Shell stable?
    ↓
(nếu PASS) OC20: Ni surface + H → HOR adsorption energy?
    ↓
(top 20) JDFTx: validate TRONG KOH + applied 0.3V
    ↓
BoTorch nhận results → suggest next
    ↓
Loop 20-30 rounds
    ↓
Output: optimal config + ranked candidates
```

---

## Config Schema (Draft — Based on Tool APIs)

```json
{
  "pipeline": "ni_carbon_shell_optimization",
  "phase_a": {
    "tool": "mace",
    "model": "mace_mp_medium",
    "task": "neb_diffusion_barrier",
    "structures": {
      "generator": "ni_at_c_shell",
      "variables": {
        "n_layers": {"type": "int", "range": [1, 3]},
        "vacancy_percent": {"type": "float", "range": [0, 20]},
        "n_doping_percent": {"type": "float", "range": [0, 10]}
      }
    },
    "targets": {
      "h2_barrier_eV": {"direction": "minimize", "threshold": 0.3},
      "o2_barrier_eV": {"direction": "maximize", "threshold": 0.8},
      "shell_stability": {"direction": "maximize"}
    }
  },
  "phase_b": {
    "tool": "jdftx",
    "input_from": "phase_a.top_20",
    "solvation": {"solvent": "H2O", "cation": "K+ 7.0", "anion": "OH- 7.0"},
    "potential_vs_SHE": 0.3,
    "task": "solvated_stability"
  },
  "optimizer": {
    "tool": "botorch",
    "acquisition": "LogExpectedImprovement",
    "n_init": 8,
    "n_iterations": 25,
    "batch_size": 1
  }
}
```
