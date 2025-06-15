
# Streamlit API Reference – Jupyter & Script Edition

[![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io)

This repository provides a comprehensive **Streamlit API reference notebook** that is suitable for both **Jupyter environments (via [streamlit_jupyter](https://github.com/ddobrinskiy/streamlit-jupyter))** and standard `.py` Streamlit scripts.

---

## Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [What's Inside](#whats-inside)
4. [Section-by-Section Guide](#section-by-section-guide)
5. [Jupyter vs Script Support](#jupyter-vs-script-support)
6. [References & Further Reading](#references--further-reading)

---

## Overview

This notebook demonstrates:
- **Streamlit usage in Jupyter notebooks** (with `streamlit_jupyter` patching)
- All major Streamlit APIs, with usage explanations and code examples
- Clear notes on which features work in Jupyter vs. which require a `.py` script

It’s designed for learners, tinkerers, and developers who want a hands-on, example-driven introduction to the Streamlit API—**directly in Jupyter or as a script**.

---

## Getting Started

To run Streamlit in Jupyter, install the necessary libraries:

```python
!pip install streamlit streamlit_jupyter
```

Then, patch Streamlit for Jupyter usage:

```python
from streamlit_jupyter import StreamlitPatcher
sp = StreamlitPatcher()
sp.jupyter()
import streamlit as st
```

> **Note:** Many examples work seamlessly in both Jupyter (with patching) and `.py` scripts. Where notebook support is unavailable, this is clearly indicated.

---

## What's Inside

The notebook is organized into the following sections:
- **Introduction:** What Streamlit is, and the aim of the notebook.
- **Getting Started:** How to install and initialize for Jupyter.
- **Core Display Functions:** Titles, headers, markdown, code, and LaTeX rendering.
- **Input Widgets:** Text, number, slider, select, checkbox, radio, multiselect, date, and time inputs.
- **Data Display & Metrics:** Tables, dataframes, JSON, and metrics.
- **Charts & Plots:** Plotly
- **Media Elements:** Image, audio, and video display (script-only).
- **Layout & Containers:** Columns, expanders, tabs, containers, and empty spaces (script-only).
- **File Upload/Download:** File upload (Jupyter-supported), download button (script-only).
- **Session State & Caching:** How to manage state and cache expensive computations .
- **Progress & Status:** Showing status, notifications, progress bars, and animations (script-only).
- **Experimental/Advanced APIs:** Description of advanced/experimental features and components (script-only).
- **Not Supported in Jupyter:** Explicitly notes functions that do not currently work in notebooks.

---

## Section-by-Section Guide

### Introduction
- Explains Streamlit’s core idea: quick web apps for data, ML, and dashboards.

### Getting Started
- Install and initialize Streamlit and `streamlit_jupyter`.
- Shows magic commands for auto-reload in Jupyter.

### Core Display Functions
- `st.title`, `st.header`, `st.subheader`, `st.markdown`, `st.write`, `st.code`, `st.latex`
- Examples for all, explaining their role in organizing and formatting content.

### Input Widgets
- Examples: `st.text_input`, `st.number_input`, `st.slider`, `st.checkbox`, `st.radio`, `st.selectbox`, `st.multiselect`, `st.date_input`, `st.time_input`, `st.button`
- Usage: Collect user input, selections, dates, times, etc.

### Data Display & Metrics
- `st.table`, `st.dataframe`, `st.data_editor` (for interactive tables)
- `st.json` for displaying dictionary/JSON objects
- `st.metric` for KPIs, numbers, and deltas

### Charts & Plots
- `st.line_chart`, `st.bar_chart`, `st.area_chart` for simple plots from pandas/numpy data
- `st.pyplot` (matplotlib)
- `st.plotly_chart`, `st.altair_chart`, `st.vega_lite_chart` for interactive plotting
- `st.map` for simple maps (requires latitude/longitude DataFrame columns)

### Media Elements
- `st.image`, `st.audio`, `st.video` for displaying images, playing audio or video

### Layout & Containers
- `st.columns` for side-by-side layout
- `st.expander` for collapsible sections
- `st.tabs` for tabbed navigation
- `st.container` and `st.empty` for layout control

### File Upload/Download
- `st.file_uploader`: Works in Jupyter for uploading files (e.g., CSV)
- `st.download_button`: **Not supported in Jupyter**—script only

### Session State & Caching
- Usage of `st.session_state` to persist variables across interactions (partial notebook support)
- `st.cache_data` and `st.cache_resource` for efficient, reactive computation

### Progress & Status
- `st.success`, `st.info`, `st.warning`, `st.error`: Notifications and status
- `st.progress` for progress bars (may have limited Jupyter support)
- `st.balloons`, `st.snow`: Fun status animations

### Experimental/Advanced APIs
- `st.experimental_rerun`, `st.experimental_get_query_params`, etc. — script only
- Streamlit Components — for advanced use

### Not Supported in Jupyter
- Lists major Streamlit functions unavailable in Jupyter (e.g., `st.sidebar`, `st.download_button`, reruns, etc.)
- Recommends using a `.py` script with `streamlit run` for full features

---

## Jupyter vs Script Support

| Feature                       | Jupyter Support         | Script Support (`.py`)   |
|-------------------------------|------------------------|--------------------------|
| Basic Display/Text            | ✅ Yes                 | ✅ Yes                   |
| Most Input Widgets            | ⚠️ Partial/Static      | ✅ Yes                   |
| Data Table/Editor             | ✅ Yes                 | ✅ Yes                   |
| Charts (line/bar/area/plotly) | ✅ Yes                 | ✅ Yes                   |
| Media Elements                | ❌ No                  | ✅ Yes                   |
| File Uploader                 | ❌ No                  | ✅ Yes                   |
| Download Button               | ❌ No                  | ✅ Yes                   |
| Sidebar                       | ❌ No                  | ✅ Yes                   |
| Progress Bar/Spinner          | ⚠️ Partial/Static      | ✅ Yes                   |
| Session State (complex)       | ⚠️ Partial             | ✅ Yes                   |
| Experimental APIs             | ❌ No                  | ✅ Yes                   |

---

## References & Further Reading

- [Streamlit Documentation](https://docs.streamlit.io/)
- [streamlit_jupyter Docs](https://ddobrinskiy.github.io/streamlit-jupyter/)
- [Awesome Streamlit Gallery](https://streamlit.io/gallery)
- [Streamlit GitHub](https://github.com/streamlit/streamlit)

---

**For any questions, improvements, or suggestions, feel free to open an issue or pull request. Happy Streamliting!**
