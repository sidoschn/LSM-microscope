import matplotlib.pyplot as plt
import pco
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.colors import Normalize

# Initialize figure and axis
fig, ax = plt.subplots()
img_plot = ax.imshow(np.zeros((2048, 2048)), cmap='gray', norm=Normalize(vmin=0, vmax=255))  # Adjust the normalization
ax.set_ylim(0, 2048)
ax.set_xlim(0, 2048)

def update(frame):
    img, meta = cam.image()
    img_plot.set_array(img)
    return img_plot,

with pco.Camera(interface='USB 3.0') as cam:
    cam.sdk.set_delay_exposure_time(0, 'ms', 10, 'ms')
    cam.record(5,mode="ring buffer")
    cam.wait_for_first_image()

    ani = FuncAnimation(fig, update, frames=41) 
    plt.show()
