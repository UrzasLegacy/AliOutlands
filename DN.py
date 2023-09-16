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
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
import os
import psutil

def setup_tts_engine():
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    engine.setProperty('rate', 200)
    engine.setProperty('volume', 0.9)
    return engine

original_volumes = {}
def attenuate_other_sounds():
    global original_volumes
    process = psutil.Process(os.getpid())
    process_name = process.name()
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        if session.Process and session.Process.name() != process_name:
            volume = session._ctl.QueryInterface(ISimpleAudioVolume)
            original_volumes[session.Process.name()] = volume.GetMasterVolume()
            volume.SetMasterVolume(0.2, None)

def restore_volumes():
    global original_volumes
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        if session.Process and session.Process.name() in original_volumes:
            volume = session._ctl.QueryInterface(ISimpleAudioVolume)
            volume.SetMasterVolume(original_volumes[session.Process.name()], None)

word_list = set(words.words())
def is_a_word(word):
    boole = word.lower() in word_list
    #print(f"word check: {word}: {boole}")
    return boole

nlp = spacy.load("en_core_web_sm")
def is_meaningful(text):
    doc = nlp(text)
    meaningful_words = [token.text for token in doc if is_a_word(token.text)]
    if len(meaningful_words) > 1:  # Arbitrary threshold
        #print('joined' + ':'.join(meaningful_words))
        return True
    return False

def filter_image_cv2de(screenshot):
    resize = screenshot#resize_image(screenshot,2)
    #resize.show()
    gray_white_mask = filter_non_gray_and_white(resize)
    image = np.array(gray_white_mask)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cv2.imshow('Image', gray)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    # Threshold
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    cv2.imshow('Image', thresh)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    #contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # Initialize an array of zeros with the same shape as the original gray image
    #filtered = np.zeros_like(gray)
    # Filter contours based on area
    # min_area = 5  # set your own minimum area
    # for contour in contours:
    #     if cv2.contourArea(contour) >= min_area:
    #         cv2.drawContours(filtered, [contour], -1, 255, thickness=cv2.FILLED)
    # # Dilate to connect letters
    kernel = np.ones((20,20), np.uint8)
    dilation = cv2.dilate(thresh, kernel, iterations=1)
    cv2.imshow('Image', dilation)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    # Find contours
    contours1, _ = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Loop through the contours
    for contour in contours1:
        area = cv2.contourArea(contour)
        if area > 32000 or area < 2000:
            cv2.drawContours(dilation, [contour], -1, 0, -1)  # Fills the contour with black
    cv2.imshow('Image', dilation)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    #Find contours
    contours2, _ = cv2.findContours(dilation, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours2 = sorted(contours2, key=cv2.contourArea, reverse=True)[:10]
    #print(f'length: {len(contours)}')
    text_contour = None
    text_contour_length = 1
    for contour in contours2:
        area = cv2.contourArea(contour)
        print(f"area: {area}")
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
        crop = gray[y:y+h, x:x+w]
        text = pytesseract.image_to_string(crop)
        if text:
            stripped = ''.join(text.split())
            spacyText = is_meaningful(text)
            print('text:' + text)
            print('stripped:' + stripped)
            text_length = len(stripped)
            if text_length > text_contour_length and spacyText:
                text_contour_length = text_length
                text_contour = crop
            cv2.imshow('Image', crop)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
    # contour = contours[0]
    # x, y, w, h = cv2.boundingRect(contour)
    # cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
    # crop = gray[y:y+h, x:x+w]
    cv2.imshow('Image', text_contour)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    # Run OCR on crop
    return text_contour

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

def filter_image_Pillow(image):
    resize = resize_image(image,3)
    gray_white_mask = filter_non_gray_and_white(resize)
    #Grayscale
    gray_img = ImageOps.grayscale(gray_white_mask)
    #Thresholding
    threshold_img = gray_img.point(lambda x: 0 if x < 100 else 255, '1')
    threshold_img.show()
    return threshold_img

def capture_and_read(x, y, width, height):
    screenshot = pyautogui.screenshot(region=(x, y, width, height))
    threshold_img = filter_image_cv2(screenshot)
    try:
        text = pytesseract.image_to_string(threshold_img)
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
    x, y, width, height = screenWidth - 370, screenHeight - 220, 340, 175
    engine = setup_tts_engine()
    last_text = ''
    while True:
        try:
            text = capture_and_read(x, y, width, height)
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
                engine.say(msg)
                time.sleep(.1)
                pyautogui.press('playpause')
                time.sleep(.1)
                attenuate_other_sounds()
                engine.runAndWait()
                restore_volumes()
                time.sleep(.1)
                pyautogui.press('playpause')
                time.sleep(.1)
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
