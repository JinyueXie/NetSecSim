# 🧠 NetSecSim — Network Security Simulation Platform

NetSecSim is a **system-level security experimentation platform** designed to simulate communication protocol behaviors (OSPF/BGP) and various attack scenarios (e.g., prefix hijack, AS path poisoning) within virtualized multi-AS networks. It serves as an ideal environment for **network protocol learning**, **routing security analysis**, and **eBPF-based system monitoring**, making it invaluable for system security education and research.

---

## 🌐 Capabilities

NetSecSim empowers users to:

* Deploy multiple Autonomous Systems (AS) using **Docker** and **FRRouting**.
* Configure **OSPF/BGP protocols** with custom filters and route maps to define routing policies.
* Simulate **routing attacks** such as prefix hijacks and AS path manipulations.
* Monitor system and network behavior with **eBPF / bpftrace**.
* Visualize network topology and attack propagation using **Graphviz**.

---

## 🚀 Motivation

### 🛡 Real-World Security Impact

The internet's backbone, built upon routing protocols, remains vulnerable to sophisticated attacks. Real-world BGP hijacks have demonstrated significant global outages and financial losses:

* **YouTube** was briefly inaccessible worldwide due to a BGP hijack by a Pakistani ISP in 2008.
* **Amazon's DNS service** was hijacked, leading to cryptocurrency theft.
* Major internet entities like **Cloudflare, Google, and Facebook** actively monitor BGP security to mitigate such threats.

While traditional cybersecurity often focuses on application layers, firewalls, and malware, NetSecSim targets the foundational routing layer, enabling deep dives into its vulnerabilities.

### 🎓 Educational & Research Value

NetSecSim offers immense value for both education and research by:

* Fostering a deep understanding of **OSPF & BGP** through hands-on configuration.
* Training **protocol-level security thinking** to identify and counter routing vulnerabilities.
* Developing practical skills with modern tools like **eBPF**, **Docker**, and **network topology** visualization.

This project bridges theoretical network knowledge with practical engineering and cutting-edge security research, particularly beneficial for individuals transitioning into infrastructure security.

---

## 📦 Project Modules

| Module                    | Technology Used                          | Purpose                                   |
| :------------------------ | :--------------------------------------- | :---------------------------------------- |
| Virtual Network Setup     | Docker + FRRouting                       | Simulate AS-level topology                |
| Routing Protocol Config   | OSPF + BGP + route maps                  | Explore BGP filtering, policy design      |
| Attack Injection          | Config rewrite + hijack scripts          | Simulate real-world attacks               |
| System Behavior Auditing  | bpftrace / Falco                         | Trace syscall-level actions               |
| Visualization             | Python + Graphviz                        | Topology & attack flow illustration       |
| Monitoring & Alerts       | Bash + Python + log parsing              | Automatic detection & alerting            |

---

## ⚙️ How to Use

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/JinyueXie/NetSecSim
```

### 2️⃣ Start the Network Lab (2 AS example)
This command spins up containers for as1 and as2, each configured with FRRouting, preconfigured BGP/OSPF neighbors, and unique IPs and AS numbers.

```bash
docker compose up -d
```

### 3️⃣ Check BGP Status
Verify that the BGP peering sessions are established between the Autonomous Systems.

```bash
docker exec -it as1 vtysh -c "show ip bgp summary"
docker exec -it as2 vtysh -c "show ip bgp summary"
```

### 4️⃣ View Routing Table & Test Connectivity
Observe the learned prefixes between AS nodes and confirm inter-AS routing functionality.

```bash
docker exec -it as1 vtysh -c "show ip bgp"
docker exec -it as2 vtysh -c "show ip bgp"
```

You can also test basic connectivity:

```bash
docker exec as1 ping 10.1.0.3
docker exec as2 traceroute 10.1.0.2
```

---

## 🖥️ Enhanced Dashboard UI (v2.0)

A modern PyQt6-powered visual interface is now included to simulate attacks and observe real-time network behavior.

### Features

- 📊 Live visualization of AS-level network topology
- 🟢 Status indicators for each AS (online / attack)
- ⚔️ One-click Prefix Hijack and Route Poisoning simulation
- 📜 Attack log viewer
- 🖼️ Custom icon and Ubuntu launcher integration

### How to Launch

```bash
cd ~/NetSecSim
source venv/bin/activate
./launch-netsec-enhanced.sh
```
