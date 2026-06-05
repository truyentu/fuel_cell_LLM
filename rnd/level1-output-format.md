# Level 1 Output Format — Cho Level 2 Engine

Date: 2026-06-03
Purpose: Define chính xác output format mà `/scientist plan` phải tạo để Level 2 engine đọc được.

---

## Tổng Quan

`/scientist plan` output 2 files:

| File | Format | Đọc bởi | Mục đích |
|------|--------|---------|----------|
| `rnd/experiments/<topic>-plan.md` | Markdown | Người đọc | Giải thích plan cho user |
| `rnd/experiments/<topic>-config.json` | JSON | Engine code | Machine-readable, feed vào GPU |

---

## File 1: `<topic>-plan.md` (Cho Người Đọc)

```markdown
# Experiment Plan — [Topic]

| Field | Value |
|-------|-------|
| Date | YYYY-MM-DD |
| Phase | Validation |
| Goal | [1 câu mô tả mục tiêu] |
| Config file | [link to config.json] |
| Estimated compute | [giờ × GPU type] |
| Estimated cost | [$X] |

## Tại Sao Chạy Plan Này

[2-3 câu context: vấn đề gì, tại sao cần simulate]

## Sẽ Tìm Gì

| Target | Nghĩa | Giá trị tốt | Source |
|--------|--------|-------------|--------|
| H adsorption energy | HOR activity | Gần -0.27 eV (như Pt) | [FACT/REASONING + source] |
| H₂ diffusion barrier | H₂ qua shell dễ không | < 0.3 eV | [FACT/REASONING + source] |
| ... | ... | ... | ... |

## Search Space

| Variable | Range | Tại sao range này |
|----------|-------|-------------------|
| Ni:Mo ratio | 70:30 → 100:0 | [Source hoặc reasoning] |
| Shell layers | 1–3 | [Source] |
| ... | ... | ... |

## Pipeline

[Mô tả flow: tool nào → tool nào → output gì]

## Risks & Assumptions

- [REASONING] Assumption 1: ...
- [REASONING] Assumption 2: ...
- [GAP] Cần verify: ...

## Confidence: [HIGH/MEDIUM/LOW]
```

---

## File 2: `<topic>-config.json` (Cho Engine)

### Schema Đầy Đủ

```json
{
  "meta": {
    "pipeline": "string — tên pipeline (snake_case)",
    "created_by": "scientist_level1",
    "date": "YYYY-MM-DD",
    "goal": "string — 1 câu mô tả",
    "plan_file": "string — path to plan.md",
    "source_confidence": "HIGH | MEDIUM | LOW"
  },

  "search_space": {
    "description": "Các biến cần optimize",
    "variables": {
      "<var_name>": {
        "type": "int | float | categorical",
        "range": [min, max],
        "step": "number (optional, cho int/float)",
        "values": ["list (cho categorical)"],
        "units": "string (optional)",
        "source": "string — [FACT/REASONING] + paper name"
      }
    },
    "fixed_conditions": {
      "<condition_name>": {
        "value": "any",
        "units": "string",
        "source": "string"
      }
    }
  },

  "targets": {
    "<target_name>": {
      "metric": "string — tên metric engine sẽ tính",
      "direction": "minimize | maximize | minimize_distance_to",
      "reference": "number (chỉ khi direction = minimize_distance_to)",
      "threshold": "number — ngưỡng pass/fail",
      "units": "string",
      "source": "string — [FACT/REASONING] + paper",
      "priority": "int 1-5 (1 = quan trọng nhất)"
    }
  },

  "tools": {
    "screening": {
      "tool": "fairchem",
      "model": "string — model name",
      "task_name": "oc20 | omat | omol",
      "evaluates": ["list target_names tool này tính"],
      "settings": {}
    },
    "simulation": {
      "tool": "mace",
      "model": "string — mace_mp_medium | custom path",
      "device": "cuda | cpu",
      "evaluates": ["list target_names"],
      "settings": {
        "neb_images": "int (default 5)",
        "neb_fmax": "float (default 0.05)",
        "md_steps": "int",
        "md_timestep_fs": "float",
        "md_temperature_K": "float"
      }
    },
    "validation": {
      "tool": "jdftx",
      "when": "top_n | all | skip",
      "n": "int",
      "evaluates": ["list target_names"],
      "settings": {
        "solvation": {
          "solvent": "H2O",
          "cation": "string — 'K+ 7.0'",
          "anion": "string — 'OH- 7.0'"
        },
        "potential_vs_SHE": "float",
        "cutoff_Ry": "int (default 20)",
        "kpoints": "string (optional)"
      }
    }
  },

  "optimizer": {
    "tool": "botorch",
    "type": "single_objective | multi_objective",
    "objectives": ["list target_names to optimize"],
    "constraints": [
      {
        "metric": "string — target_name",
        "operator": "< | > | <= | >= | ==",
        "value": "number"
      }
    ],
    "n_init": "int — random samples ban đầu (default 8)",
    "n_iterations": "int — BO rounds (default 25)",
    "batch_size": "int — candidates mỗi round (default 1)",
    "acquisition": "LogExpectedImprovement | qLogExpectedHypervolumeImprovement | UpperConfidenceBound"
  },

  "structure_generator": {
    "type": "string — generator function name",
    "base_structure": "string — path to base .xyz/.traj file (optional)",
    "description": "string — how to build structure from variables"
  },

  "output": {
    "dir": "rnd/compute/<pipeline_name>/",
    "results_csv": "results.csv",
    "ranked_md": "ranked_candidates.md",
    "pareto_plot": "pareto.png",
    "best_structure": "best_candidate.xyz"
  }
}
```

