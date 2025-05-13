from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import pandas as pd
from Altair_utils import generate_dashboard, apply_transforms, get_combined_data

app = FastAPI()

# Serve the HTML dashboard
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
        vegaEmbed("#vis", spec);
      });
  </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def get_home():
    return HTML_TEMPLATE

@app.get("/chart")
async def get_chart():
    try:
        df = get_combined_data()
        transformed = apply_transforms(df)
        chart = generate_dashboard(transformed)
        return JSONResponse(content=chart.to_dict())
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
