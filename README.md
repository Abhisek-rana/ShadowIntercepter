# ShadowIntercepter

A Burp Suite–inspired HTTP/HTTPS intercepting proxy built from scratch in Python, for web application penetration testing and traffic analysis.

![Python](https://img.shields.io/badge/Python-3.11+-blue) ![PyQt6](https://img.shields.io/badge/GUI-PyQt6-green) ![Platform](https://img.shields.io/badge/Platform-Kali%20Linux%20%7C%20Windows-lightgrey)

## Overview

ShadowIntercepter is a manual web security testing toolkit that sits between a browser and the target application as a man-in-the-middle (MITM) proxy. It intercepts, inspects, and modifies HTTP and HTTPS traffic in real time, and includes a request-replay tool and a multi-mode brute-force/fuzzing engine — the core toolkit a penetration tester reaches for during manual web app testing.

Built to understand *how* tools like Burp Suite work under the hood: raw TCP sockets, HTTP parsing, TLS interception with a self-signed CA, and a multi-threaded proxy engine, wrapped in a custom desktop GUI.

## Features

- **HTTP & HTTPS Interception** — full MITM proxy with dynamic per-domain certificate generation from a self-signed root CA
- **Request/Response Interception** — pause, inspect, and edit live traffic before it reaches the browser or server, with independent toggles for requests and responses
- **Smart Filtering** — automatically skips static assets (CSS/JS/images/fonts) during interception so normal browsing isn't blocked
- **HTTP History** — full log of every request/response with headers and body, viewable and searchable
- **Site Map** — auto-generated tree view of every host and endpoint discovered during a session
- **Repeater** — resend and manually edit any captured request, with live response
- **Bruteforce / Fuzzing Engine** — Intruder-style attacks with 4 modes:
  - **Sniper** — one payload set, one position at a time
  - **Battering Ram** — same payload in all positions simultaneously
  - **Pitchfork** — parallel payload sets across positions
  - **Cluster Bomb** — full cartesian combination of payload sets
- **Send to Repeater / Send to Bruteforce** — pivot any request from History or Intercept straight into other tools, Burp-style
- **Dashboard** — live view of proxy status, intercept state, and total requests captured

## Screenshots

*(Add these before publishing — see checklist below)*

## Tech Stack

- **Python 3** — core proxy engine, raw `socket` + `ssl`
- **PyQt6** — desktop GUI
- **`cryptography`** — CA and per-domain certificate generation for TLS interception
- Multi-threaded architecture — GUI and proxy engine run concurrently; intercept hold/release implemented with `threading.Event`

## Project Structure

```
ShadowIntercepter/
├── src/
│   ├── proxy/         # Core TCP/TLS proxy engine, HTTP parsing, SSL/CA handling
│   ├── intercept/      # Request/response hold-and-release logic
│   ├── history/         # Traffic logging
│   ├── sitemap/         # Site map builder
│   ├── bruteforce/     # Attack engine (Sniper/Battering Ram/Pitchfork/Cluster Bomb)
│   └── gui/                # PyQt6 interface (Dashboard, Proxy, Repeater, Site Map, Bruteforce)
├── certs/                 # Generated CA + per-domain certs (gitignored)
├── main.py
└── requirements.txt
```

## Installation

```bash
git clone https://github.com/Abhisek-rana/ShadowIntercepter.git
cd ShadowIntercepter
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

1. Start the application:
```bash
   python3 -m src.gui.main_window
```
   This automatically generates a unique CA certificate (`certs/ca.crt`) on first run and starts the proxy on `127.0.0.1:8080`.

2. **Configure your browser to use the proxy** (example with Firefox + FoxyProxy):
   - Install the [FoxyProxy Standard](https://addons.mozilla.org/en-US/firefox/addon/foxyproxy-standard/) extension
   - Add a new proxy: Host `127.0.0.1`, Port `8080`, Type `HTTP`
   - Enable it ("Use proxy 127.0.0.1:8080" from the FoxyProxy menu)

3. **Install the CA certificate so HTTPS interception works without browser warnings:**
   - In Firefox, go to `about:preferences#privacy`
   - Scroll down to **Certificates** → click **View Certificates**
   - Go to the **Authorities** tab → click **Import**
   - Select `certs/ca.crt` from your project folder
   - Check **"Trust this CA to identify websites"** → click **OK**

4. Browse normally — traffic will now flow through ShadowIntercepter:
   - **Proxy → Intercept**: toggle "Intercept Requests" / "Intercept Responses" independently to pause and edit live traffic before it's forwarded
   - **Proxy → HTTP History**: review every captured request/response
   - **Repeater**: resend and edit any request, or send one directly from History/Intercept
   - **Site Map**: see every host/endpoint discovered in the session
   - **Bruteforce**: mark request positions with `§...§` and run Sniper / Battering Ram / Pitchfork / Cluster Bomb attacks

   > Static assets (CSS/JS/images/fonts) are automatically skipped during interception so normal browsing isn't blocked — same behavior as Burp Suite's default scope filtering.

This tool is built for educational purposes and authorized security testing only (e.g. personal lab environments, PortSwigger Web Security Academy, or systems you have explicit permission to test). Do not use it against systems you do not own or lack authorization to test.

## Roadmap

- Intercept scope/filter rules (custom include/exclude patterns)
- WebSocket traffic support
- Export findings as a report

## Author

Built by [Abhisek Rana] — Cybersecurity Trainer, working toward Offensive Security / VAPT roles.
