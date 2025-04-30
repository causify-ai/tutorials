from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import pandas as pd
from template_utils import generate_dashboard, apply_transforms, get_combined_data

app = FastAPI()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <title>Bitcoin Dashboard</title>
  <script src="https://cdn.jsdelivr.net/npm/vega@5"></script>
  <script src="https://cdn.jsdelivr.net/npm/vega-lite@5"></script>
  <script src="https://cdn.jsdelivr.net/npm/vega-embed@6"></script>
  <style>
    body { font-family: sans-serif; padding: 2rem; }
    #vis { width: 100%; height: auto; }
  </style>
</head>
<body>
  <h1>📈 Bitcoin Dashboard</h1>
  <div id="vis">Loading chart...</div>
  <script>
    fetch("/chart")
      .then(response => response.json())
      .then(spec => {
        vegaEmbed('#vis', spec).catch(console.error);
      })
      .catch(err => {
        document.getElementById('vis').textContent = 'Failed to load chart';
        console.error("Chart load error:", err);
      });
  </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def render_dashboard(request: Request):
    return HTMLResponse(content=HTML_TEMPLATE)

@app.get("/chart")
async def get_chart():
    df = get_combined_data()
    if df is None or df.empty:
        return JSONResponse(content={"error": "No data available"}, status_code=200)
    transformed = apply_transforms(df)
    chart = generate_dashboard(transformed)
    return JSONResponse(content=chart.to_dict())