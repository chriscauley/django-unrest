import cv2
import numpy as np
import sys
import unrest.image as img

def list_colors(image, ignore_black=True, cutoff=0.01):
    image = cv2.imread(image)
    colors = image.reshape(-1, image.shape[-1])
    counts = np.unique(colors, axis=0, return_counts = True)
    counts = sorted(zip(*counts),key=lambda a: -a[1])
    if ignore_black:
        counts = [c for c in counts if any(c[0])]
    if cutoff:
        total = sum([c[1] for c in counts])
        counts = [c for c in counts if c[1] > total * cutoff]
    return counts

if __name__ == "__main__":
    colors = list_colors(sys.argv[1])
    image = cv2.imread(sys.argv[1])
    cv2.imshow('og', image)
    result = None
    for color, count in colors[:4]:
        reduced = cv2.inRange(image, color, color)
        cv2.imshow(str(color), reduced)
        if result is not None:
            result = result | reduced
        else:
            result = reduced
    cv2.imshow('final', result)
    cv2.waitKey(0)