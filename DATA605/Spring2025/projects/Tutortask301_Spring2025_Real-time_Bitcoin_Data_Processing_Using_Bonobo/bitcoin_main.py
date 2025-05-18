from bitcoin_API import BitcoinPipeline
import logging
import time

logging.basicConfig(level=logging.INFO)

def main():
    pipeline = BitcoinPipeline()
    for i in range(10):  # example: fetch 10 records
        logging.info(f"Iteration {i+1}/10")
        data = pipeline.fetch_data()
        transformed = pipeline.transform_data(data)
        if transformed:
            pipeline.save_data(transformed)
        time.sleep(5)

    pipeline.analyze_data()

if __name__ == "__main__":
    main()
