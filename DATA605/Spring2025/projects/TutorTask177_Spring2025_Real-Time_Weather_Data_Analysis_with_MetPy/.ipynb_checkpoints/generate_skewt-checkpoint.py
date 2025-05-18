import requests
import datetime
import time
import os
import matplotlib.pyplot as plt
import numpy as np
from metpy.plots import SkewT
from metpy.units import units

# Cities with their station IDs (use numeric station codes)
cities = {
    "London": "03772",   # EGLL
    "New York": "72503", # KNYC
    "Paris": "07157",    # LFPB
    # Add more city:station codes as needed
}

# Directory to save data and plots
DATA_DIR = "sounding_data"
os.makedirs(DATA_DIR, exist_ok=True)

def fetch_sounding(station, dt):
    """
    Fetch sounding text data from University of Wyoming site for a station and datetime.
    dt: datetime object in UTC (aware or naive)
    Returns raw text data or raises Exception.
    """
    base_url = "http://weather.uwyo.edu/cgi-bin/sounding?"
    params = {
        "region": "naconf",
        "TYPE": "TEXT:LIST",
        "YEAR": dt.strftime("%Y"),
        "MONTH": dt.strftime("%m"),
        "FROM": dt.strftime("%d%H"),
        "TO": dt.strftime("%d%H"),
        "STNM": station,
    }
    url = base_url + "&".join(f"{k}={v}" for k, v in params.items())

    print(f"Fetching {station} sounding for {dt} ...")
    resp = requests.get(url)
    if resp.status_code != 200 or "Sorry" in resp.text:
        raise RuntimeError(f"Failed to fetch data: HTTP {resp.status_code} or server busy")

    return resp.text

def save_sounding(text, city, dt):
    filename = os.path.join(DATA_DIR, f"skewt_{city}_{dt.strftime('%Y%m%d%H')}.txt")
    with open(filename, "w") as f:
        f.write(text)
    print(f"Saved sounding data to {filename}")
    return filename

def plot_skewt(filename, city_name):
    with open(filename, 'r') as f:
        lines = f.readlines()

    # Find start of sounding data (line after dashed line)
    start = 0
    for i, line in enumerate(lines):
        if '-------' in line:
            start = i + 1
            break

    pressure = []
    temperature = []
    dewpoint = []
    wind_dir = []
    wind_speed = []

    for line in lines[start:]:
        parts = line.strip().split()
        if len(parts) < 11:
            continue
        try:
            p = float(parts[0])
            t = float(parts[1])
            td = float(parts[2])
            wd = float(parts[6])
            ws = float(parts[7])
            if p == -9999 or t == -9999 or td == -9999:
                continue
            pressure.append(p)
            temperature.append(t)
            dewpoint.append(td)
            wind_dir.append(wd)
            wind_speed.append(ws)
        except ValueError:
            break

    if len(pressure) == 0:
        print(f"No valid data found in {filename}, skipping plot.")
        return

    pressure = np.array(pressure) * units.hPa
    temperature = np.array(temperature) * units.degC
    dewpoint = np.array(dewpoint) * units.degC
    wind_speed = np.array(wind_speed) * units.knots
    wind_dir = np.array(wind_dir) * units.degrees

    fig = plt.figure(figsize=(9, 9))
    skew = SkewT(fig)

    skew.plot(pressure, temperature, 'r')
    skew.plot(pressure, dewpoint, 'g')
    skew.plot_barbs(pressure, wind_dir, wind_speed)

    skew.ax.set_ylim(1000, 100)
    skew.ax.set_xlim(-40, 60)
    plt.title(f'Skew-T Log-P Diagram for {city_name}')

    pngfile = filename.replace('.txt', '.png')
    plt.savefig(pngfile)
    plt.close()
    print(f"Saved Skew-T plot to {pngfile}")

def get_latest_sounding_time():
    """Return nearest past 00Z or 12Z UTC sounding time."""
    now = datetime.datetime.now(datetime.timezone.utc)
    hour = now.hour
    if hour >= 12:
        return now.replace(hour=12, minute=0, second=0, microsecond=0)
    else:
        return now.replace(hour=0, minute=0, second=0, microsecond=0)

def main():
    dt = get_latest_sounding_time()

    for city, station in cities.items():
        retries = 3
        for attempt in range(retries):
            try:
                raw_text = fetch_sounding(station, dt)
                fname = save_sounding(raw_text, city, dt)
                plot_skewt(fname, city)
                break  # Success, no retry needed
            except Exception as e:
                print(f"Attempt {attempt+1} failed for {city}: {e}")
                if attempt < retries - 1:
                    print("Retrying in 10 seconds...")
                    time.sleep(10)
                else:
                    print(f"Skipping {city} after {retries} failed attempts.")

if __name__ == "__main__":
    main()
