from scipy.signal.signaltools import correlate2d as c2d
from scipy import ndimage
import numpy as np
import cv2
import matplotlib.pyplot as plt


def edge(img):
    # Diff in x-directioin
    img_x = ndimage.filters.gaussian_filter(img, (5, 5), (0, 1))
    # Diff in y-directioin
    img_y = ndimage.filters.gaussian_filter(img, (5, 5), (1, 0))
    # Merge

    img_xy = np.hypot(img_x, img_y)
    return img_xy


def correct_drift_deprecated(image1, image2):
    x_array = image1.x.values
    y_array = image1.y.values
    index = np.array([x_array.shape[0] / 2 - 1, y_array.shape[0] / 2 - 1])
    correlation_image = c2d(edge(image1.values), edge(image2.values), mode='same', boundary='wrap')
    index = np.flipud(np.array(np.unravel_index(np.argmax(correlation_image), correlation_image.shape))) - index
    delta = np.array([(x_array.max() - x_array.min()) / x_array.shape[0], (y_array.max() - y_array.min()) / y_array.shape[0]])
    return delta * index


# This is much better than the one above
def moving_amount(image1, image2):

    x_array = image1.x.values
    y_array = image1.y.values

    image1 = (image1.values / image1.values.max() * 255).astype(np.uint8)  # convert to uint8 array
    image1 = np.flip(image1, 1)  # fix flipping

    image2 = (image2.values / image2.values.max() * 255).astype(np.uint8)  # convert to uint8 array
    image2 = np.flip(image2, 1)  # fix flipping

    sift = cv2.SIFT_create()
    # 特徴点抽出
    kp1, des1 = sift.detectAndCompute(image1, None)
    kp2, des2 = sift.detectAndCompute(image2, None)

    bf = cv2.BFMatcher()
    # マッチング
    matches = bf.match(des1, des2)
    matches = sorted(matches, key=lambda x: x.distance)

    move_list = []

    best_match_std = 1
    for i, item in enumerate(matches):
        pt2 = np.array([kp2[item.trainIdx].pt[0], kp2[item.trainIdx].pt[1]])
        pt1 = np.array([kp1[item.queryIdx].pt[0], kp1[item.queryIdx].pt[1]])
        move = pt2 - pt1
        move[1] = -move[1]  # fix image flipping
        move_list.append(move)
        match_std = np.array(move_list).std(axis=0).mean()
        if i == 0:
            valild_match_num = 1
        elif match_std > best_match_std:
            break
        else:
            valild_match_num = i + 1
            best_match_std = match_std

    move_array = np.array(move_list)[:valild_match_num]
    out = cv2.drawMatches(image1, kp1, image2, kp2, matches[:valild_match_num], None, flags=2)
    plt.imshow(out), plt.show()
    move_index = move_array.mean(axis=0)
    move_index_std = move_array.std(axis=0)
    delta = np.array([(x_array.max() - x_array.min()) / x_array.shape[0], (y_array.max() - y_array.min()) / y_array.shape[0]])
    return delta * move_index, delta * move_index_std
