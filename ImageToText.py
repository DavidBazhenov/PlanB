import cv2
import pytesseract


def grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def display(mass):
    id = 0
    for i in mass:
        cv2.imshow(str(id), i)
        id += 1
    cv2.waitKey(0)


def getSkewAngle(cvImage) -> float:
    # Prep image, copy, convert to gray scale, blur, and threshold
    newImage = cvImage.copy()
    gray = cv2.cvtColor(newImage, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (9, 9), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    # Apply to dilate to merge text into meaningful lines/paragraphs.
    # Use larger kernel on X axis to merge characters into single line, cancelling out any spaces.
    # But use smaller kernel on Y axis to separate between different blocks of text
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 5))
    dilate = cv2.dilate(thresh, kernel, iterations=2)
    # Find all contours
    contours, hierarchy = cv2.findContours(dilate, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    # Find the largest contour and surround in min area box
    if len(contours)>2:
        largestContour = contours[1]
    else:
        largestContour = contours[0]
    minAreaRect = cv2.minAreaRect(largestContour)
    center, size, angle = minAreaRect
    # Determine the angle. Convert it to the value that was originally used to obtain skewed image
    angle = angle - 90
    if angle < -45:
        angle = 90 + angle
    return -1.0 * angle


# Rotate the image around its center
def rotateImage(cvImage, angle: float):
    newImage = cvImage.copy()
    (h, w) = newImage.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    newImage = cv2.warpAffine(newImage, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return newImage


def deskew(cvImage):
    angle = getSkewAngle(cvImage)
    return rotateImage(cvImage, (-1.0 * angle))


def noise_removal(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    se = cv2.getStructuringElement(cv2.MORPH_RECT, (8, 8))
    bg = cv2.morphologyEx(image, cv2.MORPH_DILATE, se)
    out_gray = cv2.divide(image, bg, scale=255)
    out_binary = cv2.threshold(out_gray, 0, 255, cv2.THRESH_OTSU)[1]

    return (out_binary)


def thick_font(image):
    import numpy as np
    image = cv2.bitwise_not(image)
    kernel = np.ones((2, 2), np.uint8)
    image = cv2.dilate(image, kernel, iterations=1)
    image = cv2.bitwise_not(image)
    return image


def rescale(img, percent):
    # Вычисление новых размеров на основе процентного изменения
    new_width = int(img.shape[1] * percent / 100)
    new_height = int(img.shape[0] * percent / 100)

    # Изменение размера изображения
    resized_image = cv2.resize(img, (new_width, new_height))
    return resized_image

def img_to_text(lang, img):
    # resize
    #img = rescale(img, 100)
    # rotate
    fixed = deskew(img)
    # обработка и фильтрация
    no_noise = noise_removal(fixed)
    # Dilation and Erosion
    dilated_image = thick_font(no_noise)
    # display([img, fixed, no_noise, dilated_image])
    output = pytesseract.image_to_string(dilated_image, lang=lang)
    return output


#image_file = "1.png"
#image_file = "new_img/2.png"
#img = cv2.imread(image_file)
#print(img_to_text("rus", img))