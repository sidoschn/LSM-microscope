import numpy as np
from tifffile import imwrite

imageData = np.random.rand(256,256)
imageData = np.random.randint(65535, size=(2048,2048))
imageData16 = imageData.astype(np.uint16)

imwrite("test.tiff",imageData)
imwrite("test16.tiff",imageData16)