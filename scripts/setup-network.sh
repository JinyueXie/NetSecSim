#!/bin/bash

# Create BGP network if it doesn't exist
docker network ls | grep bgp-net || docker network create --driver bridge --subnet=10.1.0.0/24 bgp-net

echo "BGP network created successfully!"
