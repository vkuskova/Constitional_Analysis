# Paper-to-Code Traceability

Every numerical claim in the paper, mapped to its verification check and the
source artifact the check reads. Run `python verify_paper_numbers.py` to
recompute all of them.

Two check kinds:

- **recompute** — the number is recalculated from the raw coded provision data
  (`data/Constitutions_Data.xlsx`) or the similarity matrices / network files.
  This is the strongest form of verification: the paper's number is reproduced
  from upstream source data, not merely read back from a results file.
- **check** — the number is a QAP/MRQAP permutation statistic or an ERGM
  MCMC-MLE coefficient whose recomputation requires the original stochastic
  pipeline (1,000 permutations; 500k-sample MCMC). These are verified against
  the committed result files in `results/`, and the pipeline that produced them
  is documented in the repository.

---

## Section 3 — Data and Table 1

| Paper claim | Value | Check id | Kind | Source artifact |
|---|---|---|---|---|
| Total provisions coded | 659 | `n_provisions_total` | recompute | `data/Constitutions_Data.xlsx` |
| Customary provisions | 465 | `n_provisions_customary` | recompute | `data/Constitutions_Data.xlsx` |
| International provisions | 194 | `n_provisions_international` | recompute | `data/Constitutions_Data.xlsx` |
| Constitutions (countries) | 52 | `n_countries` | recompute | `data/Constitutions_Data.xlsx` |
| Customary cooperative | 210 | `t1_cust_coop` | recompute | `data/Constitutions_Data.xlsx` |
| Customary complementary | 211 | `t1_cust_compl` | recompute | `data/Constitutions_Data.xlsx` |
| Customary competitive | 33 | `t1_cust_comp` | recompute | `data/Constitutions_Data.xlsx` |
| Customary combative | 11 | `t1_cust_comb` | recompute | `data/Constitutions_Data.xlsx` |
| International cooperative | 135 | `t1_intl_coop` | recompute | `data/Constitutions_Data.xlsx` |
| International complementary | 28 | `t1_intl_compl` | recompute | `data/Constitutions_Data.xlsx` |
| International competitive | 31 | `t1_intl_comp` | recompute | `data/Constitutions_Data.xlsx` |
| International combative | 0 | `t1_intl_comb` | recompute | `data/Constitutions_Data.xlsx` |
| Total cooperative | 345 | `t1_total_coop` | recompute | `data/Constitutions_Data.xlsx` |
| Total complementary | 239 | `t1_total_compl` | recompute | `data/Constitutions_Data.xlsx` |
| Total competitive | 64 | `t1_total_comp` | recompute | `data/Constitutions_Data.xlsx` |
| Total combative | 11 | `t1_total_comb` | recompute | `data/Constitutions_Data.xlsx` |
| International cooperative % | 69.6% | `t1_intl_coop_pct` | recompute | `data/Constitutions_Data.xlsx` |
| Customary cooperative % | 45.2%* | `t1_cust_coop_pct` | recompute | `data/Constitutions_Data.xlsx` |
| Customary complementary % | 45.4% | `t1_cust_compl_pct` | recompute | `data/Constitutions_Data.xlsx` |
| Chi-square statistic | 67.71 | `chi2_stat` | recompute | `data/Constitutions_Data.xlsx` |
| Mean customary spectrum score | 0.332 | `spectrum_cust_mean` | recompute | `data/Constitutions_Data.xlsx` |
| SD customary spectrum score | 0.712 | `spectrum_cust_sd` | recompute | `data/Constitutions_Data.xlsx` |
| Mean international spectrum score | 0.536 | `spectrum_intl_mean` | recompute | `data/Constitutions_Data.xlsx` |
| SD international spectrum score | 0.756 | `spectrum_intl_sd` | recompute | `data/Constitutions_Data.xlsx` |

\* **The paper prints 45.3%; the correct value is 45.2%** (210/465 = 45.16%,
which rounds to 45.2). This is a transcription typo flagged by the verifier —
correct it in the paper and in Table 1.

## Section 4 — Measurement and network construction

| Paper claim | Value | Check id | Kind | Source artifact |
|---|---|---|---|---|
| Cross-type QAP correlation | +0.250 | `cross_type_r` | recompute | `data/cust_sim_matrix.csv`, `data/intl_sim_matrix.csv` |
| Spectrum-diff vs cosine r (cust) | −0.725 | `spec_cosine_r_cust` | recompute | `data/customary_network.graphml`, `data/cust_sim_matrix.csv` |
| Spectrum-diff vs cosine r (intl) | −0.745 | `spec_cosine_r_intl` | recompute | `data/international_network.graphml`, `data/intl_sim_matrix.csv` |
| Independent variance, customary | 47% | `indep_var_cust` | recompute | graphml + sim matrix |
| Independent variance, international | 44% | `indep_var_intl` | recompute | graphml + sim matrix |
| Kenya–Nicaragua cosine similarity | 0.271 | `kenya_nicaragua_cosine` | recompute | `data/cust_sim_matrix.csv` |
| Customary network density (75th pct) | ~0.25 | `cust_network_density` | recompute | `data/cust_sim_matrix.csv` |

## Section 4 — Table 2 (QAP bivariate)

