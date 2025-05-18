import os
import subprocess

#step1: ingest btc price
print("\n Step 1: Ingesting BTC price...")
subprocess.run(["python", "ingest.py"])

#step2: upload csv to s3
print("\n Step 2: Uploading CSV to S3...")
subprocess.run(["python", "upload_to_s3.py"])

#step3: Generate BTC price chart
print("\n Step 3: Generating price trend chart...")
subprocess.run(["python", "analyze.py"])

#step4: Upload trend chart to S3
print("\n Step 4: Uploading trend chart to S3...")
subprocess.run(["python", "upload_plot_to_s3.py"])

#step5: Generate forecast chart
print("\n Step 5: Generating forecast chart...")
subprocess.run(["python", "forecast.py"])

#step6: Upload forecast chart to S3
print("\n Step 6: Uploading forecast chart to S3...")
subprocess.run(["python", "upload_forecast_to_s3.py"])

print("\n Pipleline complete!")