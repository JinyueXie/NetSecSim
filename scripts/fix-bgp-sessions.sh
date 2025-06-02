#!/bin/bash

echo "🔧 Fixing BGP Session Establishment"
echo "=================================="

# Function to configure BGP sessions properly
configure_bgp_session() {
    local as1=$1
    local as2=$2
    local as1_ip=$3
    local as2_ip=$4
    local as1_num=$5
    local as2_num=$6
    
    echo "Configuring BGP session: $as1 ($as1_ip) <-> $as2 ($as2_ip)"
    
    # Configure AS1 side
    docker exec -i "$as1" vtysh << BGP1_EOF
configure terminal
router bgp $as1_num
 neighbor $as2_ip remote-as $as2_num
 neighbor $as2_ip description $as2
 address-family ipv4 unicast
  neighbor $as2_ip activate
 exit-address-family
end
write memory
BGP1_EOF

    # Configure AS2 side
    docker exec -i "$as2" vtysh << BGP2_EOF
configure terminal
router bgp $as2_num
 neighbor $as1_ip remote-as $as1_num
 neighbor $as1_ip description $as1
 address-family ipv4 unicast
  neighbor $as1_ip activate
 exit-address-family
end
write memory
BGP2_EOF
}

# Configure all BGP sessions
echo "Setting up BGP peering sessions..."

# AS100 <-> AS200 (Provider-Customer)
configure_bgp_session "as100" "as200" "172.20.0.10" "172.20.0.20" "65100" "65200"

# AS200 <-> AS300 (Peer-Peer)
configure_bgp_session "as200" "as300" "172.20.0.20" "172.20.0.30" "65200" "65300"

# AS200 <-> AS400 (Provider-Customer)
configure_bgp_session "as200" "as400" "172.20.0.20" "172.20.0.40" "65200" "65400"

# AS300 <-> AS500 (Provider-Customer)
configure_bgp_session "as300" "as500" "172.20.0.30" "172.20.0.50" "65300" "65500"

echo "⏳ Waiting 30 seconds for BGP sessions to establish..."
sleep 30

echo "🔍 Checking BGP session status..."
for as_name in as100 as200 as300 as400 as500; do
    echo "=== $as_name BGP Neighbors ==="
    docker exec -t "$as_name" vtysh -c "show ip bgp summary" | grep -E "(Neighbor|Established|172\.20\.0)" | head -5
    echo ""
done

echo "✅ BGP sessions should now be established!"
echo ""
echo "Test the topology:"
echo "  docker exec -t as200 vtysh -c 'show ip bgp'"
echo "  python3 working_attack_simulator.py"
