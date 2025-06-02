#!/bin/bash

echo "🚀 NetSecSim Fixed 5-AS BGP Topology"
echo "=================================="

cleanup() {
    docker stop as100 as200 as300 as400 as500 2>/dev/null || true
    docker rm as100 as200 as300 as400 as500 2>/dev/null || true
}

create_configs() {
    echo "📝 Creating FRR configurations..."
    mkdir -p ../core/routing_config
    
    # AS100 Configuration
    mkdir -p ../core/routing_config/as100
    cat > ../core/routing_config/as100/daemons << 'AS100_DAEMONS'
bgpd=yes
zebra=yes
vtysh_enable=yes
zebra_options="  -A 127.0.0.1 -s 90000000"
bgpd_options="   -A 127.0.0.1"
AS100_DAEMONS

    cat > ../core/routing_config/as100/vtysh.conf << 'AS100_VTYSH'
service integrated-vtysh-config
AS100_VTYSH

    cat > ../core/routing_config/as100/frr.conf << 'AS100_FRR'
frr version 8.4_git
frr defaults traditional
hostname as100
service integrated-vtysh-config

ip route 100.0.0.0/16 null0

router bgp 65100
 bgp router-id 172.20.0.10
 bgp log-neighbor-changes
 network 100.0.0.0/16
 neighbor 172.20.0.20 remote-as 65200
 neighbor 172.20.0.20 description as200

line vty
AS100_FRR

    # AS200 Configuration  
    mkdir -p ../core/routing_config/as200
    cat > ../core/routing_config/as200/daemons << 'AS200_DAEMONS'
bgpd=yes
zebra=yes
vtysh_enable=yes
zebra_options="  -A 127.0.0.1 -s 90000000"
bgpd_options="   -A 127.0.0.1"
AS200_DAEMONS

    cat > ../core/routing_config/as200/vtysh.conf << 'AS200_VTYSH'
service integrated-vtysh-config
AS200_VTYSH

    cat > ../core/routing_config/as200/frr.conf << 'AS200_FRR'
frr version 8.4_git
frr defaults traditional
hostname as200
service integrated-vtysh-config

ip route 200.0.0.0/16 null0

router bgp 65200
 bgp router-id 172.20.0.20
 bgp log-neighbor-changes
 network 200.0.0.0/16
 neighbor 172.20.0.10 remote-as 65100
 neighbor 172.20.0.10 description as100
 neighbor 172.20.0.30 remote-as 65300
 neighbor 172.20.0.30 description as300
 neighbor 172.20.0.40 remote-as 65400
 neighbor 172.20.0.40 description as400

line vty
AS200_FRR

    # AS300 Configuration
    mkdir -p ../core/routing_config/as300
    cat > ../core/routing_config/as300/daemons << 'AS300_DAEMONS'
bgpd=yes
zebra=yes
vtysh_enable=yes
zebra_options="  -A 127.0.0.1 -s 90000000"
bgpd_options="   -A 127.0.0.1"
AS300_DAEMONS

    cat > ../core/routing_config/as300/vtysh.conf << 'AS300_VTYSH'
service integrated-vtysh-config
AS300_VTYSH

    cat > ../core/routing_config/as300/frr.conf << 'AS300_FRR'
frr version 8.4_git
frr defaults traditional
hostname as300
service integrated-vtysh-config

ip route 8.8.8.0/24 null0

router bgp 65300
 bgp router-id 172.20.0.30
 bgp log-neighbor-changes
 network 8.8.8.0/24
 neighbor 172.20.0.20 remote-as 65200
 neighbor 172.20.0.20 description as200
 neighbor 172.20.0.50 remote-as 65500
 neighbor 172.20.0.50 description as500

line vty
AS300_FRR

    # AS400 Configuration
    mkdir -p ../core/routing_config/as400
    cat > ../core/routing_config/as400/daemons << 'AS400_DAEMONS'
bgpd=yes
zebra=yes
vtysh_enable=yes
zebra_options="  -A 127.0.0.1 -s 90000000"
bgpd_options="   -A 127.0.0.1"
AS400_DAEMONS

    cat > ../core/routing_config/as400/vtysh.conf << 'AS400_VTYSH'
service integrated-vtysh-config
AS400_VTYSH

    cat > ../core/routing_config/as400/frr.conf << 'AS400_FRR'
frr version 8.4_git
frr defaults traditional
hostname as400
service integrated-vtysh-config

ip route 192.168.1.0/24 null0

router bgp 65400
 bgp router-id 172.20.0.40
 bgp log-neighbor-changes
 network 192.168.1.0/24
 neighbor 172.20.0.20 remote-as 65200
 neighbor 172.20.0.20 description as200

line vty
AS400_FRR

    # AS500 Configuration (Attacker)
    mkdir -p ../core/routing_config/as500
    cat > ../core/routing_config/as500/daemons << 'AS500_DAEMONS'
bgpd=yes
zebra=yes
vtysh_enable=yes
zebra_options="  -A 127.0.0.1 -s 90000000"
bgpd_options="   -A 127.0.0.1"
AS500_DAEMONS

    cat > ../core/routing_config/as500/vtysh.conf << 'AS500_VTYSH'
service integrated-vtysh-config
AS500_VTYSH

    cat > ../core/routing_config/as500/frr.conf << 'AS500_FRR'
frr version 8.4_git
frr defaults traditional
hostname as500
service integrated-vtysh-config

ip route 172.16.0.0/16 null0

router bgp 65500
 bgp router-id 172.20.0.50
 bgp log-neighbor-changes
 network 172.16.0.0/16
 neighbor 172.20.0.30 remote-as 65300
 neighbor 172.20.0.30 description as300

line vty
AS500_FRR

    echo "✓ All configurations created"
}

