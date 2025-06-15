def check_stationarity(series):
    result = adfuller(series.dropna())
    logging.info(f'ADF Statistic: {result[0]}')
    logging.info(f'p-value: {result[1]}')
    if result[1] <= 0.05:
        logging.info('✅ The series is stationary.')
    else:
        logging.info('❌ The series is NOT stationary. Differencing is needed.')