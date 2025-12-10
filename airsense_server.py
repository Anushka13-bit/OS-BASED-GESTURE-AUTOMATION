import socket
import threading
import pyautogui
import subprocess
import time
import os

# ---------------- TCP SERVER CONFIG ----------------
HOST = "0.0.0.0"          # Listen for any client
PORT = 5005               # Must match Computer A

print(f"Starting TCP server on port {PORT}...")
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)

print("Waiting for connection from Computer A...")
client, addr = server.accept()
print("Connected to:", addr)


# ---------------- COMMAND EXECUTION ----------------

def execute_command(cmd):
    """Executes high-level commands received from Computer A"""

    parts = cmd.strip().split()

    if not parts:
        return

    # ------------------------------------------------
    # 1. MOVE command
    # Format: MOVE x y
    # ------------------------------------------------
    if parts[0] == "MOVE" and len(parts) == 3:
        try:
            x = int(parts[1])
            y = int(parts[2])
            pyautogui.moveTo(x, y)
        except:
            print("Invalid MOVE coordinates")
        return

    # ------------------------------------------------
    # 2. CLICK
    # ------------------------------------------------
    if parts[0] == "CLICK":
        pyautogui.click()
        return

    # ------------------------------------------------
    # 3. RIGHTCLICK
    # ------------------------------------------------
    if parts[0] == "RIGHTCLICK":
        pyautogui.rightClick()
        return

    # ------------------------------------------------
    # 4. DOUBLECLICK
    # ------------------------------------------------
    if parts[0] == "DOUBLECLICK":
        pyautogui.doubleClick()
        return

    # ------------------------------------------------
    # 5. SCROLL amount
    # Example: SCROLL -200 (down), SCROLL 200 (up)
    # ------------------------------------------------
    if parts[0] == "SCROLL" and len(parts) == 2:
        try:
            amount = int(parts[1])
            pyautogui.scroll(amount)
        except:
            print("Invalid SCROLL amount")
        return

    # ------------------------------------------------
    # 6. DRAG x y
    # ------------------------------------------------
    if parts[0] == "DRAG" and len(parts) == 3:
        try:
            x = int(parts[1])
            y = int(parts[2])
            pyautogui.dragTo(x, y, duration=0.1)
        except:
            print("Invalid DRAG command")
        return

    # ------------------------------------------------
    # 7. TYPE text...
    # ------------------------------------------------
    if parts[0] == "TYPE":
        text = " ".join(parts[1:])
        pyautogui.typewrite(text)
        return

    # ------------------------------------------------
    # 8. OPEN appname
    # ------------------------------------------------
    if parts[0] == "OPEN":
        app = parts[1].lower()

        if app == "chrome":
            if os.name == "nt":
                subprocess.Popen(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
            else:
                subprocess.Popen(["open", "-a", "Google Chrome"])
        elif app == "notepad":
            subprocess.Popen("notepad.exe")
        else:
            print("Unknown app:", app)
        return

    # ------------------------------------------------
    # 9. SCREENSHOT
    # ------------------------------------------------
    if parts[0] == "SCREENSHOT":
        filename = "remote_ss_" + str(int(time.time())) + ".png"
        pyautogui.screenshot(filename)
        print("Saved screenshot:", filename)
        return

    print("Unknown command:", cmd)


# ---------------- RECEIVE LOOP ----------------
def client_listener():
    while True:
        try:
            data = client.recv(1024).decode()
            if not data:
                break

            print("Received:", data)
            execute_command(data)

        except Exception as e:
            print("Error:", e)
            break


listener_thread = threading.Thread(target=client_listener)
listener_thread.start()
listener_thread.join()