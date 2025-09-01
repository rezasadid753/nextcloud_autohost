import os, sys, time, platform, ctypes, traceback, subprocess, signal

try:
    import requests
except ImportError:
    requests = None

HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts" if platform.system() == "Windows" else "/etc/hosts"
TARGET_IP = "192.168.1.2"
DOMAIN = "yourdomain.com"
MARKER = "# NextCloud Autohost"

def is_admin():
    if platform.system() == "Windows":
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    else:
        return os.geteuid() == 0

def run_as_admin():
    if platform.system() == "Windows":
        try:
            exe = sys.executable
            if any(arg in sys.argv for arg in ["--install", "--uninstall"]):
                if exe.lower().endswith("pythonw.exe"):
                    exe = exe[:-5]  # pythonw.exe -> python.exe
            ctypes.windll.shell32.ShellExecuteW(None, "runas", exe, " ".join(sys.argv), None, 1)
            sys.exit(0)
        except Exception as e:
            print("[ERROR] Could not relaunch as admin:", e)
            input("Press Enter to exit...")
            sys.exit(1)
    else:
        print("[ERROR] Please run this script with sudo/root.")
        input("Press Enter to exit...")
        sys.exit(1)

def install_modules():
    global requests
    try:
        import pip
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'requests'])
        import requests
        print("[INFO] Required Python modules installed.")
    except Exception as e:
        print("[ERROR] Failed to install modules:", e)
        traceback.print_exc()
        input("Press Enter to exit...")
        sys.exit(1)

def check_nextcloud(ip):
    if requests is None:
        print("[WARNING] requests module not found, cannot check Nextcloud.")
        return False
    url = f"http://{ip}"
    try:
        r = requests.get(url, timeout=10, allow_redirects=True)
        if "nextcloud" in r.text.lower():
            return True
        return False
    except requests.exceptions.RequestException:
        return False

def update_hosts(enable):
    with open(HOSTS_PATH, "r") as f:
        lines = f.readlines()
    new_lines, found = [], False
    for line in lines:
        if DOMAIN in line and MARKER in line:
            found = True
            new_lines.append(f"{TARGET_IP}\t{DOMAIN} {MARKER}\n" if enable else f"# {TARGET_IP}\t{DOMAIN} {MARKER}\n")
        else:
            new_lines.append(line)
    if not found and enable:
        new_lines.append(f"{TARGET_IP}\t{DOMAIN} {MARKER}\n")
    with open(HOSTS_PATH, "w") as f:
        f.writelines(new_lines)

def install_autostart():
    install_modules()

    system = platform.system()
    script_path = os.path.abspath(sys.argv[0])
    try:
        if system == "Windows":
            startup = os.path.join(os.environ["APPDATA"], r"Microsoft\\Windows\\Start Menu\\Programs\\Startup")
            bat_path = os.path.join(startup, "nextcloud_autohost.bat")
            with open(bat_path, "w") as f:
                f.write(f'start /min pythonw "{script_path}"\n')
            print(f"[INFO] Installed autostart: {bat_path}")
            # Start immediately
            subprocess.Popen(['pythonw', script_path], shell=True)
            print("[INFO] nextcloud_autohost started immediately.")
        else:
            service = f"""\n[Unit]\nDescription=Nextcloud Autohost\n\n[Service]\nExecStart=/usr/bin/python3 {script_path}\nRestart=always\n\n[Install]\nWantedBy=multi-user.target\n"""
            svc_path = f"/etc/systemd/system/nextcloud_autohost.service"
            with open(svc_path, "w") as f:
                f.write(service)
            os.system("systemctl enable --now nextcloud_autohost")
            print(f"[INFO] Installed and started systemd service: {svc_path}")
    except Exception as e:
        print("[ERROR] Failed to install autostart:", e)
        traceback.print_exc()
        input("Press Enter to exit...")
        sys.exit(1)

def uninstall_autostart():
    system = platform.system()
    try:
        if system == "Windows":
            startup = os.path.join(os.environ["APPDATA"], r"Microsoft\\Windows\\Start Menu\\Programs\\Startup")
            bat_path = os.path.join(startup, "nextcloud_autohost.bat")
            if os.path.exists(bat_path):
                os.remove(bat_path)
                print(f"[INFO] Removed autostart: {bat_path}")
            else:
                print("[INFO] No autostart entry found.")
            print("[NOTICE] If nextcloud_autohost is still running, please restart your PC or close the python/pythonw process manually.")
        else:
            svc_path = f"/etc/systemd/system/nextcloud_autohost.service"
            os.system("systemctl disable --now nextcloud_autohost")
            if os.path.exists(svc_path):
                os.remove(svc_path)
                print(f"[INFO] Removed systemd service: {svc_path}")
            else:
                print("[INFO] No systemd service found.")
            print("[NOTICE] If nextcloud_autohost is still running, please reboot or kill the process manually.")
    except Exception as e:
        print("[ERROR] Failed to uninstall autostart:", e)
        traceback.print_exc()
        input("Press Enter to exit...")
        sys.exit(1)

def main_loop():
    while True:
        try:
            update_hosts(check_nextcloud(TARGET_IP))
        except Exception as e:
            print("[ERROR] Runtime failure:", e)
            traceback.print_exc()
            input("Press Enter to exit...")
            sys.exit(1)
        time.sleep(5)

if __name__ == "__main__":
    if not is_admin():
        run_as_admin()

    if len(sys.argv) > 1:
        if sys.argv[1] == "--install":
            install_autostart()
            input("Setup complete. Press Enter to exit...")
            sys.exit(0)
        elif sys.argv[1] == "--uninstall":
            uninstall_autostart()
            input("Uninstall complete. Press Enter to exit...")
            sys.exit(0)

    main_loop()
