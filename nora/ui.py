"""Visual design system for the ToxiGuard NORA Streamlit application."""

from __future__ import annotations

from html import escape
from typing import Any, Iterable

import streamlit as st


ROLE_TONES: dict[int, dict[str, str]] = {
    0: {"class": "role-r0", "accent": "#64748b", "label": "R0"},
    1: {"class": "role-r1", "accent": "#6d5bd0", "label": "R1"},
    2: {"class": "role-r2", "accent": "#2673c8", "label": "R2"},
    3: {"class": "role-r3", "accent": "#0f8a82", "label": "R3"},
    4: {"class": "role-r4", "accent": "#b7791f", "label": "R4"},
    5: {"class": "role-r5", "accent": "#7a4fb7", "label": "R5"},
}


def safe(value: Any) -> str:
    """Escape dynamic values before inserting them in custom HTML."""
    return escape(str(value if value is not None else ""), quote=True)


def role_tone(role: int | str | None) -> dict[str, str]:
    try:
        value = int(str(role).replace("R", "").strip())
    except (TypeError, ValueError):
        value = 0
    return ROLE_TONES.get(value, ROLE_TONES[0])


GLOBAL_CSS = r"""
<style>
:root {
  --nora-bg:#f6f8fb;
  --nora-surface:#ffffff;
  --nora-surface-soft:#f1f5f8;
  --nora-navy:#0c2238;
  --nora-navy-2:#153a56;
  --nora-ink:#172535;
  --nora-muted:#617183;
  --nora-teal:#0f7f78;
  --nora-teal-soft:#e7f5f2;
  --nora-cyan:#2586a5;
  --nora-line:#dce5eb;
  --nora-line-strong:#c9d6df;
  --nora-red:#b14450;
  --nora-red-soft:#fff1f2;
  --nora-amber:#a86813;
  --nora-amber-soft:#fff6e6;
  --nora-green:#17734e;
  --nora-green-soft:#edf8f2;
  --nora-shadow:0 12px 36px rgba(20,45,70,.075);
  --nora-shadow-soft:0 6px 20px rgba(20,45,70,.055);
  --nora-radius-lg:20px;
  --nora-radius-md:14px;
  --nora-radius-sm:10px;
}

html, body, [class*="css"] {
  font-family: Inter, Pretendard, -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", "Noto Sans KR", "Segoe UI", sans-serif;
}

.stApp {
  color:var(--nora-ink);
  background:
    radial-gradient(circle at 85% -5%, rgba(37,134,165,.08), transparent 28%),
    linear-gradient(180deg,#f9fbfc 0%,var(--nora-bg) 38%,#f4f7fa 100%);
}

.block-container {
  max-width:1440px;
  padding-top:1rem;
  padding-bottom:5rem;
}

#MainMenu, footer, [data-testid="stToolbar"] { visibility:hidden; }
[data-testid="stHeader"] { background:transparent; }

/* Sidebar */
[data-testid="stSidebar"] {
  background:
    radial-gradient(circle at 20% 0%, rgba(42,161,158,.16), transparent 28%),
    linear-gradient(180deg,#0b2136 0%,#0d3047 60%,#0b263b 100%);
  border-right:1px solid rgba(255,255,255,.07);
}
[data-testid="stSidebar"] > div:first-child { padding-top:.65rem; }
[data-testid="stSidebar"] * { color:#edf7fb; }
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] textarea,
[data-testid="stSidebar"] [data-baseweb="select"] > div {
  color:var(--nora-ink)!important;
  background:#fff!important;
  border-radius:10px!important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] {
  border:1px solid rgba(255,255,255,.12);
  background:rgba(255,255,255,.045);
  border-radius:14px;
  overflow:hidden;
}
[data-testid="stSidebar"] [data-testid="stExpander"] summary {
  background:rgba(255,255,255,.035);
}
[data-testid="stSidebar"] .stButton > button,
[data-testid="stSidebar"] .stDownloadButton > button {
  min-height:2.5rem;
  color:#0f2c43!important;
  background:#fff!important;
  border:1px solid rgba(255,255,255,.55)!important;
  border-radius:10px!important;
  font-weight:800!important;
  box-shadow:none!important;
}
[data-testid="stSidebar"] .stButton > button:hover,
[data-testid="stSidebar"] .stDownloadButton > button:hover {
  transform:translateY(-1px);
  border-color:#8ddbd2!important;
}
[data-testid="stSidebar"] div[role="radiogroup"] { gap:.3rem; }
[data-testid="stSidebar"] div[role="radiogroup"] > label {
  min-height:2.65rem;
  padding:.45rem .6rem;
  border:1px solid transparent;
  border-radius:11px;
  background:transparent;
  transition:.16s ease;
}
[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
  background:rgba(255,255,255,.07);
  border-color:rgba(255,255,255,.1);
}
[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
  color:white;
  background:linear-gradient(90deg,rgba(40,154,151,.30),rgba(255,255,255,.08));
  border-color:rgba(105,220,207,.35);
  box-shadow:inset 3px 0 #67d6c8;
}

.nora-side-brand { margin:.1rem 0 1rem; }
.nora-side-brand-top { display:flex; align-items:center; gap:.72rem; }
.nora-side-mark {
  width:42px; height:42px; flex:0 0 42px; border-radius:13px;
  display:grid; place-items:center; position:relative; overflow:hidden;
  color:#082437; font-weight:950; letter-spacing:-.04em;
  background:linear-gradient(135deg,#6fe1d2,#d8f5ef);
  box-shadow:0 8px 24px rgba(47,194,180,.22);
}
.nora-side-mark:after {
  content:""; position:absolute; width:8px; height:8px; right:7px; top:7px;
  border-radius:50%; background:#f5c66c; box-shadow:-17px 16px 0 #39a7c2;
}
.nora-side-brand strong { display:block; color:#fff; font-size:1.02rem; line-height:1.15; }
.nora-side-brand span { display:block; color:#a9c7d4; font-size:.72rem; margin-top:.15rem; }
.nora-side-project {
  margin-top:.85rem; padding:.8rem .85rem; border:1px solid rgba(255,255,255,.10);
  border-radius:12px; background:rgba(255,255,255,.045);
}
.nora-side-project span { color:#9fc0ce; font-size:.69rem; font-weight:750; text-transform:uppercase; letter-spacing:.06em; }
.nora-side-project strong { margin-top:.18rem; color:#fff; font-size:.9rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.nora-side-section { margin:.9rem 0 .35rem; color:#8db2c2; font-size:.68rem; font-weight:850; text-transform:uppercase; letter-spacing:.1em; }
.nora-side-note { margin-top:1rem; padding:.8rem; border-radius:11px; background:rgba(1,13,24,.22); color:#9ebcc9; font-size:.7rem; line-height:1.5; }

/* Brand bar */
.nora-shell-header {
  display:flex; align-items:center; justify-content:space-between; gap:1.3rem;
  position:relative; overflow:hidden;
  min-height:112px; padding:1.2rem 1.35rem;
  border:1px solid var(--nora-line); border-radius:var(--nora-radius-lg);
  background:rgba(255,255,255,.94); box-shadow:var(--nora-shadow);
}
.nora-shell-header:after {
  content:""; position:absolute; width:230px; height:230px; right:-95px; top:-120px;
  border-radius:50%; background:radial-gradient(circle,rgba(35,142,163,.14),rgba(35,142,163,0) 69%);
}
.nora-brand-lockup { display:flex; align-items:center; gap:1rem; min-width:0; position:relative; z-index:1; }
.nora-brand-mark {
  width:58px; height:58px; flex:0 0 58px; border-radius:17px; position:relative; overflow:hidden;
  display:grid; place-items:center; color:#fff; font-size:1.2rem; font-weight:950;
  background:linear-gradient(145deg,var(--nora-navy),#185473);
  box-shadow:0 12px 28px rgba(14,50,76,.20);
}
.nora-brand-mark:before,
.nora-brand-mark:after { content:""; position:absolute; border-radius:50%; }
.nora-brand-mark:before { width:8px;height:8px;top:10px;left:11px;background:#62d4c6;box-shadow:28px 9px 0 #3a9fbd,12px 29px 0 #f2c466; }
.nora-brand-mark:after { inset:16px; border:1px solid rgba(255,255,255,.28); }
.nora-brand-copy { min-width:0; }
.nora-eyebrow { color:var(--nora-teal); font-size:.69rem; font-weight:900; letter-spacing:.11em; text-transform:uppercase; }
.nora-brand-copy h1 { margin:.18rem 0 .16rem; color:var(--nora-navy); font-size:clamp(1.55rem,2.5vw,2.15rem); line-height:1.08; letter-spacing:-.035em; }
.nora-brand-copy p { margin:0; color:var(--nora-muted); font-size:.88rem; }
.nora-brand-meta { display:flex; flex-wrap:wrap; justify-content:flex-end; gap:.4rem; position:relative; z-index:1; }
.nora-meta-chip { padding:.38rem .62rem; border:1px solid var(--nora-line); border-radius:999px; background:#f8fbfc; color:#496174; font-size:.7rem; font-weight:800; white-space:nowrap; }
.nora-meta-chip.primary { color:#0b675f; border-color:#bde3dc; background:var(--nora-teal-soft); }

.nora-language-panel {
  min-height:112px; display:flex; flex-direction:column; justify-content:center;
  padding:.9rem 1rem; border:1px solid var(--nora-line); border-radius:var(--nora-radius-lg);
  background:rgba(255,255,255,.94); box-shadow:var(--nora-shadow);
}
.nora-language-label { color:var(--nora-muted); font-size:.68rem; font-weight:900; letter-spacing:.08em; text-transform:uppercase; margin-bottom:.35rem; }
.nora-language-panel [data-testid="stRadio"] > label { display:none; }
.nora-language-panel [role="radiogroup"] {
  display:grid!important; grid-template-columns:1fr 1fr; gap:.2rem!important;
  padding:.25rem; border:1px solid var(--nora-line); border-radius:999px; background:#f2f6f8;
}
.nora-language-panel [role="radiogroup"] label {
  justify-content:center; min-height:2.15rem; margin:0!important; padding:.25rem .35rem!important;
  border-radius:999px; transition:.15s ease;
}
.nora-language-panel [role="radiogroup"] label:has(input:checked) { background:#fff; box-shadow:0 3px 12px rgba(20,45,70,.10); }

/* Streamlit column that contains the language anchor becomes the top-right control card. */
div[data-testid="stColumn"]:has(.nora-language-anchor) {
  min-height:112px; padding:.85rem .95rem; border:1px solid var(--nora-line);
  border-radius:var(--nora-radius-lg); background:rgba(255,255,255,.94); box-shadow:var(--nora-shadow);
}
.nora-language-anchor { margin:.05rem 0 .25rem; }
.nora-language-anchor span { display:block; color:var(--nora-muted); font-size:.66rem; font-weight:900; letter-spacing:.08em; text-transform:uppercase; }
.nora-language-anchor strong { display:block; margin-top:.12rem; color:var(--nora-navy); font-size:.78rem; }
div[data-testid="stColumn"]:has(.nora-language-anchor) [data-testid="stRadio"] > label { display:none; }
div[data-testid="stColumn"]:has(.nora-language-anchor) [role="radiogroup"] {
  display:grid!important; grid-template-columns:1fr 1fr; gap:.2rem!important; padding:.24rem;
  border:1px solid var(--nora-line); border-radius:999px; background:#f2f6f8;
}
div[data-testid="stColumn"]:has(.nora-language-anchor) [role="radiogroup"] label {
  justify-content:center; min-height:2rem; margin:0!important; padding:.18rem .25rem!important; border-radius:999px;
}
div[data-testid="stColumn"]:has(.nora-language-anchor) [role="radiogroup"] label:has(input:checked) { background:#fff; box-shadow:0 3px 12px rgba(20,45,70,.10); }

.nora-trust-line {
  display:flex; align-items:center; gap:.6rem; margin:.75rem 0 1rem;
  padding:.72rem .9rem; border:1px solid #cfe5e1; border-radius:12px;
  background:linear-gradient(90deg,#f2fbf9,#fff); color:#3b5964; font-size:.8rem;
}
.nora-trust-line:before { content:""; width:8px;height:8px;border-radius:50%;background:#32aa9c;box-shadow:0 0 0 5px rgba(50,170,156,.10); }
.nora-trust-line strong { color:#0d5f59; }

/* Page hierarchy */
.nora-page-header { margin:.2rem 0 1rem; padding:.2rem 0 .4rem; }
.nora-page-kicker { color:var(--nora-teal); font-size:.7rem; font-weight:900; text-transform:uppercase; letter-spacing:.1em; }
.nora-page-header h2 { margin:.2rem 0 .25rem; color:var(--nora-navy); font-size:clamp(1.45rem,2.4vw,2rem); letter-spacing:-.025em; }
.nora-page-header p { margin:0; max-width:900px; color:var(--nora-muted); font-size:.9rem; }

/* KPI strip */
.nora-status-strip { display:grid; grid-template-columns:1.25fr repeat(4,minmax(0,1fr)); gap:.65rem; margin:.65rem 0 .85rem; }
.nora-status-card {
  min-width:0; min-height:84px; padding:.85rem .9rem; position:relative; overflow:hidden;
  border:1px solid var(--nora-line); border-radius:14px; background:rgba(255,255,255,.94); box-shadow:var(--nora-shadow-soft);
}
.nora-status-card:before { content:""; position:absolute; left:0; top:0; bottom:0; width:3px; background:#c6d6df; }
.nora-status-card.accent-teal:before { background:#23a697; }
.nora-status-card.accent-blue:before { background:#3282b3; }
.nora-status-card.accent-amber:before { background:#d49a38; }
.nora-status-label { color:var(--nora-muted); font-size:.68rem; font-weight:850; text-transform:uppercase; letter-spacing:.055em; }
.nora-status-value { display:block; margin-top:.28rem; color:var(--nora-navy); font-size:1.02rem; font-weight:900; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.nora-status-sub { display:block; margin-top:.16rem; color:#81909d; font-size:.66rem; }
.nora-role-pill { display:inline-flex; align-items:center; gap:.3rem; margin-top:.28rem; padding:.3rem .55rem; border-radius:999px; font-weight:900; font-size:.78rem; }
.role-r0 .nora-role-pill,.nora-role-pill.role-r0 { color:#475569;background:#eef2f5; }
.role-r1 .nora-role-pill,.nora-role-pill.role-r1 { color:#5542ad;background:#efedff; }
.role-r2 .nora-role-pill,.nora-role-pill.role-r2 { color:#1e5d9e;background:#e9f2ff; }
.role-r3 .nora-role-pill,.nora-role-pill.role-r3 { color:#096e67;background:#e5f7f4; }
.role-r4 .nora-role-pill,.nora-role-pill.role-r4 { color:#8b560d;background:#fff2d9; }
.role-r5 .nora-role-pill,.nora-role-pill.role-r5 { color:#68409b;background:#f3eaff; }

/* Workspace progress */
.nora-workflow { display:grid; grid-template-columns:repeat(6,minmax(0,1fr)); gap:.45rem; margin:0 0 1.15rem; }
.nora-flow-step {
  position:relative; min-height:67px; padding:.62rem .58rem .58rem 2.35rem;
  border:1px solid var(--nora-line); border-radius:12px; background:rgba(255,255,255,.88); color:#5d6f7f;
}
.nora-flow-step .nora-flow-num {
  position:absolute; left:.63rem; top:.62rem; width:1.35rem; height:1.35rem; display:grid; place-items:center;
  border-radius:50%; background:#e8eef2; color:#627383; font-size:.64rem; font-weight:900;
}
.nora-flow-step strong { display:block; color:#2d4659; font-size:.75rem; }
.nora-flow-step span { display:block; margin-top:.15rem; font-size:.64rem; line-height:1.25; }
.nora-flow-step.complete { border-color:#c7e2dd; background:#f6fbfa; }
.nora-flow-step.complete .nora-flow-num { color:#fff; background:#5aa99f; }
.nora-flow-step.active { border-color:#6abcb2; background:#eefaf8; box-shadow:0 6px 20px rgba(19,138,130,.10); }
.nora-flow-step.active .nora-flow-num { color:#fff; background:var(--nora-teal); box-shadow:0 0 0 4px rgba(15,127,120,.10); }
.nora-flow-step.active strong { color:#0b625c; }

/* Cards */
.nora-panel,
.nora-decision-card,
.nora-context-card,
.nora-task-card,
.nora-role-ladder,
.nora-recommendation-card {
  border:1px solid var(--nora-line); border-radius:var(--nora-radius-md); background:rgba(255,255,255,.96); box-shadow:var(--nora-shadow-soft);
}
.nora-decision-card { padding:1.1rem 1.15rem; }
.nora-card-label { color:var(--nora-teal); font-size:.68rem; font-weight:900; text-transform:uppercase; letter-spacing:.08em; }
.nora-decision-card h3 { margin:.36rem 0 .7rem; color:var(--nora-navy); font-size:1.15rem; line-height:1.45; }
.nora-tag-row { display:flex; flex-wrap:wrap; gap:.36rem; }
.nora-tag { padding:.34rem .55rem; border:1px solid var(--nora-line); border-radius:999px; background:#f8fafb; color:#536678; font-size:.68rem; font-weight:750; }
.nora-context-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:.55rem; margin-top:.65rem; }
.nora-context-card { padding:.78rem .85rem; }
.nora-context-card span { color:var(--nora-muted); font-size:.65rem; font-weight:850; text-transform:uppercase; letter-spacing:.05em; }
.nora-context-card strong { display:block; margin-top:.22rem; color:var(--nora-navy); font-size:.87rem; line-height:1.35; }
.nora-context-card small { display:block; margin-top:.18rem; color:#81909d; font-size:.66rem; }

.nora-role-ladder { padding:.9rem; }
.nora-role-ladder-head { display:flex; align-items:center; justify-content:space-between; margin-bottom:.55rem; }
.nora-role-ladder-head strong { color:var(--nora-navy); font-size:.9rem; }
.nora-role-ladder-head span { color:var(--nora-muted); font-size:.65rem; }
.nora-role-row { display:grid; grid-template-columns:2.55rem 1fr; gap:.55rem; align-items:center; padding:.48rem .5rem; border-radius:9px; }
.nora-role-row + .nora-role-row { margin-top:.22rem; }
.nora-role-row.active { background:#eff8f6; box-shadow:inset 3px 0 #168b82; }
.nora-role-code-mini { display:grid; place-items:center; height:1.85rem; border-radius:8px; font-size:.68rem; font-weight:950; }
.nora-role-copy strong { display:block; color:#31485a; font-size:.76rem; }
.nora-role-copy span { display:block; color:#798895; font-size:.63rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.role-r0 .nora-role-code-mini {color:#475569;background:#edf1f4}.role-r1 .nora-role-code-mini{color:#5844ad;background:#efedff}.role-r2 .nora-role-code-mini{color:#1e5d9e;background:#e9f2ff}.role-r3 .nora-role-code-mini{color:#086d66;background:#e5f7f4}.role-r4 .nora-role-code-mini{color:#8a570e;background:#fff1d8}.role-r5 .nora-role-code-mini{color:#67409b;background:#f2eaff}

.nora-task-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:.65rem; margin:.6rem 0 .7rem; }
.nora-task-card { min-height:112px; padding:.85rem .9rem; }
.nora-task-index { color:var(--nora-teal); font-size:.65rem; font-weight:950; letter-spacing:.08em; }
.nora-task-card strong { display:block; margin:.25rem 0 .22rem; color:var(--nora-navy); font-size:.86rem; }
.nora-task-card span { color:var(--nora-muted); font-size:.68rem; line-height:1.4; }

/* Result cards */
.nora-result-card { min-height:245px; padding:1.35rem; border-radius:18px; color:#fff; position:relative; overflow:hidden; box-shadow:0 16px 36px rgba(19,47,71,.16); }
.nora-result-card:after { content:""; position:absolute; width:210px;height:210px;right:-90px;top:-100px;border-radius:50%;background:rgba(255,255,255,.09); }
.nora-result-card.role-r0{background:linear-gradient(135deg,#526373,#758493)}.nora-result-card.role-r1{background:linear-gradient(135deg,#514292,#7966c6)}.nora-result-card.role-r2{background:linear-gradient(135deg,#225b92,#3e86c8)}.nora-result-card.role-r3{background:linear-gradient(135deg,#0b655f,#18a195)}.nora-result-card.role-r4{background:linear-gradient(135deg,#86520c,#c58a2d)}.nora-result-card.role-r5{background:linear-gradient(135deg,#5c398b,#8d61bd)}
.nora-result-label { color:rgba(255,255,255,.72); font-size:.68rem; font-weight:900; text-transform:uppercase; letter-spacing:.08em; }
.nora-result-code { margin:.55rem 0 0; font-size:3.35rem; line-height:1; font-weight:950; }
.nora-result-name { margin:.22rem 0 .48rem; font-size:1.4rem; font-weight:900; }
.nora-result-desc { max-width:680px; color:rgba(255,255,255,.84); font-size:.82rem; line-height:1.5; }

.nora-recommendation-card { min-height:245px; padding:1.1rem; }
.nora-recommendation-card h3 { margin:0 0 .6rem; color:var(--nora-navy); font-size:1rem; }
.nora-advisory-status { padding:.62rem .72rem; border-radius:10px; font-size:.8rem; font-weight:850; }
.nora-advisory-status.low { color:#85404a;background:var(--nora-red-soft);border:1px solid #f0cbd0; }
.nora-advisory-status.mid { color:#87570d;background:var(--nora-amber-soft);border:1px solid #efd8ad; }
.nora-advisory-status.high { color:#0a665e;background:var(--nora-teal-soft);border:1px solid #bee3dc; }
.nora-recommendation-card p { color:var(--nora-muted); font-size:.76rem; line-height:1.5; }
.nora-mini-metrics { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:.4rem; margin-top:.7rem; }
.nora-mini-metric { padding:.62rem; border:1px solid var(--nora-line); border-radius:10px; background:#f9fbfc; }
.nora-mini-metric span { color:var(--nora-muted); font-size:.61rem; font-weight:800; }
.nora-mini-metric strong { display:block; margin-top:.15rem; color:var(--nora-navy); font-size:.8rem; }

.nora-score-card { min-height:118px; padding:.85rem; border:1px solid var(--nora-line); border-radius:13px; background:#fff; box-shadow:var(--nora-shadow-soft); }
.nora-score-card span { color:var(--nora-muted); font-size:.67rem; font-weight:800; }
.nora-score-card strong { display:block; margin:.35rem 0 .45rem; color:var(--nora-navy); font-size:1.35rem; }
.nora-score-track { height:7px; overflow:hidden; border-radius:999px; background:#eaf0f3; }
.nora-score-track i { display:block; height:100%; border-radius:999px; background:linear-gradient(90deg,#1a8d83,#3b92b0); }

.nora-footer-notice { margin-top:1.4rem; padding:.78rem .9rem; border:1px solid var(--nora-line); border-radius:12px; background:#f9fbfc; color:#6e7d8b; font-size:.68rem; line-height:1.5; }

/* Streamlit components */
.stButton > button, .stDownloadButton > button {
  min-height:2.65rem; border-radius:10px!important; border:1px solid var(--nora-line-strong)!important;
  color:var(--nora-navy)!important; background:#fff!important; font-weight:800!important;
  box-shadow:none!important; transition:.16s ease!important;
}
.stButton > button:hover, .stDownloadButton > button:hover { transform:translateY(-1px); border-color:#5fb6ac!important; box-shadow:0 7px 20px rgba(20,45,70,.08)!important; }
.stButton > button[kind="primary"] { color:#fff!important; border-color:var(--nora-teal)!important; background:linear-gradient(135deg,#0e736d,#15968c)!important; }
[data-testid="stFileUploader"] { padding:.55rem; border:1px dashed #b8cbd6; border-radius:14px; background:#fbfdfe; }
[data-testid="stMetric"] { padding:.78rem .85rem; border:1px solid var(--nora-line); border-radius:12px; background:#fff; box-shadow:var(--nora-shadow-soft); }
[data-testid="stDataFrame"] { border:1px solid var(--nora-line); border-radius:13px; overflow:hidden; background:#fff; }
[data-testid="stAlert"] { border-radius:12px; }
[data-testid="stTabs"] [role="tablist"] { gap:.25rem; border-bottom:1px solid var(--nora-line); }
[data-testid="stTabs"] button[role="tab"] { padding:.55rem .75rem; border-radius:9px 9px 0 0; font-weight:780; }
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] { color:var(--nora-teal); background:#eff8f6; }
[data-testid="stForm"] { padding:1rem; border:1px solid var(--nora-line); border-radius:15px; background:rgba(255,255,255,.92); }
hr { border-color:var(--nora-line)!important; }
h1,h2,h3,h4 { color:var(--nora-navy); }

@media(max-width:1100px){
  .nora-status-strip{grid-template-columns:repeat(2,minmax(0,1fr))}.nora-status-card:first-child{grid-column:1/-1}
  .nora-workflow{grid-template-columns:repeat(3,minmax(0,1fr))}
  .nora-task-grid{grid-template-columns:1fr}
}
@media(max-width:760px){
  .block-container{padding-left:.8rem;padding-right:.8rem}.nora-shell-header{min-height:auto;padding:1rem}.nora-brand-meta{display:none}
  .nora-language-panel{min-height:auto}.nora-status-strip{grid-template-columns:1fr}.nora-status-card:first-child{grid-column:auto}
  .nora-workflow{grid-template-columns:1fr 1fr}.nora-context-grid{grid-template-columns:1fr}.nora-mini-metrics{grid-template-columns:1fr}
}

/* v0.7 readability and advisory-workspace refinement */
html { font-size:16px; }
body, .stApp { line-height:1.58; }
.block-container { max-width:1320px; padding-top:1.15rem; padding-left:1.25rem; padding-right:1.25rem; }
p, li, [data-testid="stMarkdownContainer"] { line-height:1.58; }
[data-testid="stSidebar"] { min-width:292px; max-width:292px; }
[data-testid="stSidebar"] > div:first-child { padding-left:1rem; padding-right:1rem; }
[data-testid="stSidebar"] div[role="radiogroup"] > label { min-height:2.8rem; font-size:.82rem; }
.nora-side-brand span { font-size:.76rem; }
.nora-side-project { padding:.85rem .9rem; }
.nora-side-project span { font-size:.72rem; }
.nora-side-project strong { font-size:.94rem; }
.nora-side-section { margin:1rem 0 .45rem; font-size:.71rem; }
.nora-side-note { font-size:.74rem; line-height:1.55; }
.nora-shell-header { min-height:104px; padding:1.15rem 1.3rem; }
.nora-brand-copy p { max-width:720px; font-size:.94rem; line-height:1.45; }
.nora-meta-chip { font-size:.73rem; }
div[data-testid="stColumn"]:has(.nora-language-anchor) { min-height:104px; }
.nora-language-anchor span { font-size:.7rem; }
.nora-language-anchor strong { font-size:.82rem; }
.nora-trust-line { align-items:flex-start; padding:.8rem 1rem; font-size:.86rem; line-height:1.48; }
.nora-trust-line strong { flex:0 0 auto; }
.nora-page-header { margin:.35rem 0 1.15rem; }
.nora-page-kicker { font-size:.74rem; }
.nora-page-header h2 { margin:.24rem 0 .35rem; font-size:clamp(1.55rem,2.4vw,2.08rem); }
.nora-page-header p { max-width:820px; font-size:.98rem; line-height:1.52; }
.nora-status-strip { grid-template-columns:repeat(4,minmax(0,1fr)); gap:.75rem; margin:.75rem 0 1rem; }
.nora-status-card { min-height:94px; padding:1rem; }
.nora-status-label { font-size:.73rem; }
.nora-status-value { margin-top:.34rem; font-size:1.12rem; }
.nora-status-sub { margin-top:.22rem; font-size:.73rem; line-height:1.35; }
.nora-role-pill { font-size:.84rem; }
.nora-workflow { gap:.55rem; margin:0 0 1.25rem; }
.nora-flow-step { min-height:76px; padding:.72rem .65rem .65rem 2.5rem; }
.nora-flow-step .nora-flow-num { left:.72rem; top:.72rem; width:1.45rem; height:1.45rem; font-size:.69rem; }
.nora-flow-step strong { font-size:.8rem; }
.nora-flow-step span { margin-top:.18rem; font-size:.7rem; line-height:1.35; }
.nora-decision-card { padding:1.25rem 1.3rem; }
.nora-card-label { font-size:.72rem; }
.nora-decision-card h3 { margin:.42rem 0 .8rem; font-size:1.27rem; line-height:1.48; }
.nora-tag { padding:.37rem .62rem; font-size:.74rem; }
.nora-context-grid { gap:.7rem; margin-top:.75rem; }
.nora-context-card { padding:.95rem 1rem; min-height:102px; }
.nora-context-card span { font-size:.7rem; }
.nora-context-card strong { margin-top:.28rem; font-size:.98rem; }
.nora-context-card small { font-size:.74rem; line-height:1.35; }
.nora-role-ladder { padding:1rem; }
.nora-role-ladder-head strong { font-size:1rem; }
.nora-role-ladder-head span { font-size:.72rem; }
.nora-role-row { grid-template-columns:2.8rem 1fr; padding:.56rem .58rem; }
.nora-role-code-mini { height:2rem; font-size:.73rem; }
.nora-role-copy strong { font-size:.84rem; }
.nora-role-copy span { font-size:.72rem; white-space:normal; overflow:visible; line-height:1.35; }
.nora-task-grid { grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:.75rem; }
.nora-task-card { min-height:132px; padding:1rem; }
.nora-task-index { font-size:.7rem; }
.nora-task-card strong { margin:.32rem 0 .3rem; font-size:.95rem; }
.nora-task-card span { font-size:.78rem; line-height:1.5; }
.nora-result-card { min-height:260px; padding:1.45rem; }
.nora-result-label { font-size:.73rem; }
.nora-result-name { font-size:1.5rem; }
.nora-result-desc { font-size:.94rem; line-height:1.58; }
.nora-recommendation-card { min-height:260px; padding:1.25rem; }
.nora-recommendation-card h3 { font-size:1.08rem; }
.nora-advisory-status { font-size:.88rem; }
.nora-recommendation-card p { font-size:.84rem; line-height:1.58; }
.nora-mini-metric span { font-size:.68rem; }
.nora-mini-metric strong { font-size:.88rem; }
.nora-score-card { min-height:126px; padding:1rem; }
.nora-score-card span { font-size:.74rem; }
.nora-score-card strong { font-size:1.45rem; }
.nora-footer-notice { font-size:.75rem; }
[data-testid="stForm"] { padding:1.15rem; }
[data-testid="stWidgetLabel"] p, label p { font-size:.86rem!important; line-height:1.35!important; }
[data-testid="stCaptionContainer"] p, .stCaptionContainer p { font-size:.78rem!important; line-height:1.5!important; }
[data-baseweb="input"] input, [data-baseweb="textarea"] textarea, [data-baseweb="select"] { font-size:.88rem!important; }
[data-testid="stTabs"] button[role="tab"] { padding:.68rem .9rem; font-size:.84rem; }
[data-testid="stMetricLabel"] p { font-size:.78rem!important; }
[data-testid="stMetricValue"] { font-size:1.65rem!important; }
[data-testid="stDataFrame"] { font-size:.82rem; }
.stButton > button, .stDownloadButton > button { min-height:2.8rem; font-size:.84rem; }

.nora-section-band { display:flex; justify-content:space-between; gap:1rem; align-items:flex-start; margin:.2rem 0 .8rem; padding:.95rem 1rem; border:1px solid var(--nora-line); border-left:4px solid var(--nora-teal); border-radius:12px; background:#fff; }
.nora-section-band strong { display:block; color:var(--nora-navy); font-size:.94rem; }
.nora-section-band span { display:block; margin-top:.2rem; color:var(--nora-muted); font-size:.78rem; line-height:1.48; }
.nora-section-band .nora-section-chip { flex:0 0 auto; padding:.34rem .58rem; border-radius:999px; color:#0a665f; background:var(--nora-teal-soft); font-size:.7rem; font-weight:850; }
.nora-next-action { display:grid; grid-template-columns:auto 1fr; gap:.85rem; align-items:start; margin:.8rem 0 1rem; padding:1rem 1.05rem; border:1px solid #c8e2dd; border-radius:14px; background:linear-gradient(135deg,#effaf8,#fff); box-shadow:var(--nora-shadow-soft); }
.nora-next-action-icon { width:2.25rem; height:2.25rem; display:grid; place-items:center; border-radius:11px; color:#fff; background:linear-gradient(135deg,#0f7f78,#2f9cae); font-weight:950; }
.nora-next-action span { display:block; color:var(--nora-teal); font-size:.7rem; font-weight:900; text-transform:uppercase; letter-spacing:.07em; }
.nora-next-action strong { display:block; margin:.16rem 0 .18rem; color:var(--nora-navy); font-size:1rem; }
.nora-next-action p { margin:0; color:var(--nora-muted); font-size:.8rem; }
.nora-advisory-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:.8rem; margin:.7rem 0 1rem; }
.nora-advisory-grid-three { grid-template-columns:repeat(3,minmax(0,1fr)); }
.nora-advisory-card { min-height:160px; padding:1rem 1.05rem; border:1px solid var(--nora-line); border-radius:14px; background:#fff; box-shadow:var(--nora-shadow-soft); }
.nora-advisory-card .eyebrow { color:var(--nora-teal); font-size:.7rem; font-weight:900; text-transform:uppercase; letter-spacing:.07em; }
.nora-advisory-card h3 { margin:.28rem 0 .42rem; font-size:1rem; line-height:1.4; }
.nora-advisory-card p { margin:0; color:var(--nora-muted); font-size:.8rem; }
.nora-advisory-card ul { margin:.55rem 0 0; padding-left:1.15rem; color:#42566a; font-size:.78rem; }
.nora-case-hero { padding:1.15rem 1.2rem; border:1px solid var(--nora-line); border-radius:16px; background:linear-gradient(135deg,#fff,#f3faf9); box-shadow:var(--nora-shadow-soft); }
.nora-case-hero-top { display:flex; justify-content:space-between; gap:1rem; align-items:flex-start; }
.nora-case-id { color:var(--nora-teal); font-size:.72rem; font-weight:950; letter-spacing:.08em; }
.nora-case-hero h3 { margin:.25rem 0 .36rem; font-size:1.25rem; line-height:1.35; }
.nora-case-meta { display:flex; flex-wrap:wrap; gap:.38rem; margin:.55rem 0 .75rem; }
.nora-case-meta span { padding:.34rem .58rem; border:1px solid var(--nora-line); border-radius:999px; background:#fff; color:#526779; font-size:.72rem; font-weight:750; }
.nora-case-question { margin-top:.75rem; padding:.8rem .9rem; border-left:4px solid var(--nora-cyan); border-radius:0 10px 10px 0; background:#f3f8fb; color:#29485d; font-size:.88rem; line-height:1.55; }
.nora-case-scope { padding:.4rem .62rem; border-radius:999px; background:var(--nora-amber-soft); color:#87570d; font-size:.72rem; font-weight:850; }
.nora-compact-note { margin:.65rem 0; padding:.75rem .85rem; border:1px solid var(--nora-line); border-radius:11px; background:#f9fbfc; color:var(--nora-muted); font-size:.78rem; line-height:1.5; }

@media(max-width:1100px){
  [data-testid="stSidebar"]{min-width:270px;max-width:270px}
  .nora-status-strip{grid-template-columns:repeat(2,minmax(0,1fr))}
  .nora-advisory-grid,.nora-advisory-grid-three{grid-template-columns:1fr}
}
@media(max-width:760px){
  html{font-size:15px}
  [data-testid="stSidebar"]{min-width:inherit;max-width:inherit}
  .block-container{padding-left:.75rem;padding-right:.75rem}
  .nora-status-strip{grid-template-columns:1fr 1fr}
  .nora-workflow{grid-template-columns:1fr 1fr}
  .nora-case-hero-top{display:block}
  .nora-case-scope{display:inline-block;margin-top:.5rem}
}

</style>
"""


