import pyperclip
def append_recall_home_script():
    try:
        current_content = pyperclip.paste()
        print(current_content)
        append_string = """

    wait 1000
    script "AliRoom"
    """
        new_content = current_content + append_string
        pyperclip.copy(new_content)
    except Exception as e:
        print(f"Err: {e}")

append_recall_home_script()