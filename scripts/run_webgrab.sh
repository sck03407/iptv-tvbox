#!/bin/bash
set -e

# Setup network bypass (ICMP redirect)
echo "Setting up network bypass..."
apk add --no-cache iptables
iptables -t nat -A OUTPUT -p icmp --icmp-type echo-request -j DNAT --to-destination 127.0.0.1

# Determine dotnet command
DOTNET_CMD=dotnet
[ -x /app/dotnet/dotnet ] && DOTNET_CMD=/app/dotnet/dotnet

echo "Starting WebGrab+Plus processing loop..."

# Backup the original full config
if [ -f /config/WebGrab++.config.xml ]; then
    echo "Backing up full config..."
    cp /config/WebGrab++.config.xml /config/WebGrab++.config.backup.xml
fi

# Loop through all chunked configs
count=0
# Use nullglob to handle case where no files match
shopt -s nullglob

# We look for config files in /config directory
for config_file in /config/WebGrab++.config.*.xml; do
    # Skip if it doesn't match our pattern (e.g. full.xml or just the main one)
    # The glob above matches anything starting with WebGrab++.config.
    # We strictly want .NUMBER.xml
    if [[ ! "$config_file" =~ \.[0-9]+\.xml$ ]]; then
        # echo "Skipping non-chunk file: $config_file"
        continue
    fi

    echo "==================================================="
    echo "Processing chunk: $config_file"
    echo "==================================================="

    # Overwrite main config
    cp "$config_file" /config/WebGrab++.config.xml

    # Run WG++
    # We allow it to fail without stopping the loop, so we can try other chunks
    $DOTNET_CMD /app/wg++/bin.net/WebGrab+Plus.dll /config || echo "Warning: WG++ failed for $config_file"
    
    count=$((count+1))
done

# Restore the full config
if [ -f /config/WebGrab++.config.backup.xml ]; then
    echo "Restoring full config..."
    mv /config/WebGrab++.config.backup.xml /config/WebGrab++.config.xml
fi

echo "Finished processing $count chunks."
