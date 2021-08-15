from scipy.signal.signaltools import correlate2d as c2d
from scipy import ndimage
import numpy as np


def edge(img):
    # Diff in x-directioin
    img_x = ndimage.filters.gaussian_filter(img, (5, 5), (0, 1))
    # Diff in y-directioin
    img_y = ndimage.filters.gaussian_filter(img, (5, 5), (1, 0))
    # Merge

    img_xy = np.hypot(img_x, img_y)
    return img_xy


def correct_drift(image1, image2):
    x_array = image1.x.values
    y_array = image1.y.values
    index = np.array([x_array.shape[0] / 2 - 1, y_array.shape[0] / 2 - 1])
    correlation_image = c2d(edge(image1.values), edge(image2.values), mode='same')
    index = np.array(np.unravel_index(np.argmax(correlation_image), correlation_image.shape)) - index
    delta = np.array([(x_array.max() - x_array.min()) / x_array.shape[0], (y_array.max() - y_array.min()) / y_array.shape[0]])
    return delta * index
