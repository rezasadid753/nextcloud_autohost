# ☁️ Nextcloud Autohost (Windows & Linux)

Nextcloud Autohost is a lightweight Python script that automatically manages your system’s hosts file to give you the fastest possible connection to your self-hosted Nextcloud server — whether you’re at home on your LAN or away using your public domain.

> I originally wrote this script for my own home Nextcloud server running on a spare computer. I wanted to store my files locally but still make them accessible over the internet with my domain. The idea was simple: when I’m on my home Wi-Fi or LAN, I shouldn’t have to route traffic over the internet — I should connect directly to the local IP for speed.
>
> While I expected the Nextcloud client itself to have a feature like this, it doesn’t. So I built **Nextcloud Autohost** as a “set-and-forget” solution. It detects whether your Nextcloud instance is reachable locally and dynamically updates your hosts file to point your domain to your LAN IP. When you’re away, it disables the local entry so your domain resolves normally.

---

## 🛠️ Features

* ### Automatic Local Detection

  Periodically checks if your Nextcloud server is reachable at its local IP.

* ### Smart Hosts File Updates

  Adds or removes an entry for your domain in the system’s hosts file depending on availability.

* ### Cross-Platform

  Works on both **Windows** and **Linux**.

* ### Background Service

  Installs itself as a **Startup entry (Windows)** or **systemd service (Linux)** for continuous operation.

* ### Self-Installing

  Handles installation of required Python modules and sets up autostart automatically.

* ### Safe Uninstallation

  Removes autostart entries but leaves the current process alone — you can reboot or stop it manually when convenient.

---

## 📦 Installation

The script installs itself and required dependencies.

Before installing, **edit the script to set your own IP and domain**:

```python
TARGET_IP = "192.168.1.2"
DOMAIN = "yourdomain.com"
```

Run the installer:

```bash
python3 nextcloud_autohost.py --install
```

---

## 🖱️ Usage

Once installed, the script runs silently in the background, checking every 5 seconds whether your local Nextcloud is reachable.

* When reachable → your domain (e.g., `yourdomain.com`) is pointed to your local IP (e.g., `192.168.1.2`).
* When unreachable → the hosts entry is commented out, letting DNS resolve normally.

---

## 🧹 Uninstallation

To remove autostart entries and disable the service:

```bash
python3 nextcloud_autohost.py --uninstall
```

* On **Windows**, it deletes the Startup entry.
* On **Linux**, it disables and removes the systemd service.
* The running process is not killed — just reboot or stop it manually.

---

## 🧬 How It Works

Nextcloud Autohost is based on a few simple components:

* ### Connectivity Check

  Uses the Python `requests` module to send an HTTP request to your local Nextcloud server and confirm if it’s accessible.

* ### Hosts File Management

  Dynamically writes or comments out a line in your hosts file:

  ```
  192.168.1.2   yourdomain.com   # NextCloud Autohost
  ```

* ### Background Service

  * **Windows:** Creates a `.bat` file in the Startup folder that runs the script with `pythonw`.
  * **Linux:** Creates a systemd service unit that runs continuously and restarts automatically if it fails.

* ### Self-Installing

  If `requests` isn’t installed, the script installs it automatically using `pip`.

---

## ⚠️ Notes

* Requires admin/root privileges to edit the system hosts file.
* You should replace the `DOMAIN` and `TARGET_IP` constants in the script with your own setup before use.
* Meant for home/self-hosted servers — not suitable for multi-user or enterprise environments.

---


## 📜 License

This project is licensed under the MIT License — feel free to use, modify, and distribute it as you like.

---

## 🤝 Acknowledgements

[Nextcloud](https://github.com/nextcloud) — for creating the powerful self-hosted cloud platform that inspired this little helper script to make using it at home even smoother.
