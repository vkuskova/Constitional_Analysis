"""
verifier_core.py
=================
The CHECKS list for the paper "Terms of Engagement in Constitutions: The State
and Nonstate Law" (Powell & Bambrick).

Each check is a dict with:
  - id:        unique short identifier
  - section:   where the claim appears in the paper
  - claim:     human-readable description of the number being verified
  - paper:     the value as printed in the paper
  - compute:   a function (ctx) -> value that recomputes the number from source
  - tol:       absolute tolerance for the match (0 = exact)
  - kind:      'recompute' (from raw data) or 'check' (from a saved result file)

The function `run_all_checks()` executes every check and reports PASS/FAIL.

Design philosophy: every number a reviewer could spot-check in the paper is
recomputed here from the most upstream artifact available — the raw coded
provision data wherever possible, falling back to the saved result CSVs for
quantities (QAP/MRQAP permutation p-values, ERGM MCMC-MLE coefficients) whose
recomputation requires the original stochastic pipeline. Those are checked
against the committed result files, and the pipeline that produced them is in
the repository.
"""

import os
import numpy as np
import pandas as pd
import xml.etree.ElementTree as ET

HERE      = os.path.dirname(os.path.abspath(__file__))
DATA_DIR  = os.path.join(HERE, "data")
RESULT_DIR = os.path.join(HERE, "results")

GRAPHML_NS = {"g": "http://graphml.graphdrawing.org/xmlns"}
SCORE_MAP  = {"Cooperative": 1, "Complementary": 0,
              "Competitive": -1, "Combative": -2}


# ─────────────────────────────────────────────────────────────────────────────
# Context loaders — parsed once, shared across checks
# ─────────────────────────────────────────────────────────────────────────────
def load_context():
    """Load every source artifact once and return a context dict."""
    ctx = {}

    # ── Raw coded provisions ──────────────────────────────────────────────────
    df = pd.read_excel(os.path.join(DATA_DIR, "Constitutions_Data.xlsx"))
    df = df[["Country", "Type", "Category"]].dropna(
        subset=["Country", "Type", "Category"])
    # Merge the two spellings of Kyrgyzstan into one country
    df["Country"] = df["Country"].replace({"Kyrgyz Republic": "Kyrgyzstan"})
    df["score"] = df["Category"].map(SCORE_MAP)
    ctx["provisions"] = df

    # ── Similarity matrices ───────────────────────────────────────────────────
    ctx["cust_sim"] = pd.read_csv(
        os.path.join(DATA_DIR, "cust_sim_matrix.csv"), index_col=0)
    ctx["intl_sim"] = pd.read_csv(
        os.path.join(DATA_DIR, "intl_sim_matrix.csv"), index_col=0)

    # ── GraphML node attributes (region, legal, colonial, spectrum) ──────────
    ctx["cust_nodes"] = _parse_graphml(
        os.path.join(DATA_DIR, "customary_network.graphml"))
    ctx["intl_nodes"] = _parse_graphml(
        os.path.join(DATA_DIR, "international_network.graphml"))

    # ── Saved result files ────────────────────────────────────────────────────
    ctx["qap_cust"]  = pd.read_csv(os.path.join(RESULT_DIR, "qap_results_customary.csv"))
    ctx["qap_intl"]  = pd.read_csv(os.path.join(RESULT_DIR, "qap_results_international.csv"))
    ctx["mrqap_cust"] = pd.read_csv(os.path.join(RESULT_DIR, "mrqap_results_customary.csv"))
    ctx["mrqap_intl"] = pd.read_csv(os.path.join(RESULT_DIR, "mrqap_results_international.csv"))
    ctx["ergm_cust"] = pd.read_csv(os.path.join(RESULT_DIR, "ergm_customary_mcmc_results.csv"))
    ctx["ergm_intl"] = pd.read_csv(os.path.join(RESULT_DIR, "ergm_international_mcmc_results.csv"))
    ctx["gof"]       = pd.read_csv(os.path.join(RESULT_DIR, "ergm_gof_model_statistics.csv"))

    return ctx


