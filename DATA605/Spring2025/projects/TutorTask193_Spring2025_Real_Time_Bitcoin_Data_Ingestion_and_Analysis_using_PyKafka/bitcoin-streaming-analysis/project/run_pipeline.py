from producer.btc_producer import run_producer
from consumer.btc_consumer import run_consumer
import multiprocessing

if __name__ == "__main__":
    p1 = multiprocessing.Process(target=run_producer)
    p2 = multiprocessing.Process(target=run_consumer)

    p1.start()
    p2.start()

    p1.join()
    p2.join()
