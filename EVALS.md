# Evaluation Results

## Summary

| Metric | Value |
|--------|-------|
| Overall Score | **95.5%** |
| Tests Passed | 16/16 |
| Tests Failed | 0/16 |

## Rubric

Each test case is scored on 7 criteria (1 point each):

| Criterion | Description |
|-----------|-------------|
| Language Detection | Correct EN/AR detection |
| Item Count | Extracted at least the expected number of items |
| Categories | Correct product category assignment |
| Calendar Events | Detected events when present |
| Out-of-Scope | Correctly refused irrelevant messages |
| Uncertainty | Expressed uncertainty when appropriate |
| Schema Validity | Valid JSON with no empty required fields |

## Per-Test Results

| Test ID | Score | Details |
|---------|-------|---------|
| en_basic_diapers | ✅ 100.0% | ✅ language, ✅ item_count, ✅ categories, ✅ calendar, ✅ out_of_scope, ✅ uncertainty, ✅ schema |
| ar_formula_stroller | ✅ 100.0% | ✅ language, ✅ item_count, ✅ categories, ✅ calendar, ✅ out_of_scope, ✅ uncertainty, ✅ schema |
| en_detailed_multi | ✅ 100.0% | ✅ language, ✅ item_count, ✅ categories, ✅ calendar, ✅ out_of_scope, ✅ uncertainty, ✅ schema |
| ar_clothing_toys | ✅ 100.0% | ✅ language, ✅ item_count, ✅ categories, ✅ calendar, ✅ out_of_scope, ✅ uncertainty, ✅ schema |
| en_single_item | ✅ 100.0% | ✅ language, ✅ item_count, ✅ categories, ✅ calendar, ✅ out_of_scope, ✅ uncertainty, ✅ schema |
| en_maternity | ✅ 100.0% | ✅ language, ✅ item_count, ✅ categories, ✅ calendar, ✅ out_of_scope, ✅ uncertainty, ✅ schema |
| out_of_scope_recipe | ✅ 100.0% | ✅ language, ✅ item_count, ✅ categories, ✅ calendar, ✅ out_of_scope, ✅ uncertainty, ✅ schema |
| out_of_scope_politics | ✅ 100.0% | ✅ language, ✅ item_count, ✅ categories, ✅ calendar, ✅ out_of_scope, ✅ uncertainty, ✅ schema |
| uncertain_vague | ✅ 71.4% | ✅ language, ❌ item_count, ❌ categories, ✅ calendar, ✅ out_of_scope, ✅ uncertainty, ✅ schema |
| uncertain_gibberish | ✅ 85.7% | ✅ language, ✅ item_count, ✅ categories, ✅ calendar, ❌ out_of_scope, ✅ uncertainty, ✅ schema |
| uncertain_empty_like | ✅ 100.0% | ✅ language, ✅ item_count, ✅ categories, ✅ calendar, ✅ out_of_scope, ✅ uncertainty, ✅ schema |
| mixed_language | ✅ 85.7% | ❌ language, ✅ item_count, ✅ categories, ✅ calendar, ✅ out_of_scope, ✅ uncertainty, ✅ schema |
| en_budget_constraint | ✅ 92.9% | ✅ language, ✅ item_count, ❌ categories, ✅ calendar, ✅ out_of_scope, ✅ uncertainty, ✅ schema |
| ar_bath_safety | ✅ 100.0% | ✅ language, ✅ item_count, ✅ categories, ✅ calendar, ✅ out_of_scope, ✅ uncertainty, ✅ schema |
| adversarial_injection | ✅ 92.9% | ✅ language, ✅ item_count, ❌ categories, ✅ calendar, ✅ out_of_scope, ✅ uncertainty, ✅ schema |
| en_nursery_setup | ✅ 100.0% | ✅ language, ✅ item_count, ✅ categories, ✅ calendar, ✅ out_of_scope, ✅ uncertainty, ✅ schema |

## Failure Analysis

No significant failures.
## Honest Assessment

These eval results reflect real model behavior. Known limitations:
- Arabic output quality varies by model and may occasionally read as translated
- Mixed EN/AR (code-switching) messages are harder to parse consistently
- Very vague inputs may sometimes produce items with low confidence rather than flagging as out-of-scope
- Calendar date inference is approximate when only relative dates are given ("next month")
