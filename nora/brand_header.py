"""Current app header, independent of a UI module cached before a rename."""

from __future__ import annotations

from html import escape

import streamlit as st

from .branding import __app_name__


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
      <div class="nora-eyebrow">{escape(eyebrow)}</div>
      <h1>{escape(__app_name__)}</h1>
      <p>{escape(subtitle)}</p>
    </div>
  </div>
  <div class="nora-brand-meta">
    <span class="nora-meta-chip primary">Evidence Assurance</span>
    {f'<span class="nora-meta-chip">{escape(project_name)}</span>' if project_name else ''}
    <span class="nora-meta-chip">v{escape(version)}</span>
    <span class="nora-meta-chip">{escape(ontology_version)}</span>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
