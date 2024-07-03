#import cv2
import numpy as np
#import matplotlib.pyplot as plt

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

# Draw rectangles around detected backpacks
for (startX, startY, endX, endY) in nms_rects:
    cv2.rectangle(image, (startX, startY), (endX, endY), (0, 255, 0), 2)

# Display the detected backpacks
plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
plt.title('Detected Backpacks')
plt.show()

# Define a function to process each detected ROI
def process_roi(image, roi):
    x1, y1, x2, y2 = roi
    roi_image = image[y1:y2, x1:x2]
    hsv_roi = cv2.cvtColor(roi_image, cv2.COLOR_BGR2HSV)

    # Define color ranges for different items (these ranges need to be adjusted based on actual item colors)
    color_ranges = {
        'potion': ([0, 50, 50], [10, 255, 255]),  # Example range for red items
        'gold': ([20, 100, 100], [30, 255, 255]),  # Example range for yellow items
        'gem': ([110, 50, 50], [130, 255, 255])   # Example range for blue items
    }

    item_counts = {}
    for item, (lower, upper) in color_ranges.items():
        lower = np.array(lower, dtype="uint8")
        upper = np.array(upper, dtype="uint8")
        mask = cv2.inRange(hsv_roi, lower, upper)
        
        # Apply morphological operations
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Count items based on contours
        item_counts[item] = len(contours)
        
        # Draw contours on the ROI image for visualization
        cv2.drawContours(roi_image, contours, -1, (0, 255, 0), 2)
    
    return item_counts, roi_image

# Process each detected ROI
all_item_counts = []
for i, roi in enumerate(nms_rects):
    item_counts, roi_image = process_roi(image, roi)
    all_item_counts.append(item_counts)
    print(f'Backpack {i+1} item counts: {item_counts}')

    # Display results
    plt.figure(figsize=(10, 10))
    plt.imshow(cv2.cvtColor(roi_image, cv2.COLOR_BGR2RGB))
    plt.title(f'Backpack {i+1}: Items Detected')
    plt.show()

print("All item counts:", all_item_counts)