---

## Validation Rules (Engine PHẢI Check)

### Reject config nếu:

```
1. meta.source_confidence == "LOW" → WARNING, hỏi user confirm
2. Bất kỳ target.source chứa "[UNVERIFIED]" → REJECT
   "Cannot run simulation on unverified data. Need paper confirmation."
3. search_space.variables range vô lý:
   - range[0] >= range[1]
   - percent > 100 hoặc < 0
   - n_layers <= 0
4. tools.*.tool không nằm trong installed tools
5. tools.*.device == "cuda" nhưng torch.cuda.is_available() == False
6. optimizer.objectives reference target_name không tồn tại
7. optimizer.constraints reference metric không tồn tại
```

### Warning (không reject, nhưng log):

```
1. n_iterations > 50 → "Consider reducing — diminishing returns after 30"
2. search_space total combinations > 10,000 → "Large space — ensure n_iterations sufficient"
3. tools.validation.when == "skip" → "No JDFTx validation — results less reliable in electrolyte"
```

---

## Ví Dụ Hoàn Chỉnh — Ni@C Shell Optimization

```json
{
  "meta": {
    "pipeline": "ni_carbon_shell_optimization",
    "created_by": "scientist_level1",
    "date": "2026-06-03",
    "goal": "Find optimal Ni-alloy composition + carbon shell for PGM-free AEMFC HOR anode",
    "plan_file": "rnd/experiments/carbon-shell-plan.md",
    "source_confidence": "HIGH"
  },

  "search_space": {
    "description": "Ni alloy composition + carbon shell structure",
    "variables": {
      "dopant_type": {
        "type": "categorical",
        "values": ["Mo", "Fe", "Co", "none"],
        "source": "[REASONING] Common HOR-active Ni alloys in alkaline"
      },
      "dopant_percent": {
        "type": "float",
        "range": [0, 30],
        "step": 5,
        "units": "at%",
        "source": "[REASONING] >30% destabilizes FCC structure"
      },
      "n_layers": {
        "type": "int",
        "range": [1, 3],
        "units": "graphene layers",
        "source": "[FACT] Paper tested 1-3 layers — Source: Unveiling...Ni oxidation state"
      },
      "vacancy_percent": {
        "type": "float",
        "range": [0, 20],
        "step": 2,
        "units": "%",
        "source": "[REASONING] Defects needed for H₂ permeation, >20% = unstable"
      },
      "n_doping_percent": {
        "type": "float",
        "range": [0, 10],
        "step": 2,
        "units": "%",
        "source": "[REASONING] N-doping may stabilize shell + modify permeation"
      }
    },
    "fixed_conditions": {
      "temperature_K": {
        "value": 343,
        "units": "K",
        "source": "[FACT] AEMFC operates at 70°C — Source: Unveiling...Ni oxidation state"
      },
      "electrolyte": {
        "value": "KOH 7M",
        "units": "",
        "source": "[FACT] Standard AEMFC electrolyte"
      },
      "potential_vs_SHE": {
        "value": 0.3,
        "units": "V",
        "source": "[FACT] Ni oxidizes above 0.3V vs RHE — Source: Unveiling...Ni oxidation state"
      }
    }
  },

  "targets": {
    "hor_activity": {
      "metric": "H_adsorption_energy_eV",
      "direction": "minimize_distance_to",
      "reference": -0.27,
      "threshold": 0.15,
      "units": "eV",
      "source": "[FACT] Pt optimal H binding ~-0.27 eV (Sabatier principle)",
      "priority": 1
    },
    "h2_barrier": {
      "metric": "neb_h2_barrier_eV",
      "direction": "minimize",
      "threshold": 0.3,
      "units": "eV",
      "source": "[REASONING] H₂ kinetic diameter 0.29 nm, needs low barrier through shell",
      "priority": 2
    },
    "o2_barrier": {
      "metric": "neb_o2_barrier_eV",
      "direction": "maximize",
      "threshold": 0.8,
      "units": "eV",
      "source": "[REASONING] O₂ kinetic diameter 0.35 nm, must be blocked to prevent Ni oxidation",
      "priority": 2
    },
    "shell_stability": {
      "metric": "md_intact_ratio",
      "direction": "maximize",
      "threshold": 0.95,
      "units": "fraction",
      "source": "[REASONING] Shell must remain >95% intact after 10 ps MD at 343K",
      "priority": 3
    }
  },

  "tools": {
    "screening": {
      "tool": "fairchem",
      "model": "uma-s-1p2",
      "task_name": "oc20",
      "evaluates": ["hor_activity"],
      "settings": {
        "fmax": 0.05,
        "max_steps": 200
      }
    },
    "simulation": {
      "tool": "mace",
      "model": "mace_mp_medium",
      "device": "cuda",
      "evaluates": ["h2_barrier", "o2_barrier", "shell_stability"],
      "settings": {
        "neb_images": 5,
        "neb_fmax": 0.05,
        "md_steps": 10000,
        "md_timestep_fs": 1.0,
        "md_temperature_K": 343
      }
    },
    "validation": {
      "tool": "jdftx",
      "when": "top_n",
      "n": 5,
      "evaluates": ["hor_activity", "shell_stability"],
      "settings": {
        "solvation": {
          "solvent": "H2O",
          "cation": "K+ 7.0",
          "anion": "OH- 7.0"
        },
        "potential_vs_SHE": 0.3,
        "cutoff_Ry": 20
      }
    }
  },

  "optimizer": {
    "tool": "botorch",
    "type": "multi_objective",
    "objectives": ["hor_activity", "shell_stability"],
    "constraints": [
      {"metric": "h2_barrier", "operator": "<", "value": 0.3},
      {"metric": "o2_barrier", "operator": ">", "value": 0.8}
    ],
    "n_init": 8,
    "n_iterations": 25,
    "batch_size": 1,
    "acquisition": "qLogExpectedHypervolumeImprovement"
  },

  "structure_generator": {
    "type": "ni_at_c_shell_generator",
    "base_structure": null,
    "description": "Generate Ni/NiX nanoparticle (2nm) wrapped in graphene shell with specified layers, vacancy%, N-doping%"
  },

  "output": {
    "dir": "rnd/compute/ni_carbon_shell_optimization/",
    "results_csv": "results.csv",
    "ranked_md": "ranked_candidates.md",
    "pareto_plot": "pareto.png",
    "best_structure": "best_candidate.xyz"
  }
}
```

