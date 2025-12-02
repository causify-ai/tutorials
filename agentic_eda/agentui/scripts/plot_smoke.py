#!/usr/bin/env python3
import matplotlib.pyplot as plt
import numpy as np
import os

x = np.linspace(0, 10, 100)
y = np.sin(x)
plt.plot(x, y)
os.makedirs('examples/images', exist_ok=True)
plt.savefig('examples/images/sine.png')
