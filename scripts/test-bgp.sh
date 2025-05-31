#!/bin/bash

echo "=== BGP Route Tables ==="
echo "AS1 Routes:"
docker exec -it as1 vtysh -c "show ip bgp"
echo ""
echo "AS2 Routes:"  
docker exec -it as2 vtysh -c "show ip bgp"
echo ""

echo "=== BGP Summary ==="
echo "AS1 Summary:"
docker exec -it as1 vtysh -c "show ip bgp summary"
echo ""
echo "AS2 Summary:"
docker exec -it as2 vtysh -c "show ip bgp summary"