---

## Mapping: Level 1 Concepts → Config Fields

| Level 1 (Scientist) nói | Config field |
|--------------------------|-------------|
| "Thử NiMo, NiFe, NiCo" | `search_space.variables.dopant_type.values` |
| "1-3 layers carbon shell" | `search_space.variables.n_layers.range` |
| "HOR activity gần Pt" | `targets.hor_activity.reference = -0.27` |
| "Shell phải chặn O₂" | `targets.o2_barrier.threshold = 0.8` |
| "Chạy ở 70°C trong KOH" | `search_space.fixed_conditions` |
| "Top 5 validate bằng JDFTx" | `tools.validation.n = 5` |
| "Bayesian optimize 25 rounds" | `optimizer.n_iterations = 25` |

---

## Traceability Chain

```
Paper → NotebookLM → /scientist plan [FACT] → config.json "source" field
                                                      ↓
                                              Engine validate:
                                              - [FACT] → accept
                                              - [REASONING] → accept with warning
                                              - [UNVERIFIED] → REJECT
```

---

## Checklist Cho `/scientist plan` Khi Tạo Config

```
[ ] Mọi variable range có source tag?
[ ] Mọi target threshold có source tag?
[ ] Không có [UNVERIFIED] data trong targets?
[ ] fixed_conditions đủ? (temperature, electrolyte, potential)
[ ] structure_generator.type defined? (engine biết build structure nào)
[ ] output.dir unique? (không ghi đè run cũ)
[ ] meta.source_confidence phản ánh đúng data quality?
```