def inject_design_system() -> None:
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def render_brand_header(
    *,
    subtitle: str,
    version: str,
    ontology_version: str,
    rule_version: str,
    eyebrow: str = "Nonclinical evidence assurance",
    project_name: str = "",
) -> None:
    st.markdown(
        f"""
<div class="nora-shell-header">
  <div class="nora-brand-lockup">
    <div class="nora-brand-mark">N</div>
    <div class="nora-brand-copy">
      <div class="nora-eyebrow">{safe(eyebrow)}</div>
      <h1>ToxiGuard NORA EarlyTox</h1>
      <p>{safe(subtitle)}</p>
    </div>
  </div>
  <div class="nora-brand-meta">
    <span class="nora-meta-chip primary">Evidence Assurance</span>
    {f'<span class="nora-meta-chip">{safe(project_name)}</span>' if project_name else ''}
    <span class="nora-meta-chip">v{safe(version)}</span>
    <span class="nora-meta-chip">{safe(ontology_version)}</span>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_page_header(kicker: str, title: str, description: str) -> None:
    st.markdown(
        f"""
<div class="nora-page-header">
  <div class="nora-page-kicker">{safe(kicker)}</div>
  <h2>{safe(title)}</h2>
  <p>{safe(description)}</p>
</div>
""",
        unsafe_allow_html=True,
    )


def render_status_strip(items: Iterable[dict[str, str]], role: int | None = None) -> None:
    tone = role_tone(role)
    cards: list[str] = []
    for index, item in enumerate(items):
        accent = item.get("accent", "")
        cls = f"nora-status-card {accent}".strip()
        value = item.get("value", "")
        if item.get("role") == "true":
            value_html = f'<span class="nora-role-pill {tone["class"]}">{safe(value)}</span>'
        else:
            value_html = f'<span class="nora-status-value">{safe(value)}</span>'
        cards.append(
            f'<div class="{cls}"><span class="nora-status-label">{safe(item.get("label", ""))}</span>{value_html}'
            f'<span class="nora-status-sub">{safe(item.get("sub", ""))}</span></div>'
        )
    st.markdown(f'<div class="nora-status-strip">{"".join(cards)}</div>', unsafe_allow_html=True)


def render_pipeline(steps: list[tuple[str, str]], active_index: int) -> None:
    parts: list[str] = []
    for index, (title, body) in enumerate(steps):
        state = "complete" if index < active_index else "active" if index == active_index else "upcoming"
        parts.append(
            f'<div class="nora-flow-step {state}"><span class="nora-flow-num">{index + 1}</span>'
            f'<strong>{safe(title)}</strong><span>{safe(body)}</span></div>'
        )
    st.markdown(f'<div class="nora-workflow">{"".join(parts)}</div>', unsafe_allow_html=True)


def render_role_ladder(role_rows: Iterable[tuple[str, str, str]], current_role: int | None = None, heading: str = "Evidence Role") -> None:
    rows: list[str] = []
    for index, (code, title, description) in enumerate(role_rows):
        tone = role_tone(index)
        active = " active" if current_role == index else ""
        rows.append(
            f'<div class="nora-role-row {tone["class"]}{active}">'
            f'<div class="nora-role-code-mini">{safe(code)}</div>'
            f'<div class="nora-role-copy"><strong>{safe(title)}</strong><span>{safe(description)}</span></div></div>'
        )
    st.markdown(
        f'<div class="nora-role-ladder"><div class="nora-role-ladder-head"><strong>{safe(heading)}</strong>'
        f'<span>R0 → R5</span></div>{"".join(rows)}</div>',
        unsafe_allow_html=True,
    )



def render_section_band(title: str, description: str, chip: str = "") -> None:
    chip_html = f'<span class="nora-section-chip">{safe(chip)}</span>' if chip else ""
    st.markdown(
        f'<div class="nora-section-band"><div><strong>{safe(title)}</strong><span>{safe(description)}</span></div>{chip_html}</div>',
        unsafe_allow_html=True,
    )


def render_next_action(title: str, description: str, label: str = "Next best action") -> None:
    st.markdown(
        f'<div class="nora-next-action"><div class="nora-next-action-icon">→</div><div>'
        f'<span>{safe(label)}</span><strong>{safe(title)}</strong><p>{safe(description)}</p></div></div>',
        unsafe_allow_html=True,
    )


def render_advisory_card(eyebrow: str, title: str, body: str, bullets: Iterable[str] = ()) -> str:
    bullet_html = "".join(f'<li>{safe(item)}</li>' for item in bullets)
    list_html = f'<ul>{bullet_html}</ul>' if bullet_html else ""
    return (
        f'<div class="nora-advisory-card"><div class="eyebrow">{safe(eyebrow)}</div>'
        f'<h3>{safe(title)}</h3><p>{safe(body)}</p>{list_html}</div>'
    )


def render_consulting_case_card(
    *,
    case_id: str,
    title: str,
    segment: str,
    objective: str,
    engagement: str,
    decision_question: str,
    automation_scope: str,
) -> None:
    html = (
        '<div class="nora-case-hero">'
        '<div class="nora-case-hero-top">'
        f'<div><div class="nora-case-id">{safe(case_id)}</div><h3>{safe(title)}</h3></div>'
        f'<span class="nora-case-scope">{safe(automation_scope)}</span>'
        '</div>'
        f'<div class="nora-case-meta"><span>{safe(segment)}</span><span>{safe(objective)}</span><span>{safe(engagement)}</span></div>'
        f'<div class="nora-case-question">{safe(decision_question)}</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)

def render_footer_notice(text: str) -> None:
    st.markdown(f'<div class="nora-footer-notice">{safe(text)}</div>', unsafe_allow_html=True)
