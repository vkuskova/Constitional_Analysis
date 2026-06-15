# Terms of Engagement in Constitutions — Paper Number Verifier

Reproducibility bundle for **"Terms of Engagement in Constitutions: The State and
Nonstate Law"** (Powell & Bambrick).

This repository lets anyone **verify every reported number in the paper** by
recomputing it from the source data. No model training, no GPU, runs in about
30 seconds in Google Colab.

---

## What's in this repository

```
├── README.md                              ← this file
├── Constitutions_Verifier_Colab.ipynb     ← the notebook — open this in Colab
├── constitutions-reproducibility.tar.gz   ← the bundle (all data, results, and the audit code)
└── PAPER_TO_CODE_TRACEABILITY.md          ← every paper number → check → source file
```

The **bundle** (`constitutions-reproducibility.tar.gz`) is the canonical
artifact. It contains everything needed to verify the paper:

```
constitutions-reproducibility.tar.gz
├── verifier_core.py                  ← the 62 checks
├── requirements.txt                  ← numpy, pandas, scipy, openpyxl
├── PAPER_TO_CODE_TRACEABILITY.md
├── data/                             ← upstream source data
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

## How to verify every number (Colab, no setup)

1. Open **`Constitutions_Verifier_Colab.ipynb`** in
   [Google Colab](https://colab.research.google.com) (**File → Upload notebook**).
2. **Cell 1 — get the bundle.** Choose one option in the cell's dropdown:
   - **Upload from computer:** download `constitutions-reproducibility.tar.gz`
     from this repository, then run the cell and upload it.
   - **Google Drive:** put the tarball on your Drive, set the path in the cell,
     and run it to mount Drive and load the bundle.
3. **Cell 2 — unpack & install.** Unpacks the bundle and installs the four Python
   dependencies.
4. **Cell 3 — run the audit.** Executes all 62 checks.

Expected output:

```
62/62 checks passed
```

Each check prints the value as printed in the paper next to the value recomputed
from source data, grouped by paper section.

---

## What the 62 checks cover

Every numerical claim in the paper, organized by section:

| Section | Checks | What is verified |
|---|---|---|
| §3 Data + Table 1 | 24 | Provision counts (659 total; 465 customary; 194 international), the full 2×4 category breakdown, column totals, percentages, the chi-square test, and all four pooled spectrum-score means and SDs |
| §4 Measurement | 7 | Cross-type QAP correlation (r = +0.250), spectrum-vs-cosine correlations and independent-variance percentages, the Kenya–Nicaragua worked example, and 75th-percentile network density |
| §4 Table 2 (QAP) | 7 | Bivariate correlations for all predictors, both networks |
| §4 Table 3 (MRQAP) | 4 | Multivariate standardized coefficients |
| §4 Table 4 (ERGM customary) | 9 | Every coefficient and odds ratio |
| §4 Table 5 (ERGM international) | 9 | Every coefficient and odds ratio |
| Appendix D (GOF) | 2 | Goodness-of-fit MC p-value bounds, both networks |

A full per-claim cross-reference — every paper number mapped to its check ID and
the exact source file — is in
[`PAPER_TO_CODE_TRACEABILITY.md`](PAPER_TO_CODE_TRACEABILITY.md).

### Two kinds of verification

- **recompute** (35 checks): the number is recalculated from the raw coded
  provision data or the similarity/network files. This is the strongest form of
  verification — the paper's number is reproduced from upstream source data, not
  just read back from a results file.
- **check** (27 checks): QAP/MRQAP permutation statistics and ERGM MCMC-MLE
  coefficients, whose recomputation requires the original stochastic pipeline
  (1,000-permutation QAP; 500,000-sample MCMC-MLE estimated in R via `statnet`).
  These are verified against the committed result files. Because MCMC-MLE is
  stochastic, re-running the ERGM pipeline reproduces these values to within the
  Monte Carlo standard error (< 0.6); the committed files are the canonical run,
  fixed by random seed 42.

---

## Notes

- **Tolerances.** Integer counts are checked exactly. Real-valued quantities
  (correlations, coefficients, percentages) are checked within a tight tolerance
  to absorb rounding in the paper's printed precision.
- **Spectrum scores.** The §3 spectrum statistics are the pooled mean across all
  provisions of a given type (as reported in the paper). This differs from the
  per-country mean stored as a node attribute in the graphml files, which is used
  for the network analysis — both are correct but measure different things.
- **Country spelling.** The source spreadsheet lists one country under two
  spellings ("Kyrgyz Republic" / "Kyrgyzstan"); the audit merges them to recover
  the correct count of 52 constitutions.

---

## License

- **Code:** MIT.
- **Coded provision data:** the authors'.
- **Structural predictors** (region, legal family, colonial heritage): World Bank
  (2024), La Porta et al. (1998), and Hensel (2014) respectively, as cited in the
  paper. Provided for reproducibility; cite the original sources if reused.

## Contact

Anonymized for double-blind review. Please direct questions through the review
system for this submission.
