#!/bin/bash
# Quick topology status checker

echo "NetSecSim 5-AS Topology Status"
echo "=============================="

containers=("as100" "as200" "as300" "as400" "as500")

for container in "${containers[@]}"; do
    if docker ps --filter "name=$container" --format "{{.Names}}" | grep -q "$container"; then
        echo "✓ $container: Running"
        
        # Quick BGP check
        neighbors=$(docker exec -t $container vtysh -c "show ip bgp summary" 2>/dev/null | grep -c "Established" || echo "0")
        routes=$(docker exec -t $container vtysh -c "show ip bgp" 2>/dev/null | grep -c "^\*" || echo "0")
        
        echo "    BGP neighbors: $neighbors established"
        echo "    BGP routes: $routes learned"
    else
        echo "✗ $container: Not running"
    fi
    echo ""
done
