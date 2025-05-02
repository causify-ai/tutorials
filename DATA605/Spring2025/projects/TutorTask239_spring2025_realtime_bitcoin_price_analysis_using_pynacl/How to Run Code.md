Make sure python version > 3.9

python3 -m venv dhanush_venv
source dhanush_venv/bin/activate
pip3 install -r requirements.txt

In terminal 1 : (collects, encrypts, stores, groups data in one minute intervals and plots the data)
python3 main.py

In terminal 2 : (runs hourly analysis on the collected data and adds results to analysis and forcasting tables and plots all the results till now)
python3 -m analysis.run_hourly_analysis

In terminal 3 : (exposed dashboard to visualise BTC price, indicators and forcast)
python3 -m visualize.dashboard

Note: all 3 processes cant run in parallel on mac. DuckDB doesn't allow multiple treadded connection at the same time. So, for now run one at a time. 
