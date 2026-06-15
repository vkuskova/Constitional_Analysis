# Paper Number Verifier — Terms of Engagement in Constitutions

Verification bundle for the paper **"Terms of Engagement in Constitutions: The
State and Nonstate Law"** (Powell & Bambrick).

This repository recomputes **every reported number in the paper** from the
committed source data and asserts each matches. No model training, no GPU, runs
in under a minute.

---

## What's in this repository

```
├── README.md                         ← this file
├── verify_paper_numbers.py           ← run this to audit every number
├── verifier_core.py                  ← the CHECKS list (62 checks)
├── requirements.txt                  ← numpy, pandas, scipy, openpyxl
├── PAPER_TO_CODE_TRACEABILITY.md      ← every paper claim → check → source file
├── data/                             ← upstream source artifacts
│   ├── Constitutions_Data.xlsx        ← the 659 coded provisions (raw data)
│   ├── cust_sim_matrix.csv            ← customary cosine similarity matrix
│   ├── intl_sim_matrix.csv            ← international cosine similarity matrix
│   ├── customary_network.graphml      ← customary network + node attributes
│   └── international_network.graphml   ← international network + node attributes
└── results/                          ← committed pipeline outputs
    ├── qap_results_customary.csv
    ├── qap_results_international.csv
    ├── mrqap_results_customary.csv
    ├── mrqap_results_international.csv
    ├── ergm_customary_mcmc_results.csv
    ├── ergm_international_mcmc_results.csv
    └── ergm_gof_model_statistics.csv
```

---

## Run the audit (under one minute, no setup)

```bash
pip install -r requirements.txt
python verify_paper_numbers.py
```

Expected output: `62/62 checks passed`.

The script prints one line per check showing the value printed in the paper next
to the value recomputed from source data, grouped by paper section, with a final
tally.

---

## What the 62 checks cover

Every numerical claim in the paper, organized by section:

- **§3 Data and Table 1** — provision counts (659 total, 465 customary, 194
  international), the full 2×4 category breakdown, column totals, percentages,
  the chi-square test of independence, and the four pooled spectrum-score
  means and standard deviations. All recomputed from the raw coded provisions.
- **§4 Measurement** — the cross-type QAP correlation (r = +0.250), the
  spectrum-difference-vs-cosine correlations and the independent-variance
  percentages used to rebut the mechanical-correlation concern, the
  Kenya–Nicaragua worked example, and the network density at the 75th-percentile
  threshold. All recomputed from the similarity matrices and network files.
- **§4 Table 2 (QAP)** and **Table 3 (MRQAP)** — bivariate correlations and
  multivariate standardized coefficients for all predictors.
- **§4 Tables 4–5 (ERGM)** — every coefficient and odds ratio in both the
  Customary and International models.
- **Appendix D (GOF)** — the goodness-of-fit MC p-value bounds for both networks.

### recompute vs check

Two kinds of verification, both reported by the audit:

- **recompute** — recalculated from the raw coded provision data or the
  similarity/network files. This is the strongest verification: the paper's
  number is reproduced from upstream source data.
- **check** — QAP/MRQAP permutation statistics and ERGM MCMC-MLE coefficients,
  whose recomputation requires the original stochastic pipeline (1,000-permutation
  QAP; 500,000-sample MCMC-MLE). These are verified against the committed result
  files, which the pipeline produced. Because MCMC-MLE estimation is stochastic,
  re-running the ERGM pipeline from scratch reproduces these values to within the
  Monte Carlo standard error (< 0.6); the committed result files are the canonical
  run, fixed by random seed 42.

A per-claim cross-reference is in
[`PAPER_TO_CODE_TRACEABILITY.md`](PAPER_TO_CODE_TRACEABILITY.md).

---

## Two discrepancies the verifier found

The audit is configured to assert the **true** recomputed values, and in two
places those differ from what the current paper draft prints:

1. **Customary cooperative percentage.** The paper prints **45.3%**; the correct
   value is **45.2%** (210/465 = 45.16%). A rounding/transcription typo — correct
   it in the text and Table 1.
2. **International GOF p-value bound.** The paper states all MC p-values exceed
   **0.86**; the International network's GWESP term is **0.84**. Restate as
   "≥ 0.84," or report the two networks separately (≥ 0.86 Customary, ≥ 0.84
   International).

Both are minor and easily corrected, but they are exactly the kind of number a
reviewer might spot-check — fixing them before submission removes two avoidable
queries.

---

## Reproducibility notes

- **Exact vs. tolerance checks.** Integer counts are checked exactly. Real-valued
  quantities (correlations, coefficients, percentages) are checked within a tight
  tolerance to absorb rounding in the paper's printed precision.
- **The Kyrgyzstan spelling.** The source spreadsheet lists the country under two
  spellings ("Kyrgyz Republic" for customary provisions, "Kyrgyzstan" for
  international). The verifier merges them, recovering the correct count of 52
  constitutions. The spreadsheet should be corrected to one spelling.
- **Spectrum scores.** The §3 spectrum-score statistics are the pooled mean across
  all provisions of a given type (matching the paper). Note this differs from the
  per-country mean stored as a node attribute in the graphml files, which is used
  for the network analysis — both are correct but measure different things.

---

## License

- **Code**: MIT.
- **Data**: the coded provision dataset is the authors'; the structural predictor
  sources (region, legal family, colonial heritage) are from World Bank (2024),
  La Porta et al. (1998), and Hensel (2014) respectively, as cited in the paper.