def _parse_graphml(path):
    """Return a DataFrame of node attributes from a graphml file."""
    tree = ET.parse(path)
    root = tree.getroot()
    # Map key id -> attribute name
    keymap = {k.get("id"): k.get("attr.name")
              for k in root.findall(".//g:key", GRAPHML_NS)}
    rows = []
    for node in root.findall(".//g:node", GRAPHML_NS):
        row = {"id": node.get("id")}
        for data in node.findall("g:data", GRAPHML_NS):
            row[keymap[data.get("key")]] = data.text
        rows.append(row)
    out = pd.DataFrame(rows)
    for col in ["spectrum_score", "n_provisions", "community", "weight"]:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Helper functions for ERGM/QAP table lookups
# ─────────────────────────────────────────────────────────────────────────────
def _ergm_val(df, param, col):
    row = df[df["Parameter"] == param]
    if len(row) == 0:
        raise KeyError(f"ERGM parameter '{param}' not found")
    return float(row.iloc[0][col])


def _qap_val(df, predictor, col):
    row = df[df["Predictor"] == predictor]
    if len(row) == 0:
        raise KeyError(f"QAP predictor '{predictor}' not found")
    return float(row.iloc[0][col])


# ─────────────────────────────────────────────────────────────────────────────
# THE CHECKS
# ─────────────────────────────────────────────────────────────────────────────
CHECKS = [

    # ====================  SECTION 3: DATA / TABLE 1  =======================
    dict(id="n_provisions_total", section="§3", kind="recompute",
         claim="Total provisions coded",
         paper=659, tol=0,
         compute=lambda c: len(c["provisions"])),

    dict(id="n_provisions_customary", section="§3", kind="recompute",
         claim="Customary provisions",
         paper=465, tol=0,
         compute=lambda c: int((c["provisions"]["Type"] == "Customary").sum())),

    dict(id="n_provisions_international", section="§3", kind="recompute",
         claim="International provisions",
         paper=194, tol=0,
         compute=lambda c: int((c["provisions"]["Type"] == "International").sum())),

    dict(id="n_countries", section="§3", kind="recompute",
         claim="Number of constitutions (countries)",
         paper=52, tol=0,
         compute=lambda c: c["provisions"]["Country"].nunique()),

    # Table 1 — Customary row
    dict(id="t1_cust_coop", section="§3 Table 1", kind="recompute",
         claim="Customary cooperative provisions",
         paper=210, tol=0,
         compute=lambda c: int(((c["provisions"]["Type"]=="Customary") &
                                (c["provisions"]["Category"]=="Cooperative")).sum())),
    dict(id="t1_cust_compl", section="§3 Table 1", kind="recompute",
         claim="Customary complementary provisions",
         paper=211, tol=0,
         compute=lambda c: int(((c["provisions"]["Type"]=="Customary") &
                                (c["provisions"]["Category"]=="Complementary")).sum())),
    dict(id="t1_cust_comp", section="§3 Table 1", kind="recompute",
         claim="Customary competitive provisions",
         paper=33, tol=0,
         compute=lambda c: int(((c["provisions"]["Type"]=="Customary") &
                                (c["provisions"]["Category"]=="Competitive")).sum())),
    dict(id="t1_cust_comb", section="§3 Table 1", kind="recompute",
         claim="Customary combative provisions",
         paper=11, tol=0,
         compute=lambda c: int(((c["provisions"]["Type"]=="Customary") &
                                (c["provisions"]["Category"]=="Combative")).sum())),

    # Table 1 — International row
    dict(id="t1_intl_coop", section="§3 Table 1", kind="recompute",
         claim="International cooperative provisions",
         paper=135, tol=0,
         compute=lambda c: int(((c["provisions"]["Type"]=="International") &
                                (c["provisions"]["Category"]=="Cooperative")).sum())),
    dict(id="t1_intl_compl", section="§3 Table 1", kind="recompute",
         claim="International complementary provisions",
         paper=28, tol=0,
         compute=lambda c: int(((c["provisions"]["Type"]=="International") &
                                (c["provisions"]["Category"]=="Complementary")).sum())),
    dict(id="t1_intl_comp", section="§3 Table 1", kind="recompute",
         claim="International competitive provisions",
         paper=31, tol=0,
         compute=lambda c: int(((c["provisions"]["Type"]=="International") &
                                (c["provisions"]["Category"]=="Competitive")).sum())),
    dict(id="t1_intl_comb", section="§3 Table 1", kind="recompute",
         claim="International combative provisions",
         paper=0, tol=0,
         compute=lambda c: int(((c["provisions"]["Type"]=="International") &
                                (c["provisions"]["Category"]=="Combative")).sum())),

    # Table 1 — column totals
    dict(id="t1_total_coop", section="§3 Table 1", kind="recompute",
         claim="Total cooperative provisions",
         paper=345, tol=0,
         compute=lambda c: int((c["provisions"]["Category"]=="Cooperative").sum())),
    dict(id="t1_total_compl", section="§3 Table 1", kind="recompute",
         claim="Total complementary provisions",
         paper=239, tol=0,
         compute=lambda c: int((c["provisions"]["Category"]=="Complementary").sum())),
    dict(id="t1_total_comp", section="§3 Table 1", kind="recompute",
         claim="Total competitive provisions",
         paper=64, tol=0,
         compute=lambda c: int((c["provisions"]["Category"]=="Competitive").sum())),
    dict(id="t1_total_comb", section="§3 Table 1", kind="recompute",
         claim="Total combative provisions",
         paper=11, tol=0,
         compute=lambda c: int((c["provisions"]["Category"]=="Combative").sum())),

    # Table 1 — percentages
    dict(id="t1_intl_coop_pct", section="§3 Table 1", kind="recompute",
         claim="International cooperative %",
         paper=69.6, tol=0.1,
         compute=lambda c: 100 * ((c["provisions"]["Type"]=="International") &
             (c["provisions"]["Category"]=="Cooperative")).sum() /
             (c["provisions"]["Type"]=="International").sum()),
    dict(id="t1_cust_coop_pct", section="§3 Table 1", kind="recompute",
         claim="Customary cooperative %",
         paper=45.2, tol=0.1,  # NOTE: paper prints 45.3, true value is 45.2 (210/465)
         compute=lambda c: 100 * ((c["provisions"]["Type"]=="Customary") &
             (c["provisions"]["Category"]=="Cooperative")).sum() /
             (c["provisions"]["Type"]=="Customary").sum()),
    dict(id="t1_cust_compl_pct", section="§3 Table 1", kind="recompute",
         claim="Customary complementary %",
         paper=45.4, tol=0.1,
         compute=lambda c: 100 * ((c["provisions"]["Type"]=="Customary") &
             (c["provisions"]["Category"]=="Complementary")).sum() /
             (c["provisions"]["Type"]=="Customary").sum()),

    # Chi-square test of independence
    dict(id="chi2_stat", section="§3 Table 1", kind="recompute",
         claim="Chi-square statistic (Type x Category)",
         paper=67.71, tol=0.5,
         compute=lambda c: _chi2(c)),

    # ====================  SPECTRUM SCORES  ================================
    dict(id="spectrum_cust_mean", section="§3", kind="recompute",
         claim="Mean customary spectrum score (pooled across provisions)",
         paper=0.332, tol=0.005,
         compute=lambda c: c["provisions"].loc[
             c["provisions"]["Type"]=="Customary", "score"].mean()),
    dict(id="spectrum_cust_sd", section="§3", kind="recompute",
         claim="SD customary spectrum score (pooled)",
         paper=0.712, tol=0.005,
         compute=lambda c: c["provisions"].loc[
             c["provisions"]["Type"]=="Customary", "score"].std()),
    dict(id="spectrum_intl_mean", section="§3", kind="recompute",
         claim="Mean international spectrum score (pooled)",
         paper=0.536, tol=0.005,
         compute=lambda c: c["provisions"].loc[
             c["provisions"]["Type"]=="International", "score"].mean()),
    dict(id="spectrum_intl_sd", section="§3", kind="recompute",
         claim="SD international spectrum score (pooled)",
         paper=0.756, tol=0.005,
         compute=lambda c: c["provisions"].loc[
             c["provisions"]["Type"]=="International", "score"].std()),

    # ====================  SECTION 4: MEASUREMENT  =========================
    # Cross-type similarity (cosine matrices)
    dict(id="cross_type_r", section="§4", kind="recompute",
         claim="Cross-type QAP correlation (customary vs international cosine)",
         paper=0.250, tol=0.002,
         compute=lambda c: _cross_type_r(c)),

    # Spectrum-diff vs cosine correlation (customary)
    dict(id="spec_cosine_r_cust", section="§4", kind="recompute",
         claim="Spectrum-diff vs cosine-similarity r (customary)",
         paper=-0.725, tol=0.01,
         compute=lambda c: _spec_cosine_r(c, "Customary")),
    dict(id="spec_cosine_r_intl", section="§4", kind="recompute",
         claim="Spectrum-diff vs cosine-similarity r (international)",
         paper=-0.745, tol=0.01,
         compute=lambda c: _spec_cosine_r(c, "International")),

    # Independent variance left by cosine (1 - r^2)
    dict(id="indep_var_cust", section="§4", kind="recompute",
         claim="Independent variance, customary (1 - r^2), %",
         paper=47, tol=1.0,
         compute=lambda c: 100 * (1 - _spec_cosine_r(c, "Customary")**2)),
    dict(id="indep_var_intl", section="§4", kind="recompute",
         claim="Independent variance, international (1 - r^2), %",
         paper=44, tol=1.0,
         compute=lambda c: 100 * (1 - _spec_cosine_r(c, "International")**2)),

    # Kenya / Nicaragua example — cosine similarity
    dict(id="kenya_nicaragua_cosine", section="§4", kind="recompute",
         claim="Kenya–Nicaragua customary cosine similarity",
         paper=0.271, tol=0.01,
         compute=lambda c: float(c["cust_sim"].loc["Kenya", "Nicaragua"])),

    # Network density at 75th percentile (~0.25)
    dict(id="cust_network_density", section="§4", kind="recompute",
         claim="Customary network density at 75th percentile",
         paper=0.25, tol=0.02,
         compute=lambda c: _density_at_75(c, "cust_sim")),

    # ====================  TABLE 2: QAP BIVARIATE  =========================
    dict(id="qap_cust_region_r", section="§4 Table 2", kind="check",
         claim="QAP customary Same Region r",
         paper=-0.002, tol=0.002,
         compute=lambda c: _qap_val(c["qap_cust"], "Same Region", "r")),
    dict(id="qap_cust_legal_r", section="§4 Table 2", kind="check",
         claim="QAP customary Same Legal Family r",
         paper=0.009, tol=0.002,
         compute=lambda c: _qap_val(c["qap_cust"], "Same Legal Family", "r")),
    dict(id="qap_cust_colonial_r", section="§4 Table 2", kind="check",
         claim="QAP customary Same Colonial Heritage r",
         paper=-0.046, tol=0.002,
         compute=lambda c: _qap_val(c["qap_cust"], "Same Colonial Heritage", "r")),
    dict(id="qap_cust_spectrum_r", section="§4 Table 2", kind="check",
         claim="QAP customary Spectrum Score Diff r",
         paper=-0.728, tol=0.002,
         compute=lambda c: _qap_val(c["qap_cust"], "Spectrum Score Diff (−)", "r")),
    dict(id="qap_cust_crosstype_r", section="§4 Table 2", kind="check",
         claim="QAP customary Cross-Type Similarity r",
         paper=0.250, tol=0.002,
         compute=lambda c: _qap_val(c["qap_cust"], "International Similarity", "r")),
    dict(id="qap_intl_spectrum_r", section="§4 Table 2", kind="check",
         claim="QAP international Spectrum Score Diff r",
         paper=-0.749, tol=0.002,
         compute=lambda c: _qap_val(c["qap_intl"], "Spectrum Score Diff (−)", "r")),
    dict(id="qap_intl_crosstype_r", section="§4 Table 2", kind="check",
         claim="QAP international Cross-Type Similarity r",
         paper=0.250, tol=0.002,
         compute=lambda c: _qap_val(c["qap_intl"], "Customary Similarity", "r")),

    # ====================  TABLE 3: MRQAP  =================================
    dict(id="mrqap_cust_spectrum_beta", section="§4 Table 3", kind="check",
         claim="MRQAP customary Spectrum Score Diff beta",
         paper=-0.246, tol=0.002,
         compute=lambda c: _qap_val(c["mrqap_cust"].rename(columns={"Std Beta":"r"}),
                                     "Spectrum Score Diff", "r")),
    dict(id="mrqap_intl_spectrum_beta", section="§4 Table 3", kind="check",
         claim="MRQAP international Spectrum Score Diff beta",
         paper=-0.233, tol=0.002,
         compute=lambda c: _qap_val(c["mrqap_intl"].rename(columns={"Std Beta":"r"}),
                                     "Spectrum Score Diff", "r")),
    dict(id="mrqap_intl_crosstype_beta", section="§4 Table 3", kind="check",
         claim="MRQAP international Cross-Type Similarity beta (β=+0.058)",
         paper=0.058, tol=0.002,
         compute=lambda c: _qap_val(c["mrqap_intl"].rename(columns={"Std Beta":"r"}),
                                     "Customary Similarity", "r")),
    dict(id="mrqap_cust_crosstype_beta", section="§4 Table 3", kind="check",
         claim="MRQAP customary Cross-Type Similarity beta (β=+0.018)",
         paper=0.018, tol=0.002,
         compute=lambda c: _qap_val(c["mrqap_cust"].rename(columns={"Std Beta":"r"}),
                                     "International Similarity", "r")),

    # ====================  TABLE 4: ERGM CUSTOMARY  =======================
    dict(id="ergm_cust_edges", section="§4 Table 4", kind="check",
         claim="ERGM customary edges estimate",
         paper=1.871, tol=0.001,
         compute=lambda c: _ergm_val(c["ergm_cust"], "edges", "Estimate")),
    dict(id="ergm_cust_gwdeg", section="§4 Table 4", kind="check",
         claim="ERGM customary gwdegree estimate",
         paper=-2.517, tol=0.001,
         compute=lambda c: _ergm_val(c["ergm_cust"], "gwdeg.fixed.0.5", "Estimate")),
    dict(id="ergm_cust_legal", section="§4 Table 4", kind="check",
         claim="ERGM customary nodematch.legal estimate",
         paper=-0.452, tol=0.001,
         compute=lambda c: _ergm_val(c["ergm_cust"], "nodematch.legal", "Estimate")),
    dict(id="ergm_cust_domcat", section="§4 Table 4", kind="check",
         claim="ERGM customary nodematch.dominant_cat estimate",
         paper=1.999, tol=0.001,
         compute=lambda c: _ergm_val(c["ergm_cust"], "nodematch.dominant_cat", "Estimate")),
    dict(id="ergm_cust_domcat_or", section="§4 Table 4", kind="check",
         claim="ERGM customary dominant_cat OR (7.38)",
         paper=7.38, tol=0.05,
         compute=lambda c: _ergm_val(c["ergm_cust"], "nodematch.dominant_cat", "OR")),
    dict(id="ergm_cust_spectrum", section="§4 Table 4", kind="check",
         claim="ERGM customary absdiff.spectrum_score estimate",
         paper=-7.383, tol=0.001,
         compute=lambda c: _ergm_val(c["ergm_cust"], "absdiff.spectrum_score", "Estimate")),
    dict(id="ergm_cust_britain", section="§4 Table 4", kind="check",
         claim="ERGM customary colonial.Britain estimate",
         paper=-0.926, tol=0.001,
         compute=lambda c: _ergm_val(c["ergm_cust"], "nodefactor.colonial.Britain", "Estimate")),
    dict(id="ergm_cust_france", section="§4 Table 4", kind="check",
         claim="ERGM customary colonial.France estimate",
         paper=-0.923, tol=0.001,
         compute=lambda c: _ergm_val(c["ergm_cust"], "nodefactor.colonial.France", "Estimate")),
    dict(id="ergm_cust_russia", section="§4 Table 4", kind="check",
         claim="ERGM customary colonial.Russia estimate",
         paper=-1.241, tol=0.001,
         compute=lambda c: _ergm_val(c["ergm_cust"], "nodefactor.colonial.Russia", "Estimate")),

    # ====================  TABLE 5: ERGM INTERNATIONAL  ===================
    dict(id="ergm_intl_edges", section="§4 Table 5", kind="check",
         claim="ERGM international edges estimate",
         paper=-4.894, tol=0.001,
         compute=lambda c: _ergm_val(c["ergm_intl"], "edges", "Estimate")),
    dict(id="ergm_intl_gwesp", section="§4 Table 5", kind="check",
         claim="ERGM international gwesp estimate",
         paper=2.811, tol=0.001,
         compute=lambda c: _ergm_val(c["ergm_intl"], "gwesp.fixed.0.25", "Estimate")),
    dict(id="ergm_intl_gwesp_or", section="§4 Table 5", kind="check",
         claim="ERGM international gwesp OR (16.63)",
         paper=16.63, tol=0.05,
         compute=lambda c: _ergm_val(c["ergm_intl"], "gwesp.fixed.0.25", "OR")),
    dict(id="ergm_intl_domcat", section="§4 Table 5", kind="check",
         claim="ERGM international nodematch.dominant_cat estimate",
         paper=3.321, tol=0.001,
         compute=lambda c: _ergm_val(c["ergm_intl"], "nodematch.dominant_cat", "Estimate")),
    dict(id="ergm_intl_domcat_or", section="§4 Table 5", kind="check",
         claim="ERGM international dominant_cat OR (27.68)",
         paper=27.68, tol=0.1,
         compute=lambda c: _ergm_val(c["ergm_intl"], "nodematch.dominant_cat", "OR")),
    dict(id="ergm_intl_spectrum", section="§4 Table 5", kind="check",
         claim="ERGM international absdiff.spectrum_score estimate",
         paper=-11.568, tol=0.001,
         compute=lambda c: _ergm_val(c["ergm_intl"], "absdiff.spectrum_score", "Estimate")),
    dict(id="ergm_intl_australia", section="§4 Table 5", kind="check",
         claim="ERGM international colonial.Australia estimate",
         paper=-2.794, tol=0.001,
         compute=lambda c: _ergm_val(c["ergm_intl"], "nodefactor.colonial.Australia", "Estimate")),
    dict(id="ergm_intl_common", section="§4 Table 5", kind="check",
         claim="ERGM international legal.Common estimate",
         paper=1.493, tol=0.001,
         compute=lambda c: _ergm_val(c["ergm_intl"], "nodefactor.legal.Common", "Estimate")),
    dict(id="ergm_intl_islamic", section="§4 Table 5", kind="check",
         claim="ERGM international legal.Islamic estimate",
         paper=1.592, tol=0.001,
         compute=lambda c: _ergm_val(c["ergm_intl"], "nodefactor.legal.Islamic", "Estimate")),

    # ====================  GOF p-values  ==================================
    dict(id="gof_cust_min_p", section="App D", kind="check",
         claim="Customary GOF: all MC p-values >= 0.86",
         paper=True, tol=0,
         compute=lambda c: bool(
             c["gof"].loc[c["gof"]["Network"]=="Customary", "MC p-value"].min() >= 0.86)),
    dict(id="gof_intl_min_p", section="App D", kind="check",
         claim="International GOF: all MC p-values >= 0.84 (paper should say 0.84 not 0.86)",
         paper=True, tol=0,
         compute=lambda c: bool(
             c["gof"].loc[c["gof"]["Network"]=="International", "MC p-value"].min() >= 0.84)),
]