start_containers() {
    echo "🐳 Starting containers..."
    
    docker run -d --rm --name as100 --hostname as100 --network bgp-sim --ip 172.20.0.10 \
        -v "$(pwd)/../core/routing_config/as100:/etc/frr" --privileged frrouting/frr:v8.4.0
    
    docker run -d --rm --name as200 --hostname as200 --network bgp-sim --ip 172.20.0.20 \
        -v "$(pwd)/../core/routing_config/as200:/etc/frr" --privileged frrouting/frr:v8.4.0
        
    docker run -d --rm --name as300 --hostname as300 --network bgp-sim --ip 172.20.0.30 \
        -v "$(pwd)/../core/routing_config/as300:/etc/frr" --privileged frrouting/frr:v8.4.0
        
    docker run -d --rm --name as400 --hostname as400 --network bgp-sim --ip 172.20.0.40 \
        -v "$(pwd)/../core/routing_config/as400:/etc/frr" --privileged frrouting/frr:v8.4.0
        
    docker run -d --rm --name as500 --hostname as500 --network bgp-sim --ip 172.20.0.50 \
        -v "$(pwd)/../core/routing_config/as500:/etc/frr" --privileged frrouting/frr:v8.4.0
    
    echo "⏳ Waiting 30 seconds for BGP to converge..."
    sleep 30
}

verify_bgp() {
    echo "🔍 Verifying BGP sessions..."
    
    for as_name in as100 as200 as300 as400 as500; do
        echo "=== $as_name BGP Status ==="
        docker exec -t "$as_name" vtysh -c "show ip bgp summary" | grep -E "(Neighbor|Established)" || echo "No established sessions"
        echo ""
    done
}

main() {
    cleanup
    create_configs
    start_containers
    verify_bgp
    
    echo "🎉 BGP Topology Ready!"
    echo ""
    echo "Test commands:"
    echo "  docker exec -t as200 vtysh -c 'show ip bgp'"
    echo "  docker exec -t as500 vtysh -c 'show ip bgp neighbors'"
    echo ""
    echo "Run attack simulation:"
    echo "  python3 bgp_attack_simulator.py"
}

main "$@"
