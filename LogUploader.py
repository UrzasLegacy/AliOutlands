import requests
import os
import glob

def PostJournalLog():
    url = 'https://outlandmalls.com/uploads'
    headers = {'Authorization': '11111111-1111-1111-1111-111111111111'}
    data = {'tz': 'America/New_York'}
    file_path = get_most_recent_log()
    if not file_path:
        print("No accessible files found. Halting...")
        return
    with open(file_path, 'rb') as f:
        file = {'file': (file_path, f)}
        response = requests.post(url, headers=headers, files=file, data=data).status_code
        out_msg = ""
        match response:
            case 200:
                out_msg = "Upload Successful."
            case 401:
                out_msg = "Upload Failed. Unauthorized access, double check OutlandMalls API key."
            case 404:
                out_msg = "Upload Failed. Site not found, double check URL."
            case _:
                out_msg = f"Upload Failed. Google Error Code: {response}."
        print(f"Results: {out_msg}")

def get_most_recent_log():
    folder_path = "C:\\Program Files (x86)\\Ultima Online Outlands\\ClassicUO\\Data\\Client\\JournalLogs\\"
    files = [f for f in glob.glob(os.path.join(folder_path, '*.txt')) if os.path.isfile(f)]
    sorted_files = sorted(files, key=os.path.getmtime, reverse=True)
    latest_files = sorted_files[:6]
    accessible_files = [f for f in latest_files if check_accessibility(f)]
    try:
        latest_file = max(accessible_files, key=os.path.getmtime)
    except Exception as e:
        print(f"Unexpected error: {folder_path}: {str(e)}")
        return False
    print(f"Most recent accessible journal: {latest_file}")
    return latest_file

def check_accessibility(file_path):
    try:
        with open(file_path):
            pass
        return True    
    except IOError:
        print(f"File is in use: {file_path}")
        return False
    except Exception as e:
        print(f"Unexpected error when accessing {file_path}: {str(e)}")
        return False
    
PostJournalLog()