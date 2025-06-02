#!/bin/bash

echo "🔧 Fixing BGP Route Policies"
echo "============================"

# Function to enable route advertisements
enable_route_advertisements() {
    local as_name=$1
    local as_num=$2
    
    echo "Enabling route advertisements on $as_name..."
    
    docker exec -i "$as_name" vtysh << POLICY_FIX_EOF
configure terminal
router bgp $as_num
 no bgp ebgp-requires-policy
 
 address-family ipv4 unicast
  redistribute connected
 exit-address-family
 
end
write memory
clear ip bgp * soft
POLICY_FIX_EOF
}

# Remove BGP policies that are blocking route advertisements
echo "Removing restrictive BGP policies..."

enable_route_advertisements "as100" "65100"
enable_route_advertisements "as200" "65200"  
enable_route_advertisements "as300" "65300"
enable_route_advertisements "as400" "65400"
enable_route_advertisements "as500" "65500"

echo "⏳ Waiting 20 seconds for route exchange..."
sleep 20

echo "🔍 Checking route exchange..."
echo "AS200 should now see routes from neighbors:"
docker exec -t as200 vtysh -c "show ip bgp"

echo ""
echo "AS300 routes (should include 8.8.8.0/24):"
docker exec -t as300 vtysh -c "show ip bgp"

echo ""
echo "AS500 routes:"
docker exec -t as500 vtysh -c "show ip bgp"
