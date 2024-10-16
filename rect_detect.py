import cv2
import numpy as np

def edge_detect(im):
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    gaus = cv2.GaussianBlur(gray, (5,5), 0)
    mask = cv2.Canny(gaus, threshold1=100, threshold2=200)
    return mask


def areaFilter(arThres, inputImage):

    # Perform an area filter on the binary blobs:
    componentsNumber, labeledImage, componentStats, componentCentroids = \
cv2.connectedComponentsWithStats(inputImage, connectivity=4)

    # Get the indices/labels of the remaining components based on the area stat
    # (skip the background component at index 0)
    remainingComponentLabels = [i for i in range(1, componentsNumber) if arThres <= componentStats[i][4]]

    # Filter the labeled pixels based on the remaining labels,
    # assign pixel intensity to 255 (uint8) for the remaining pixels
    filteredImage = np.where(np.isin(labeledImage, remainingComponentLabels) == True, 255, 0).astype('uint8')

    return filteredImage

def rect_contours(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    mask = cv2.GaussianBlur(gray, (5, 5), 0)

    mask = edge_detect(img)
    kern_size = 3
    struct_elem = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kern_size, kern_size))
    it = 2
    mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, struct_elem, None, None, it, cv2.BORDER_REFLECT101)
    mask = cv2.morphologyEx(mask, cv2.MORPH_ERODE, struct_elem, None, None, it, cv2.BORDER_REFLECT101)

    contours, _ = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

    return contours

def box_detect(contour, area_range):
    p = cv2.arcLength(contour, True)
    poly = cv2.approxPolyDP(contour, 0.04 * p, True)
    rect = cv2.boundingRect(poly)
    area = rect[2] * rect[3]
    if area_range[0] < area < area_range[1]:
        return rect

def box_detect_r(contour, ratio):
    p = cv2.arcLength(contour, True)
    poly = cv2.approxPolyDP(contour, 0.04 * p, True)
    rect = cv2.boundingRect(poly)
    rat = rect[2] / rect[3] 
    if ratio[0] < rat < ratio[1]:
        return rect
