# Auditor Linux Integrity
## 1.0 Introduction
This script helps detect files or directories on your Linux system that may have been tampered with by an unauthorized actor.

The first time you run the script, it creates and enables a systemd service that starts automatically every time the system boots. During this setup, the script scans all executable binaries and kernel modules, calculates their SHA-256 hashes, and saves those hashes inside the script. These saved hashes serves as the trusted baseline for future integrity checks.

Each time the system starts, the systemd service runs the script automatically. The script calculates the SHA-256 hash of every monitored file and compares it with the saved reference hash. If the hashes are different, the script reports that the file has changed. It also checks for any new executable binaries or kernel modules that were not included in the original scan and reports them as newly added files.

## 2.0 Setup
1. Download the script and run it once to set up the required service and calculate the initial file hashes.
```shell
Pv0t[/Downloads]$ git clone https://github.com/Pv0t/auditor-linux-integrity.git
Pv0t[/Downloads]$ sudo mv auditor-linux-integrity/auditor.py /root/
Pv0t[/Downloads]$ sudo python3 /root/auditor.py
[*] Creating Auditor service.
Created symlink '/etc/systemd/system/multi-user.target.wants/auditor.service' → '/etc/systemd/system/auditor.service'.
[*] STARTING TO CHECK THE SYSTEM DRIVE DIRECTORY
[*] The system drive directory '/bin' exists.
[*] The system drive directory '/boot' exists.
[*] The system drive directory '/dev' exists.
[*] The system drive directory '/etc' exists.
[*] The system drive directory '/home' exists.
[*] The system drive directory '/lib' exists.
[*] The system drive directory '/lib64' exists.
[*] The system drive directory '/lost+found' exists.
[*] The system drive directory '/media' exists.
[*] The system drive directory '/mnt' exists.
[*] The system drive directory '/opt' exists.
[*] The system drive directory '/proc' exists.
[*] The system drive directory '/root' exists.
[*] The system drive directory '/run' exists.
[*] The system drive directory '/sbin' exists.
[*] The system drive directory '/srv' exists.
[*] The system drive directory '/sys' exists.
[*] The system drive directory '/tmp' exists.
[*] The system drive directory '/usr' exists.
[*] The system drive directory '/var' exists.
Scanned 1874 files
```

2. Ensure the systemd service of the script it is enabled correctly:
```shell
Pv0t[/]$ sudo systemctl status auditor.service
○ auditor.service - Start
     Loaded: loaded (/etc/systemd/system/auditor.service; enabled; preset: enabled)
     Active: inactive (dead)
```

## 3.0 Usage & Showcase
The script during the setup creates a systemd service that schedules the script to run every 4 hours and also triggers it on every system boot. This demonstration showcases the script’s normal‑run behavior during the system boot:
<img width="846" height="889" alt="1" src="https://github.com/user-attachments/assets/8dcc7b6d-7f8c-4a30-8535-1d6e480a0f56" />

When the script detects different hashes:
<img width="904" height="898" alt="2" src="https://github.com/user-attachments/assets/73a9c444-f55c-476b-93d4-52cfe1f88190" />


It is possible to run the script manually.
```
Pv0t[/]$ sudo python3 /root/auditor.py
[*] Linux Auditor service exists.
[*] STARTING TO CHECK THE SYSTEM DRIVE DIRECTORY
[*] The system drive directory '/bin' exists.
[*] The system drive directory '/boot' exists.
[..]
Scanned 6465 files
SYSTEM CLEAN
NO FILE TAMPERED DETECTED
```

----