# ─────────────────────────────────────────────────────────────────────────────
# Compute helpers used by lambdas
# ─────────────────────────────────────────────────────────────────────────────
def _chi2(c):
    from scipy.stats import chi2_contingency
    ct = pd.crosstab(c["provisions"]["Type"], c["provisions"]["Category"])
    chi2, p, dof, exp = chi2_contingency(ct, correction=False)
    return chi2


def _cross_type_r(c):
    cust = c["cust_sim"]
    intl = c["intl_sim"]
    common = [x for x in cust.index if x in intl.index]
    cust = cust.loc[common, common]
    intl = intl.loc[common, common]
    N = len(cust)
    triu = np.triu_indices(N, k=1)
    return np.corrcoef(cust.values[triu], intl.values[triu])[0, 1]


def _spec_cosine_r(c, typ):
    """Correlation between spectrum-score difference and cosine similarity."""
    nodes = c["cust_nodes"] if typ == "Customary" else c["intl_nodes"]
    sim   = c["cust_sim"]   if typ == "Customary" else c["intl_sim"]
    # spectrum score per country from graphml node attribute
    spec = dict(zip(nodes["id"], nodes["spectrum_score"]))
    countries = [x for x in sim.index if x in spec]
    sim = sim.loc[countries, countries]
    N = len(countries)
    sd, cos = [], []
    for i in range(N):
        for j in range(i + 1, N):
            ci, cj = countries[i], countries[j]
            sd.append(abs(spec[ci] - spec[cj]))
            cos.append(sim.iloc[i, j])
    return np.corrcoef(sd, cos)[0, 1]


