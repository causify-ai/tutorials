# Real-Time Bitcoin Blockchain Metrics Visualization and Time Series Analysis

This project was created for **DATA605 (Spring 2025)** as a demonstration of how to ingest, process, and visualize **live blockchain data** using Python and Plotly. The focus is on three key Bitcoin metrics:

- **Transaction Count**
- **Block Size**
- **Hash Rate**

The tool also includes basic **time series analysis** and the ability to **update in real time**.

---

##  Project Goals

- Learn how to collect data using a public API.
- Analyze blockchain metrics in time series form.
- Create interactive visualizations using Plotly.
- Understand and explore trends using decomposition.

---

##  Project Structure

```
.
├── Bitcoin_API.py             # Script to fetch Bitcoin data from Blockchain.com API
├── template_example.ipynb     # Jupyter Notebook that runs the complete analysis and visualization
├── template/                  
│   └── API.py                 # Contains a class for API calls (used in the notebook)
├── requirements.txt           # Required Python libraries
├── README.md                  # Project overview and usage
```

---

##  How It Works

1. **API Access**: Uses the Blockchain.com public API to pull Bitcoin metrics.
2. **Data Handling**: Parses JSON responses and converts them to clean pandas DataFrames.
3. **Visualization**: Generates subplots and time series charts using Plotly.
4. **Time Series Decomposition**: Applies seasonal decomposition to show trends and seasonality.
5. **Real-Time Updates**: Automatically updates metrics in fixed time intervals using `threading`.

---

##  Running the Project

Make sure you have the required libraries installed:

```bash
pip install -r requirements.txt
```

Then, run the Jupyter Notebook:

```bash
jupyter notebook template_example.ipynb
```

---

##  Features

- Interactive visualizations with zoom and hover features
- Real-time updates every 60 seconds (configurable)
- HTML export of final plots
- Clean and student-friendly code with comments

---

##  Skills Demonstrated

- REST API integration
- Time series preprocessing and decomposition
- Interactive data visualization
- Threaded execution for live data handling

---

##  Data Source

All blockchain data is fetched from the [Blockchain.com Charts API](https://www.blockchain.com/explorer/api/charts-api).

---

##  Author

Varun P.  
Graduate Student, MS in Data Science  
DATA605 – Spring 2025  
