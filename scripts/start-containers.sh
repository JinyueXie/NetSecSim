#!/bin/bash

# Stop existing containers
docker stop as1 as2 2>/dev/null || true

# Start AS1 container
docker run -d --rm \
  --name as1 \
  --hostname as1 \
  --network bgp-net \
  --ip 10.1.0.2 \
  -v "$(pwd)/../core/routing_config/as1:/etc/frr" \
  --privileged \
  frrouting/frr:v8.4.0

# Start AS2 container  
docker run -d --rm \
  --name as2 \
  --hostname as2 \
  --network bgp-net \
  --ip 10.1.0.3 \
  -v "$(pwd)/../core/routing_config/as2:/etc/frr" \
  --privileged \
  frrouting/frr:v8.4.0

echo "Containers started. Waiting 10 seconds for BGP to initialize..."
sleep 10

# Add static routes that were working
docker exec -it as1 vtysh -c "configure terminal" -c "ip route 10.1.1.0/24 null0" -c "exit"
docker exec -it as2 vtysh -c "configure terminal" -c "ip route 10.1.2.0/24 null0" -c "exit"

# Add the route-maps that made it work
docker exec -it as1 vtysh -c "configure terminal" -c "route-map ACCEPT_ALL permit 10" -c "router bgp 65001" -c "neighbor 10.1.0.3 route-map ACCEPT_ALL in" -c "neighbor 10.1.0.3 route-map ACCEPT_ALL out" -c "end" -c "write"

docker exec -it as2 vtysh -c "configure terminal" -c "route-map ACCEPT_ALL permit 10" -c "router bgp 65002" -c "neighbor 10.1.0.2 route-map ACCEPT_ALL in" -c "neighbor 10.1.0.2 route-map ACCEPT_ALL out" -c "end" -c "write"

# Clear BGP to refresh
docker exec -it as1 vtysh -c "clear ip bgp *"
docker exec -it as2 vtysh -c "clear ip bgp *"

echo "BGP lab is ready!"