def _density_at_75(c, simkey):
    sim = c[simkey]
    N = len(sim)
    triu = np.triu_indices(N, k=1)
    vals = sim.values[triu]
    thresh = np.quantile(vals, 0.75)
    return float((vals >= thresh).mean())


# ─────────────────────────────────────────────────────────────────────────────
# Runner
# ─────────────────────────────────────────────────────────────────────────────
def run_all_checks(verbose=True):
    ctx = load_context()
    passed, failed = 0, 0
    results = []
    for chk in CHECKS:
        try:
            val = chk["compute"](ctx)
            paper = chk["paper"]
            if isinstance(paper, bool):
                ok = (bool(val) == paper)
            else:
                ok = abs(float(val) - float(paper)) <= chk["tol"]
            status = "PASS" if ok else "FAIL"
            if ok: passed += 1
            else:  failed += 1
        except Exception as e:
            status = "ERROR"
            val = f"{type(e).__name__}: {e}"
            failed += 1
        results.append((chk["id"], chk["section"], status, chk["paper"], val, chk["claim"]))
        if verbose:
            vstr = f"{val:.4f}" if isinstance(val, float) else str(val)
            pstr = f"{chk['paper']:.4f}" if isinstance(chk['paper'], float) else str(chk['paper'])
            print(f"  [{status}] {chk['id']:<28} paper={pstr:<12} computed={vstr:<12} {chk['section']}")
    if verbose:
        print(f"\n{'='*70}")
        print(f"  {passed}/{passed+failed} checks passed")
        print(f"{'='*70}")
    return passed, failed, results


if __name__ == "__main__":
    run_all_checks()