| Paper claim | Value | Check id | Kind | Source artifact |
|---|---|---|---|---|
| Same Region r (cust) | −0.002 | `qap_cust_region_r` | check | `results/qap_results_customary.csv` |
| Same Legal Family r (cust) | +0.009 | `qap_cust_legal_r` | check | `results/qap_results_customary.csv` |
| Same Colonial Heritage r (cust) | −0.046 | `qap_cust_colonial_r` | check | `results/qap_results_customary.csv` |
| Spectrum Score Diff r (cust) | −0.728 | `qap_cust_spectrum_r` | check | `results/qap_results_customary.csv` |
| Cross-Type Similarity r (cust) | +0.250 | `qap_cust_crosstype_r` | check | `results/qap_results_customary.csv` |
| Spectrum Score Diff r (intl) | −0.749 | `qap_intl_spectrum_r` | check | `results/qap_results_international.csv` |
| Cross-Type Similarity r (intl) | +0.250 | `qap_intl_crosstype_r` | check | `results/qap_results_international.csv` |

## Section 4 — Table 3 (MRQAP)

| Paper claim | Value | Check id | Kind | Source artifact |
|---|---|---|---|---|
| Spectrum Score Diff beta (cust) | −0.246 | `mrqap_cust_spectrum_beta` | check | `results/mrqap_results_customary.csv` |
| Spectrum Score Diff beta (intl) | −0.233 | `mrqap_intl_spectrum_beta` | check | `results/mrqap_results_international.csv` |
| Cross-Type Similarity beta (intl) | +0.058 | `mrqap_intl_crosstype_beta` | check | `results/mrqap_results_international.csv` |
| Cross-Type Similarity beta (cust) | +0.018 | `mrqap_cust_crosstype_beta` | check | `results/mrqap_results_customary.csv` |

## Section 4 — Table 4 (ERGM Customary)

| Paper claim | Value | Check id | Kind | Source artifact |
|---|---|---|---|---|
| edges estimate | 1.871 | `ergm_cust_edges` | check | `results/ergm_customary_mcmc_results.csv` |
| gwdegree estimate | −2.517 | `ergm_cust_gwdeg` | check | `results/ergm_customary_mcmc_results.csv` |
| nodematch.legal estimate | −0.452 | `ergm_cust_legal` | check | `results/ergm_customary_mcmc_results.csv` |
| nodematch.dominant_cat estimate | 1.999 | `ergm_cust_domcat` | check | `results/ergm_customary_mcmc_results.csv` |
| dominant_cat OR | 7.38 | `ergm_cust_domcat_or` | check | `results/ergm_customary_mcmc_results.csv` |
| absdiff.spectrum_score estimate | −7.383 | `ergm_cust_spectrum` | check | `results/ergm_customary_mcmc_results.csv` |
| colonial.Britain estimate | −0.926 | `ergm_cust_britain` | check | `results/ergm_customary_mcmc_results.csv` |
| colonial.France estimate | −0.923 | `ergm_cust_france` | check | `results/ergm_customary_mcmc_results.csv` |
| colonial.Russia estimate | −1.241 | `ergm_cust_russia` | check | `results/ergm_customary_mcmc_results.csv` |

## Section 4 — Table 5 (ERGM International)

| Paper claim | Value | Check id | Kind | Source artifact |
|---|---|---|---|---|
| edges estimate | −4.894 | `ergm_intl_edges` | check | `results/ergm_international_mcmc_results.csv` |
| gwesp estimate | 2.811 | `ergm_intl_gwesp` | check | `results/ergm_international_mcmc_results.csv` |
| gwesp OR | 16.63 | `ergm_intl_gwesp_or` | check | `results/ergm_international_mcmc_results.csv` |
| nodematch.dominant_cat estimate | 3.321 | `ergm_intl_domcat` | check | `results/ergm_international_mcmc_results.csv` |
| dominant_cat OR | 27.68 | `ergm_intl_domcat_or` | check | `results/ergm_international_mcmc_results.csv` |
| absdiff.spectrum_score estimate | −11.568 | `ergm_intl_spectrum` | check | `results/ergm_international_mcmc_results.csv` |
| colonial.Australia estimate | −2.794 | `ergm_intl_australia` | check | `results/ergm_international_mcmc_results.csv` |
| legal.Common estimate | 1.493 | `ergm_intl_common` | check | `results/ergm_international_mcmc_results.csv` |
| legal.Islamic estimate | 1.592 | `ergm_intl_islamic` | check | `results/ergm_international_mcmc_results.csv` |

## Appendix D — Goodness of Fit

| Paper claim | Value | Check id | Kind | Source artifact |
|---|---|---|---|---|
| Customary GOF all MC p ≥ 0.86 | True | `gof_cust_min_p` | check | `results/ergm_gof_model_statistics.csv` |
| International GOF all MC p ≥ 0.84** | True | `gof_intl_min_p` | check | `results/ergm_gof_model_statistics.csv` |

\*\* **The paper states all MC p-values exceed 0.86; the International network's
GWESP term has p = 0.84.** Update the paper to read "≥ 0.84" (or report the two
networks separately: ≥ 0.86 Customary, ≥ 0.84 International).

---

## Two issues the verifier surfaced

1. **Customary cooperative % typo** — paper says 45.3%, correct value is 45.2%.
2. **International GOF claim** — paper says all MC p-values exceed 0.86, but the
   GWESP term is 0.84. Restate as ≥ 0.84 or report per-network.

## Data note

The source file contains the country under two spellings ("Kyrgyz Republic" for
the customary provisions and "Kyrgyzstan" for the international provisions). The
verifier merges these to a single country, yielding the correct count of 52
constitutions. The underlying spreadsheet should be corrected to use one
spelling consistently.
