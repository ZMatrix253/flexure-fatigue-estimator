# flexure-fatigue-estimator

# PRODUCT_BRIEF.md  
**Flexure Fatigue Estimator (FFE)**  
Version 0.1 – Starter Scope

## 1. Product Vision
FFE is a focused engineering software product that lets a user define simple compliant flexure geometries, apply cyclic loads, run structural analysis, extract relevant stress histories, and obtain a stress-life (S-N) fatigue estimate with safety factors and an automatically generated engineering report.

It is intentionally scoped as a starter project: clean product surface for the end user, solid mechanics + durability engineering under the hood. The tool prioritises usability and reliable basic results over full multi-physics or highly complex geometries.

## 2. Exact Allowed Scope (v0.1)

### Geometry
- **Only** rectangular cross-section cantilever leaf spring  
  - Parameters: length \(L\), width \(b\), thickness \(h\)  
  - Fixed at one end, free at the other  
  - No fillets, no variable thickness, no other shapes

### Loading
- Cyclic tip force (point load at free end)
- Constant amplitude
- User-specified force amplitude \(F_a\) and R-ratio (\(R = F_{min}/F_{max}\))
- Fully reversed (\(R = -1\)) or with mean force supported

### Material Model
- Linear elastic only  
  - Isotropic: Young’s modulus \(E\), Poisson’s ratio \(\nu\)  
  - No plasticity, no hyperelasticity, no temperature dependence

### Fatigue Method
- Stress-life (S-N) approach  
- Basquin’s equation for the high-cycle regime  
- Goodman mean-stress correction  
- Output: estimated cycles to failure \(N_f\), safety factor on life and/or stress, and a simple engineering report (PDF or Markdown)

## 3. Explicit Non-Goals (v0.1)
- No 3-D CAD import or free-form geometry
- No plasticity or nonlinear material behaviour
- No multi-physics (thermal, fluid, contact, large deformation geometric nonlinearity beyond basic beam theory)
- No complex meshes or full 3-D finite-element analysis
- No multi-body mechanisms, no assemblies, no time-varying load spectra beyond constant-amplitude cycles

## 4. Recommended Core Workflow
1. User inputs geometry parameters + material properties + load (\(F_a\), \(R\))
2. Analytical beam theory (or simple 1-D FE beam model) computes max bending stress history
3. Apply Goodman correction → equivalent fully-reversed stress
4. Basquin evaluation → \(N_f\) + safety factors
5. Auto-generate concise engineering report

## 5. Success Criteria for v0.1
- Correct analytical stress for a rectangular cantilever under tip load
- Correct Basquin + Goodman calculation against textbook examples
- Clean, single-page GUI or CLI that a mechanical engineer can use in < 2 minutes
- Reproducible report that can be dropped into a design review

This tight scope keeps the product honest, shippable, and a solid foundation for later expansion (additional geometries, nonlinear effects, etc.).