from data_ingestion import *

# Cronjob Command
# * * * * * /Users/sagarmaheshwari/Downloads/Datasets/Projects/projects/bin/python3 /Users/sagarmaheshwari/Downloads/UMDClasses/DATA605/src/tutorials1/DATA605/Spring2025/projects/TutorTask96_Spring2025_Real-Time_Bitcoin_Data_Processing_with_Gensim/data_ingestion_cron.py >> /Users/sagarmaheshwari/Downloads/UMDClasses/DATA605/src/tutorials1/DATA605/Spring2025/projects/TutorTask96_Spring2025_Real-Time_Bitcoin_Data_Processing_with_Gensim/logfile.log 2>&1

data_ingest(minutes=1)