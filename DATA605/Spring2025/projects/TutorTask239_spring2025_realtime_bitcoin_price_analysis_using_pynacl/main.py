from ingest.fetch_binance import start_stream, main_plotting_loop
from threading import Thread

if __name__ == '__main__':
    Thread(target=start_stream).start()
    main_plotting_loop()
