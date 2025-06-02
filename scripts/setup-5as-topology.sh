#!/bin/bash

echo "🚀 Setting up 5-AS BGP Topology for Attack Simulation"
echo "====================================================="

# AS Configuration - Using 172.20.0.x to avoid conflicts
declare -A AS_CONFIG=(
    ["as100"]="65100 172.20.0.10 Tier1-ISP 100.0.0.0/16"
    ["as200"]="65200 172.20.0.20 Regional-ISP 200.0.0.0/16"  
    ["as300"]="65300 172.20.0.30 Peer-ISP 8.8.8.0/24"
    ["as400"]="65400 172.20.0.40 Customer 192.168.1.0/24"
    ["as500"]="65500 172.20.0.50 Attacker 172.16.0.0/16"
)

BGP_SESSIONS=(
    "as100:as200"
    "as200:as300"
    "as200:as400"
    "as300:as500"
)

cleanup_existing() {
    echo "🧹 Cleaning up..."
    docker stop as100 as200 as300 as400 as500 2>/dev/null || true
    docker rm as100 as200 as300 as400 as500 2>/dev/null || true
    docker network rm bgp-sim 2>/dev/null || true
    echo "✓ Cleanup completed"
}

create_network() {
    echo "🌐 Creating network..."
    docker network create --driver bridge --subnet=172.20.0.0/16 --gateway=172.20.0.1 bgp-sim
    echo "✓ Network created"
}

generate_configs() {
    echo "📝 Generating configs..."
    mkdir -p ../core/routing_config
    
    for as_name in "${!AS_CONFIG[@]}"; do
        IFS=' ' read -r asn ip role network <<< "${AS_CONFIG[$as_name]}"
        echo "  Configuring $as_name (AS$asn)"
        
        mkdir -p "../core/routing_config/$as_name"
        
        cat > "../core/routing_config/$as_name/daemons" << 'DAEMONS_END'
bgpd=yes
zebra_options="  -A 127.0.0.1 -s 90000000"
bgpd_options="   -A 127.0.0.1"
vtysh_enable=yes
DAEMONS_END

        cat > "../core/routing_config/$as_name/zebra.conf" << ZEBRA_END
hostname $as_name
line vty
ZEBRA_END

        cat > "../core/routing_config/$as_name/bgpd.conf" << BGP_END
hostname $as_name-bgp
router bgp $asn
 bgp router-id $ip
 network $network
line vty
BGP_END
    done
    echo "✓ Configs generated"
}

start_containers() {
    echo "🐳 Starting containers..."
    
    for as_name in "${!AS_CONFIG[@]}"; do
        IFS=' ' read -r asn ip role network <<< "${AS_CONFIG[$as_name]}"
        echo "  Starting $as_name at $ip"
        
        docker run -d --rm \
            --name "$as_name" \
            --hostname "$as_name" \
            --network bgp-sim \
            --ip "$ip" \
            -v "$(pwd)/../core/routing_config/$as_name:/etc/frr" \
            --privileged \
            frrouting/frr:v8.4.0
    done
    
    echo "⏳ Waiting 15 seconds..."
    sleep 15
}

configure_routes() {
    echo "🛣️  Adding static routes..."
    
    for as_name in "${!AS_CONFIG[@]}"; do
        IFS=' ' read -r asn ip role network <<< "${AS_CONFIG[$as_name]}"
        docker exec -i "$as_name" vtysh -c "configure terminal" -c "ip route $network null0" -c "exit"
    done
    echo "✓ Routes configured"
}

configure_bgp() {
    echo "🔗 Configuring BGP..."
    
    # AS100 <-> AS200
    docker exec -i as100 vtysh -c "configure terminal" -c "router bgp 65100" -c "neighbor 172.20.0.20 remote-as 65200" -c "exit" -c "write"
    docker exec -i as200 vtysh -c "configure terminal" -c "router bgp 65200" -c "neighbor 172.20.0.10 remote-as 65100" -c "exit" -c "write"
    
    # AS200 <-> AS300
    docker exec -i as200 vtysh -c "configure terminal" -c "router bgp 65200" -c "neighbor 172.20.0.30 remote-as 65300" -c "exit" -c "write"
    docker exec -i as300 vtysh -c "configure terminal" -c "router bgp 65300" -c "neighbor 172.20.0.20 remote-as 65200" -c "exit" -c "write"
    
    # AS200 <-> AS400
    docker exec -i as200 vtysh -c "configure terminal" -c "router bgp 65200" -c "neighbor 172.20.0.40 remote-as 65400" -c "exit" -c "write"
    docker exec -i as400 vtysh -c "configure terminal" -c "router bgp 65400" -c "neighbor 172.20.0.20 remote-as 65200" -c "exit" -c "write"
    
    # AS300 <-> AS500
    docker exec -i as300 vtysh -c "configure terminal" -c "router bgp 65300" -c "neighbor 172.20.0.50 remote-as 65500" -c "exit" -c "write"
    docker exec -i as500 vtysh -c "configure terminal" -c "router bgp 65500" -c "neighbor 172.20.0.30 remote-as 65300" -c "exit" -c "write"
    
    echo "⏳ Waiting for BGP convergence..."
    sleep 20
}

verify_topology() {
    echo "🔍 Verifying topology..."
    
    for as_name in as100 as200 as300 as400 as500; do
        echo "=== $as_name ==="
        docker exec -t "$as_name" vtysh -c "show ip bgp summary" 2>/dev/null | grep -E "(Neighbor|Established|State)" || echo "BGP not ready"
    done
    
    echo "✅ Setup complete!"
}

main() {
    cleanup_existing
    create_network
    generate_configs
    start_containers
    configure_routes
    configure_bgp
    verify_topology
    
    echo ""
    echo "🎉 5-AS BGP Topology Ready!"
    echo "Test with: docker exec -t as100 vtysh -c 'show ip bgp'"
}

main "$@"
