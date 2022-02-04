from unrest.utils import mkdir

import cv2
import sys
import os

def white_background(image):
  image = image.copy()
  trans_mask = image[:,:,3] == 0
  image[trans_mask] = [255, 255, 255, 255]
  return cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)

def extract_sprites(image, dest='.cache', show=True):
  fname = image.rsplit('.', 1)[0]
  dest = mkdir(dest, fname)
  image = cv2.imread(image, cv2.IMREAD_UNCHANGED)
  white = white_background(image)
  gray = cv2.cvtColor(white, cv2.COLOR_BGR2GRAY)
  thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

  # Original script used the following to try to get multipart sprites to join together
  # maybe make this a kwarg option?
  # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
  # close = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
  # dilate = cv2.dilate(close, kernel, iterations=1)

  cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
  cnts = cnts[0] if len(cnts) == 2 else cnts[1]

  sprite_number = 0
  crops = []
  for c in cnts:
    x, y, w, h = cv2.boundingRect(c)
    ROI = image[y:y+h, x:x+w]
    out_path = os.path.join(dest, f'{fname}_{sprite_number}.png')
    crops.append(out_path)
    cv2.imwrite(out_path, ROI)
    cv2.rectangle(image, (x, y), (x + w, y + h), (36, 255, 12), 2)
    sprite_number += 1

  if show:
    cv2.imshow('thresh', thresh)
    # cv2.imshow('dilate', dilate)
    cv2.imshow('image', image)
    cv2.waitKey()


if __name__ == "__main__":
  extract_sprites(sys.argv[1])