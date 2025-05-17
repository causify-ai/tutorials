import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from activecampaign_api import get_campaigns


def simulate_email_data_spikey() -> pd.DataFrame:
    names = [
        'Newsletter', 'Promo Blast', 'Weekly Update', 'Career Hack Alert',
        'UMD RecWell Notice', '50% Pro Discount', 'Free Fries Friday',
        'Job Alerts', 'AI Tips Newsletter'
    ]
    end_date = datetime.now()
    date_range = pd.date_range(end=end_date, periods=30)

    simulated_rows = []
    for date in date_range:
        weekday = date.weekday()
        open_mean = 150 + np.random.randint(0, 50) if weekday < 5 else 60 + np.random.randint(0, 20)
        for name in names:
            opens = np.random.poisson(lam=open_mean)
            unique_opens = max(0, int(opens * np.random.uniform(0.5, 0.8)))
            clicks = max(0, int(opens * np.random.uniform(0.2, 0.4)))
            unique_clicks = max(0, int(clicks * np.random.uniform(0.5, 0.9)))
            unsubscribes = np.random.binomial(n=3, p=0.05)

            simulated_rows.append({
                'name': name,
                'cdate': date,
                'opens': opens,
                'uniqueopens': unique_opens,
                'linkclicks': clicks,
                'uniquelinkclicks': unique_clicks,
                'unsubscribes': unsubscribes
            })

    df = pd.DataFrame(simulated_rows)
    df['cdate'] = pd.to_datetime(df['cdate'])
    return df


# Load data
real_df = get_campaigns()
real_df['cdate'] = pd.to_datetime(real_df['cdate']).dt.tz_localize(None)
sim_df = simulate_email_data_spikey()

# Combine and clean
combined_df = pd.concat([real_df, sim_df], ignore_index=True).sort_values(by="cdate")
combined_df.to_csv("combined_campaign_data.csv", index=False)

# Type conversion
cols_to_convert = ['opens', 'uniqueopens', 'linkclicks', 'uniquelinkclicks', 'unsubscribes']
for col in cols_to_convert:
    combined_df[col] = pd.to_numeric(combined_df[col], errors='coerce')
combined_df.fillna(0, inplace=True)
combined_df = combined_df.infer_objects(copy=False)

# Daily engagement plot
daily_summary = combined_df.groupby('cdate').agg({'opens': 'sum', 'linkclicks': 'sum'})
plt.figure(figsize=(12, 6))
plt.plot(daily_summary.index, daily_summary['opens'], label='Opens', marker='o')
plt.plot(daily_summary.index, daily_summary['linkclicks'], label='Clicks', marker='x')
plt.xticks(rotation=45)
plt.title("Daily Email Engagement")
plt.xlabel("Date")
plt.ylabel("Count")
plt.legend()
plt.tight_layout()
plt.savefig("campaign_trends_plot.png")
print("Saved: campaign_trends_plot.png")

# Weekday analysis
combined_df['weekday'] = combined_df['cdate'].dt.day_name()
weekday_summary = combined_df.groupby('weekday').agg({
    'opens': 'sum',
    'linkclicks': 'sum',
    'unsubscribes': 'sum'
}).reindex([
    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
])
weekday_summary.plot(kind='bar', figsize=(12, 6), colormap='viridis')
plt.title("Engagement Metrics by Weekday")
plt.ylabel("Count")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("engagement_by_weekday.png")
print("Saved: engagement_by_weekday.png")

# Derived metrics: Open Rate & CTR
combined_df['open_rate'] = combined_df['uniqueopens'] / combined_df['opens']
combined_df['ctr'] = combined_df['uniquelinkclicks'] / combined_df['uniqueopens']
combined_df[['open_rate', 'ctr']] = combined_df[['open_rate', 'ctr']].fillna(0)

daily_kpi = combined_df.groupby('cdate').agg({
    'open_rate': 'mean',
    'ctr': 'mean'
})
plt.figure(figsize=(12, 6))
plt.plot(daily_kpi.index, daily_kpi['open_rate'], label='Avg Open Rate', marker='o')
plt.plot(daily_kpi.index, daily_kpi['ctr'], label='Avg CTR', marker='x')
plt.title("Daily Open Rate & CTR Trends")
plt.xlabel("Date")
plt.ylabel("Rate")
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()
plt.savefig("openrate_ctr_trends.png")
print("Saved: openrate_ctr_trends.png")

# Top performing campaigns
top_campaigns = combined_df.groupby('name').agg({
    'opens': 'sum',
    'linkclicks': 'sum',
    'unsubscribes': 'sum'
}).sort_values(by='linkclicks', ascending=False).head(10)
print("Top Performing Campaigns:")
print(top_campaigns)
top_campaigns.to_csv("top_campaigns.csv")

# Heatmap: Opens by weekday-hour
combined_df['hour'] = np.random.randint(8, 20, size=len(combined_df))
heatmap_df = combined_df.groupby(['weekday', 'hour'])['opens'].sum().unstack(fill_value=0)
plt.figure(figsize=(14, 6))
sns.heatmap(heatmap_df, cmap='Blues', annot=True, fmt='g')
plt.title("Heatmap of Opens by Weekday & Hour")
plt.tight_layout()
plt.savefig("opens_heatmap.png")
print("Saved: opens_heatmap.png")

# Moving average trend
window = 3
daily_summary['opens_ma'] = daily_summary['opens'].rolling(window).mean()
daily_summary['clicks_ma'] = daily_summary['linkclicks'].rolling(window).mean()
plt.figure(figsize=(12, 6))
plt.plot(daily_summary.index, daily_summary['opens_ma'], label='Opens (3-day MA)', marker='o')
plt.plot(daily_summary.index, daily_summary['clicks_ma'], label='Clicks (3-day MA)', marker='x')
plt.title("Smoothed Engagement Trend (3-day Moving Avg)")
plt.xlabel("Date")
plt.ylabel("Count")
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()
plt.savefig("moving_avg_trend.png")
print("Saved: moving_avg_trend.png")

