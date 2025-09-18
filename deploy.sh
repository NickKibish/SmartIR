#!/bin/bash

# Deploy SmartIR integration to Home Assistant and restart
# This script copies the integration files and restarts the HA container

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Directories
INTEGRATION_SOURCE="./custom_components/smartir"
HA_CUSTOM_COMPONENTS="../ha/config/custom_components"
HA_INTEGRATION_TARGET="$HA_CUSTOM_COMPONENTS/smartir"

echo -e "${YELLOW}🚀 Deploying SmartIR integration...${NC}"

# Check if source integration exists
if [ ! -d "$INTEGRATION_SOURCE" ]; then
    echo -e "${RED}❌ Error: Integration source directory not found: $INTEGRATION_SOURCE${NC}"
    exit 1
fi

# Create custom_components directory if it doesn't exist
if [ ! -d "$HA_CUSTOM_COMPONENTS" ]; then
    echo -e "${YELLOW}📁 Creating custom_components directory...${NC}"
    mkdir -p "$HA_CUSTOM_COMPONENTS"
fi

# Remove existing integration if it exists
if [ -d "$HA_INTEGRATION_TARGET" ]; then
    echo -e "${YELLOW}🗑️  Removing existing integration...${NC}"
    # Use docker to remove to handle permissions properly
    cd ../ha
    docker-compose exec homeassistant rm -rf /config/custom_components/smartir || true
    cd ../SmartIR
fi

# Copy integration files
echo -e "${YELLOW}📋 Copying integration files...${NC}"
cp -r "$INTEGRATION_SOURCE" "$HA_INTEGRATION_TARGET"

# Copy codes directory to writable config location
echo -e "${YELLOW}📋 Copying device codes...${NC}"
CODES_SOURCE="./codes"
CODES_TARGET="../ha/config/smartir_codes"
if [ -d "$CODES_SOURCE" ]; then
    mkdir -p "$CODES_TARGET"
    cp -r "$CODES_SOURCE"/* "$CODES_TARGET/"
fi

# Verify copy was successful
if [ ! -d "$HA_INTEGRATION_TARGET" ]; then
    echo -e "${RED}❌ Error: Failed to copy integration files${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Integration files copied successfully${NC}"

# Change to HA directory for docker-compose commands
cd ../ha

# Restart Home Assistant container
echo -e "${YELLOW}🔄 Restarting Home Assistant container...${NC}"
docker-compose restart homeassistant

# Wait for HA to start
echo -e "${YELLOW}⏳ Waiting for Home Assistant to start...${NC}"
sleep 10

# Check if container is running
if docker-compose ps homeassistant | grep -q "Up"; then
    echo -e "${GREEN}✅ Home Assistant restarted successfully${NC}"
    echo -e "${GREEN}🌐 Home Assistant should be available at: http://localhost:8123${NC}"
else
    echo -e "${RED}❌ Error: Home Assistant container failed to start${NC}"
    echo -e "${YELLOW}📋 Recent logs:${NC}"
    docker-compose logs --tail=20 homeassistant
    exit 1
fi

echo -e "${GREEN}🎉 Deployment complete!${NC}"