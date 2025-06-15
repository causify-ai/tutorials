# run.py
import threading
import time
import subprocess

def run_producer():
    subprocess.run(["python", "kafka/producer.py"])

def run_visualizer():
    #subprocess.run(["python", "visualization/plotter.py"])
    # Or to test basic consumer:
    # subprocess.run(["python", "kafka/consumer.py"])
    subprocess.Popen(["python", "visualization/plotter.py"], close_fds=True)


if __name__ == '__main__':
    print("Starting Producer and Visualizer...")

    producer_thread = threading.Thread(target=run_producer)
    visualizer_thread = threading.Thread(target=run_visualizer)

    producer_thread.start()
    time.sleep(2)  # Let producer get a head start
    visualizer_thread.start()

    producer_thread.join()
    visualizer_thread.join()
