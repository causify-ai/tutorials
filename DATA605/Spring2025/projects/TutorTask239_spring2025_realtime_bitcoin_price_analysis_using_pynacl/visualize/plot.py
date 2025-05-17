import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from analysis.analytics import window

def animate(i):
    if not window:
        return  # Don't plot until data exists
    plt.cla()
    plt.plot(list(window), label='BTC Price')
    plt.title("Real-Time BTC Price (Last 10min)")
    plt.xlabel("Most Recent Seconds")
    plt.ylabel("Price (USD)")
    plt.legend()


def start_plotting():
    ani = FuncAnimation(plt.gcf(), animate, interval=1000)
    plt.tight_layout()
    plt.show()
