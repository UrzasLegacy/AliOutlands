import pyautogui
import pytesseract
import socket
import time
import pyttsx3
from PIL import Image, ImageOps, ImageFilter
import numpy as np
import cv2
import spacy
from nltk.corpus import words


def filter_image_cv2de(screenshot):
    resize = screenshot#resize_image(screenshot,2)
    #resize.show()
    gray_white_mask = resize#filter_non_gray_and_white(resize)
    image = np.array(gray_white_mask)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cv2.imshow('Image', gray)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    # Thresholding
    _, thresh_image = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    cv2.imshow('Image', thresh_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    # Dilation
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10,10))
    dilate = cv2.dilate(thresh_image, kernel, iterations=1)
    closing = cv2.morphologyEx(dilate, cv2.MORPH_CLOSE, kernel)
    cv2.imshow('Image', dilate)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    # Contour Detection
    contours, _ = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Sort contours
    contours = sorted(contours, key=lambda ctr: cv2.boundingRect(ctr)[0])

    result = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 32000 or area < 1000:
            continue
        x, y, w, h = cv2.boundingRect(contour)
        roi = dilate[y:y+h, x:x+w]
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
        
        opened = cv2.morphologyEx(roi, cv2.MORPH_OPEN, kernel)
        cv2.imshow('Image', opened)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        text = pytesseract.image_to_string(opened, config=r'--oem 3 --psm 10 tessedit_char_whitelist=0123456789')
        result.append(text.strip())
    final_text = ''.join(result)
    print("Final Text:", final_text)
    # contour = contours[0]
    # x, y, w, h = cv2.boundingRect(contour)
    # cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
    # crop = gray[y:y+h, x:x+w]
    # cv2.imshow('Image', text_contour)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    # # Run OCR on crop
    # return text_contour

def filter_image_cv2(screenshot):
    resize = screenshot#resize_image(screenshot,2)
    gray_white_mask = filter_non_gray_and_white(resize)
    image = np.array(gray_white_mask)
    # cv2.imshow('Image', image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    kernel = np.ones((20,20), np.uint8)
    dilation = cv2.dilate(thresh, kernel, iterations=1)
    contours, _ = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 32000 or area < 1000:
            cv2.drawContours(dilation, [contour], -1, 0, -1)
    contours, _ = cv2.findContours(dilation, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
    text_contour = None
    text_contour_length = 1
    pass_check = False
    for contour in contours:
        area = cv2.contourArea(contour)
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
        crop = gray[y:y+h, x:x+w]
        text = pytesseract.image_to_string(crop)
        if text:
            stripped = ''.join(text.split())
            spacyText = is_meaningful(text)
            if "Discord" in text:
                pass_check = True
                continue
            text_length = len(stripped)
            if text_length > text_contour_length and spacyText:
                text_contour_length = text_length
                text_contour = crop
    if pass_check:
        return text_contour
    return None

def capture_and_read(x, y, width, height):
    screenshot = pyautogui.screenshot(region=(x, y, width, height))
    threshold_img = filter_image_cv2de(screenshot)
    # OCR configuration
    custom_config = r'--oem 3 --psm 8 tessedit_char_whitelist=0123456789'
    try:
        text = pytesseract.image_to_string(threshold_img,config=custom_config)
    except Exception as e:
        text = ''
    return text.strip()

def resize_image(image, scale_factor):
    width, height = image.size
    new_size = (int(width * scale_factor), int(height * scale_factor))
    resized_image = image.resize(new_size, Image.LANCZOS)
    return resized_image

def filter_non_gray_and_white(image):
    # Convert image to numpy array and split color channels
    img_np = np.array(image)
    r, g, b = img_np[:,:,0], img_np[:,:,1], img_np[:,:,2]
    # Create mask for gray and white pixels
    mask = np.where((r == g) & (g == b), 1, 0)

    # Filter out non-gray and non-white pixels
    img_np = img_np * np.expand_dims(mask, axis=-1)
    # Convert filtered numpy array back to an image
    filtered_image = Image.fromarray(np.uint8(img_np))
    
    return filtered_image

def format_text(text):
    split_text = text.split('\n\n')
    try:
        header = split_text[0]
        body = split_text[1:] if len(split_text) > 0 else ""
        body_joined = ' '.join(body)
    except IndexError:
        return f"IndexError.{text}"  # or return some default text
    body_formatted = ' '.join(body_joined.split('\n'))
    msg = f"{header}\n{body_formatted}"
    return msg

def main():
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    screenWidth, screenHeight = pyautogui.size()
    x, y, width, height = 0, 0, screenWidth, screenHeight
    x, y, width, height = screenWidth - 370, screenHeight - 205, 110, 150
    last_text = ''
    while True:
        try:
            text = capture_and_read(x, y, width, height)
            print(f"text: {text}")
            # Wait until text stops changing
            while text != '' and last_text != text:
                print(text)
                last_text = text
                time.sleep(0.5)
                text = capture_and_read(x, y, width, height)
            if text:
                print(f"{time.asctime()}: {text}")
                msg = format_text(text)
                print(f"formatted: {msg}")
                last_text = text
                while text == last_text:
                    time.sleep(0.5)
                    text = capture_and_read(x, y, width, height)
        except Exception as e:
            print(f"An error occurred: {e}")
        time.sleep(0.5)

if __name__ == "__main__":
    main()

# UDP_IP = "localhost"
# UDP_PORT = 5005

# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
