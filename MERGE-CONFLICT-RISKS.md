# Merge Conflict Risk Analysis
**Branch:** `feat/opik-eval-explore`
**Base:** `main`
**Created:** 2026-01-27

## Purpose
This document identifies files modified in `feat/opik-eval-explore` that could cause merge conflicts if you make changes to them in `main` before merging this branch.

---

## ⚠️ High Risk Files (Modified in Both Places = Conflict)

If you modify these files in `main`, you **will** get merge conflicts when merging this branch:

### 1. `backend/api/services/ai_agent_service.py`
**Lines changed:** ~100 additions
**What this branch changed:**
- Added Opik tracking with `OpikTracer` and `opik_context`
- Added cost tracking imports from `backend.core.llm_utils`
- Added `get_user_context()` function to extract skill level and metrics
- Enhanced tracing metadata throughout

**Conflict risk if you:**
- Modify the imports section
- Change the `get_opik_config()` function
- Add new tracking or monitoring code
- Refactor the AI agent flow

---

### 2. `backend/api/services/live_coach_service.py`
**Lines changed:** ~92 additions
**What this branch changed:**
- Added Opik tracking and cost tracking imports
- Added `ProductionAutoScorer` for auto-scoring feedback quality
- Enhanced `generate_coaching_feedback()` with cost tracking
- Added session metrics to trace metadata

**Conflict risk if you:**
- Modify the imports section
- Change `generate_coaching_feedback()` function
- Add new monitoring or tracking
- Modify the coaching prompt or response handling

---

### 3. `.gitignore`
**Lines changed:** +17 additions
**What this branch changed:**
- Added Opik planning docs to ignore list:
  - `opik-plan/`
  - `PHASE*-VALIDATION.md`
  - `OPIK-IMPACT-REPORT.md`
  - `DEMO-SCRIPT.md`
- Added generated evaluation artifacts:
  - `baseline_experiments.json`
  - `optimization_results.json`
  - `dashboard_configs.json`
  - `online_evaluation_rules.json`

**Conflict risk if you:**
- Add new entries to `.gitignore` (especially at the end of file)
- Remove or reorganize ignore patterns

---

### 4. `opik/opik-usage.md`
**Lines changed:** ~253 additions
**What this branch changed:**
- Extensive documentation updates for Opik integration
- Usage examples and configuration details

**Conflict risk if you:**
- Update Opik documentation
- Add new sections to this doc

---

### 5. `web/web-backend/tools/database_tools.py`
**Lines changed:** ~81 additions
**What this branch changed:**
- Database utility enhancements (need to check specific changes)

**Conflict risk if you:**
- Modify database tools or queries
- Add new database utilities

---

## ✅ Low Risk Files (New in This Branch)

These files are **new** in this branch, so they won't conflict unless you also create files with the same names in `main`:

- `backend/core/llm_utils.py` - New utility for cost tracking
- `evaluation/` - Entire new directory with evaluation scripts:
  - `create_datasets.py`
  - `custom_metrics.py`
  - `optimize_prompts.py`
  - `production_monitoring.py`
  - `run_baseline_experiments.py`
  - `run_experiments.py`
  - `setup_online_rules.py`

---

## 📋 Recommendations

### If you need to work on `main` while this branch is in progress:

1. **Avoid modifying these files in `main`:**
   - `backend/api/services/ai_agent_service.py`
   - `backend/api/services/live_coach_service.py`

2. **Safe to modify in `main`:**
   - Any frontend code
   - Database schemas (but not `database_tools.py`)
   - New features that don't touch AI/coaching services
   - Tests (unless they test the modified services)

3. **If you must modify a high-risk file:**
   - Create a separate feature branch from `main`
   - Merge this evaluation branch first, then work on the new feature
   - Or coordinate changes to avoid the same code sections

4. **When ready to merge this branch:**
   - Pull latest `main` first
   - Resolve any conflicts carefully
   - Test all Opik integration points
   - Verify evaluation scripts still work

---

## 🔍 Quick Conflict Check Command

Before merging, run this to preview conflicts:

```bash
git checkout feat/opik-eval-explore
git fetch origin main
git merge-tree $(git merge-base main HEAD) main HEAD | grep -A 5 "changed in both"
```

---

## 📊 Branch Stats

```
Total files changed: 15
Lines added: 3,548
Lines removed: 51

Modified files: 5
New files: 10
```
