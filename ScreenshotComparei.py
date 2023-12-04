import pyautogui
import numpy as np
import time
import socket
import threading

def detect_notification():
    def images_are_equal(img1, img2):
        arr1 = np.array(img1)
        arr2 = np.array(img2)
        return np.array_equal(arr1, arr2)
    def send_udp_message(message, target_ip, target_port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(message.encode(), (target_ip, target_port))
    x, y, width, height = 715, 1150, 782, 135  # Update these values
    time_stamp = time.time()
    initial_screenshot = pyautogui.screenshot(region=(x, y, width, height))
    while True:
        new_screenshot = pyautogui.screenshot(region=(x, y, width, height))
        if time.time() > time_stamp and not images_are_equal(new_screenshot, initial_screenshot):
            time_stamp = time.time() + 5
            send_udp_message("Triggered", "10.0.0.61", 8080)  # Update IP and port
        initial_screenshot = new_screenshot
        time.sleep(0.2)

def udp_daemon(port=8080):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', port))
    while True:
        data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        print("Received message:", data.decode())

def summon_udp_daemon():
    monitor_thread = threading.Thread(target=udp_daemon)
    monitor_thread.start()

summon_udp_daemon()