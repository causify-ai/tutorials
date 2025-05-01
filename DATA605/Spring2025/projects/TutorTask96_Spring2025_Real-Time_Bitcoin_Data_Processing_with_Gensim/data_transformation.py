import pandas as pd
import numpy as np
from loguru import logger

def data_transform(df, window):
    '''
    We can change percentage definition based on use cases 
    More definition = More accurate decision
    '''
    df = df.sort_values(by=['date','time'])
    # Calculate precentage price change (delta)
    df['perc_change'] = df['price'].pct_change() * 100
    df['perc_change'] = df['perc_change'].fillna(0)

    def categories(pct):
        if pct > 0.05: return 'large_up'
        elif pct > 0.02: return 'medium_up'
        elif pct < -0.05: return 'large_down'
        elif pct < -0.02: return 'medium_down'
        else: return 'stable'

    df['movement'] = df['perc_change'].apply(categories)

    # Create x-minute interval windows -> Segmentation
    window_size = window
    df['window'] = (df.index // window_size)
    logger.info("Segmented data with window size of: "+str(window))
    return df


def segmentation(df):
    # Group by window and convert price labels to tokens
    documents = df.groupby('window')['movement'].apply(list).tolist()
    logger.info("Segmented data into documents")
    return documents