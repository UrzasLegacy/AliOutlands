#import cv2
#import pytesseract
#import matplotlib.pyplot as plt
import numpy as np

# Function to perform template matching
def template_matching(image, template, threshold=0.8):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    
    # Create a mask from the alpha channel of the template
    _, _, _, alpha = cv2.split(template)
    mask = alpha
    
    # Perform template matching
    result = cv2.matchTemplate(gray_image, gray_template, cv2.TM_CCOEFF_NORMED, mask=mask)
    loc = np.where(result >= threshold)
    
    # Collect rectangles for detected regions
    rects = []
    for pt in zip(*loc[::-1]):
        rects.append([pt[0], pt[1], pt[0] + gray_template.shape[1], pt[1] + gray_template.shape[0]])
    
    return rects

# Function to apply non-maximum suppression
def non_max_suppression_fast(boxes, overlapThresh):
    if len(boxes) == 0:
        return []

    boxes = np.array(boxes)
    if boxes.dtype.kind == "i":
        boxes = boxes.astype("float")
    
    pick = []
    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 2]
    y2 = boxes[:, 3]

    area = (x2 - x1 + 1) * (y2 - y1 + 1)
    idxs = np.argsort(y2)

    while len(idxs) > 0:
        last = len(idxs) - 1
        i = idxs[last]
        pick.append(i)

        xx1 = np.maximum(x1[i], x1[idxs[:last]])
        yy1 = np.maximum(y1[i], y1[idxs[:last]])
        xx2 = np.minimum(x2[i], x2[idxs[:last]])
        yy2 = np.minimum(y2[i], y2[idxs[:last]])

        w = np.maximum(0, xx2 - xx1 + 1)
        h = np.maximum(0, yy2 - yy1 + 1)

        overlap = (w * h) / area[idxs[:last]]

        idxs = np.delete(idxs, np.concatenate(([last], np.where(overlap > overlapThresh)[0])))

    return boxes[pick].astype("int")

def preprocess_image_for_ocr(image):
    
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Resize the image to double its original size
    image = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    
    # Apply thresholding to get a binary image
    _, image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    
    return image


def extract_text_from_roi(image, roi):
    x, y, w, h = roi
    roi_image = image[y:y+h, x:x+w]

    text = pytesseract.image_to_string(roi_image)
    
    return text.strip()

def visualize_roi(image, roi, title='Region of Interest'):
    x, y, w, h = roi
    roi_image = image[y:y+h, x:x+w]
    plt.imshow(cv2.cvtColor(roi_image, cv2.COLOR_BGR2RGB))
    plt.title(title)
    plt.show()


# Load the transparent PNG template
template_path = 'c:/BackpackDetection/LoreBookPatternTemplate.png'  # Replace with your template path
template = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)
if template is None:
    raise FileNotFoundError(f"Template file not found at path: {template_path}")

# Load the main image
image_path = 'c:/BackpackDetection/LoreBookTestPic.png'  # Replace with your image path
image = cv2.imread(image_path)
if image is None:
    raise FileNotFoundError(f"Image file not found at path: {image_path}")

# Perform template matching
rects = template_matching(image, template, threshold=0.8)

# Apply non-maximum suppression
nms_rects = non_max_suppression_fast(rects, overlapThresh=0.3)


x1,y1,x2,y2 = nms_rects[0]
image = image[y1:y2, x1:x2]


# Preprocess the image
preprocessed_image = preprocess_image_for_ocr(image)
# plt.imshow(cv2.cvtColor(preprocessed_image, cv2.COLOR_BGR2RGB))
# plt.title("ROI")
# plt.show()
# # Define ROIs for title and amounts
# title_roi = (42, 93, 175, 25)  # Adjusted for better title extraction
# amounts_roi_left = (223, 122, 20, 210)  # Adjusted left side amounts
# amounts_roi_right = (479, 122, 20, 110)  # Adjusted right side amounts
title_roi = (84, 186, 350, 50)  # Adjusted for better title extraction
amounts_roi_left = (446, 244, 40, 420)  # Adjusted left side amounts
amounts_roi_right = (958, 244, 40, 220)  # Adjusted right side amounts

# Visualize ROIs
visualize_roi(preprocessed_image, title_roi, title='Title ROI')
# visualize_roi(preprocessed_image, amounts_roi_left, title='Left Amounts ROI')
# visualize_roi(preprocessed_image, amounts_roi_right, title='Right Amounts ROI')

# Extract title
title = extract_text_from_roi(preprocessed_image, title_roi)

# Define more precise ROIs for amounts
amounts_rois = [
    (50, 150, 200, 30),  # Page 1
    (50, 180, 200, 30),  # Page 2
    (50, 210, 200, 30),  # Page 3
    # Add more ROIs as needed for each page
]

# Extract amounts from defined ROIs
amounts_dict = {}

for i, roi in enumerate(amounts_rois, start=1):
    text = extract_text_from_roi(preprocessed_image, roi)
    if text.isdigit():
        amounts_dict[f'Page {i}'] = int(text)

# Prepare the result dictionary
result = {
    'title': title,
    'amounts': amounts_dict
}

print(result)
