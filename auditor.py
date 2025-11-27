#!/usr/bin/env python3

import hashlib
import os
import sys
from pathlib import Path
from datetime import datetime
import time

SYSTEM_DRIVE_CHECK = [
    Path("/bin"),
    Path("/boot"),
    Path("/dev"),
    Path("/etc"),
    #Path("/home"),
    Path("/lib"),
    Path("/lib64"),
    Path("/lost+found"),
    Path("/media"),
    Path("/mnt"),
    Path("/opt"),
    Path("/proc"),
    Path("/root"),
    Path("/run"),
    Path("/sbin"),
    Path("/srv"),
    Path("/sys"),
    Path("/tmp"),
    Path("/usr"),
    Path("/var"),
]

PATHS_TO_CHECK = [
    Path("/lib/modules") / os.uname().release / "kernel",
    Path("/bin"),
    Path("/sbin"),
]

SCRIPT = Path(__file__)
START_MARKER = "# [TRUSTED HASHES] #"
END_MARKER   = "# [TRUSTED HASHES END] #"  

def service():
    start_service = "[Unit]\nDescription=Start\nBefore=display-manager.service\nBefore=lightdm.service\nBefore=graphical.target\nAfter=local-fs.target\n\n[Service]\nExecStart=python3 /root/auditor.py\nType=oneshot\nRemainAfterExit=yes\nStandardOutput=tty\nStandardError=tty\nStandardInput=tty\nTTYPath=/dev/tty1\nTimeoutSec=0\n\n[Install]\nWantedBy=multi-user.target"
    login_auditor_service = '/etc/systemd/system/login-auditor.service'
    if os.path.exists(login_auditor_service):
        print("[*]Login auditor service exists.")
        os.system("systemctl enable login-auditor")
    else:
        with open (login_auditor_service, 'w') as file_object:
            print("[*]Creating the login auditor service.")
            file_object.write(start_service)
            os.system("systemctl enable login-auditor")

def is_relevant(f):
    return f.suffix == ".ko" or f.parent in (Path("/bin"), Path("/sbin"))

def sha256(file):
    try:
        return hashlib.sha256(file.read_bytes()).hexdigest()
    except:
        return None

def load_trusted():
    text = SCRIPT.read_text(encoding="utf-8")
    start = text.rfind(START_MARKER)
    if start == -1:
        return {}
    end = text.find(END_MARKER, start + len(START_MARKER))
    if end == -1:
        return {}
    block = text[start + len(START_MARKER):end]
    trusted = {}
    for line in block.splitlines():
        line = line.strip()
        if line and "  " in line:
            h, p = line.split("  ", 1)
            trusted[p.strip()] = h.strip()
    return trusted

def save_trusted(trusted):
    lines = [f"{h}  {p}\n" for p, h in sorted(trusted.items())]
    text = SCRIPT.read_text(encoding="utf-8")
    start = text.rfind(START_MARKER)
    if start == -1:
        before = text
        after = ""
    else:
        end = text.find(END_MARKER, start + len(START_MARKER))
        if end == -1:
            before = text[:start]
            after = ""
        else:
            before = text[:start]
            after = text[end + len(END_MARKER):]
    new_block = START_MARKER + "\n" + \
                f"# Last time the list of hashes got updated: {datetime.now().isoformat()}\n" + \
                "".join(lines) + \
                END_MARKER + "\n"
    SCRIPT.write_text(before + new_block + after, encoding="utf-8")

def menu(file, old, new):
    while True:
        print("[!] POSSIBLE FILE TAMPERED [!]")
        print(f"[*] File : {file}")
        print(f"[*] Old hash  : {old or '(none)'}")
        print(f"[*] New hash  : {new}")
        print(" ")
        print("1] I trust this hash.")
        print("2] Trust ALL the modified hash.")
        print("3] Quit")
        choice = input("\nChoice [1-3]: ").strip()
        if choice == "1": return "this"
        if choice == "2": return "all"
        if choice in ("3", "q", "quit", "exit"): sys.exit("Bye")

def main():
    print('\n' * 50)
    if os.geteuid() != 0:
        sys.exit("Run with sudo!")
    service()
    current = {}
    print("STARTING TO CHECK THE SYSTEM DRIVE DIRECTORY")
    for drive in SYSTEM_DRIVE_CHECK:
      if os.path.exists(drive):
        print(f"[*] The system drive directory '{drive}' exists.")
      else:
        print(f"[!] The system drive directory '{drive}' does not exists.")
        print("1] Continue. ")
        print("2] Quit. ")
        system_drive_choice = input("\nChoice [1-2]: ").strip()
        if system_drive_choice == "1": continue
        if system_drive_choice in ("2", "q", "quit", "exit"): sys.exit("Bye")

    for base in PATHS_TO_CHECK:
        if base.exists():
            for f in base.rglob("*"):
                if f.is_file() and is_relevant(f):
                    h = sha256(f)
                    if h:
                        current[str(f)] = h
    print(f"Scanned {len(current)} files")  
    trusted = load_trusted()
    if not trusted:
        if os.getcwd() != '/root':
            print("[!] These script needs to be run on the '/root/' directory.")
            sys.exit("Bye")
        print("\nFirst run: Scanning and loading all the hash.")
        save_trusted(current)
        return

    trust_all = False
    changed = False

    for path, new_h in current.items():
        old_h = trusted.get(path)
        if old_h == new_h:
            continue
        if trust_all:
            trusted[path] = new_h
            changed = True
            continue

        decision = menu(path, old_h, new_h)
        if decision == "all":
            trust_all = True
        trusted[path] = new_h
        changed = True

    if changed:
        save_trusted(trusted)
        print("\nScript updated.")

    print("SYSTEM CLEAN\nNO FILE TAMPERED DETECTED")
    time.sleep(15)
    print('\n' * 50)

if __name__ == "__main__":
    main()

"""
# [TRUSTED HASHES] #
# [TRUSTED HASHES END] #
"""
