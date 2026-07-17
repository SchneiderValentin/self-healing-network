#!/bin/bash

# ==========================================
# CONFIG
# ==========================================
INTERFACE="ens22"
MANAGEMENT_IP="192.168.99.99"
PORT="5000"
SOURCE_IP="10.0.2.20"

echo "Target online. Waiting for $SOURCE_IP at $INTERFACE..."

# ==========================================
# CATCH
# ==========================================

EXACT_TIME=$(sudo tcpdump -i $INTERFACE -n -tt -c 1 "icmp and src host $SOURCE_IP" 2>/dev/null | awk '{print $1}')

# ==========================================
# PUSH
# ==========================================

if [ -n "$EXACT_TIME" ]; then
    curl -s -X POST http://${MANAGEMENT_IP}:${PORT}/webhook/sniffer \
         -H "Content-Type: application/json" \
         -d "{\"node\": \"edge_target\", \"timestamp\": \"${EXACT_TIME}\"}" > /dev/null &

    echo "ICMP Traffic from $SOURCE_IP detected. Timestamp $EXACT_TIME sent."
else
    echo "ERROR: maybe tcpdump has been closed"
fi