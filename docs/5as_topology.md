# NetSecSim 5-AS BGP Topology

## Network Architecture

```
        AS100 (Tier-1 ISP)
        65100 | 100.0.0.0/16
              |
        AS200 (Regional ISP) ===== AS300 (Peer ISP)
        65200 | 200.0.0.0/16      65300 | 8.8.8.0/24
              |                         |
        AS400 (Customer)          AS500 (Attacker)
        65400 | 192.168.1.0/24    65500 | 172.16.0.0/16
```

## AS Details

| AS | ASN | Role | IP | Network | Description |
|----|-----|------|----|---------| ------------|
| AS100 | 65100 | Tier-1 ISP | 10.1.0.10 | 100.0.0.0/16 | Major Internet backbone |
| AS200 | 65200 | Regional ISP | 10.1.0.20 | 200.0.0.0/16 | Regional service provider |
| AS300 | 65300 | Peer ISP | 10.1.0.30 | 8.8.8.0/24 | Hosts Google DNS (target) |
| AS400 | 65400 | Customer | 10.1.0.40 | 192.168.1.0/24 | End customer network |
| AS500 | 65500 | Attacker | 10.1.0.50 | 172.16.0.0/16 | Malicious AS (attack source) |

## BGP Relationships

- **AS100 → AS200**: Provider-Customer (AS100 provides transit)
- **AS200 ↔ AS300**: Peer-to-Peer (settlement-free peering)
- **AS200 → AS400**: Provider-Customer (AS200 provides transit)
- **AS300 → AS500**: Provider-Customer (AS300 unknowingly hosts attacker)

## Attack Scenarios

### 1. Prefix Hijacking
- **Target**: AS500 hijacks 8.8.8.0/24 (Google DNS) from AS300
- **Impact**: DNS traffic gets misdirected to attacker
- **Command**: `python3 attack_simulator.py --attack prefix-hijack --attacker as500 --target 8.8.8.0/24`

### 2. Route Leak
- **Scenario**: AS400 leaks provider routes to AS200
- **Impact**: Breaks normal routing hierarchy
- **Command**: `python3 attack_simulator.py --attack route-leak --leaker as400`

### 3. AS Path Prepending
- **Scenario**: AS500 prepends AS path to manipulate traffic flow
- **Impact**: Forces traffic through specific paths
- **Command**: `python3 attack_simulator.py --attack path-prepend --attacker as500 --count 5`

### 4. BGP Blackholing
- **Scenario**: AS500 advertises /32 routes to blackhole specific IPs
- **Impact**: Makes specific services unreachable

## Container Commands

Start topology:
```bash
cd ~/NetSecSim/scripts
./setup-5as-topology.sh
```

Check BGP status:
```bash
docker exec -t as100 vtysh -c "show ip bgp summary"
docker exec -t as200 vtysh -c "show ip bgp"
```

Monitor routes:
```bash
docker exec -t as300 vtysh -c "show ip bgp neighbors"
```
