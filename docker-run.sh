#!/bin/bash

# Script to help with common Docker operations for the docx-parser-api

# Make script exit if any command fails
set -e

# Define colors for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to display usage
usage() {
    echo -e "${YELLOW}Usage:${NC}"
    echo -e "  $0 ${GREEN}start${NC}    - Build and start the container"
    echo -e "  $0 ${GREEN}stop${NC}     - Stop the container"
    echo -e "  $0 ${GREEN}logs${NC}     - View logs"
    echo -e "  $0 ${GREEN}test${NC}     - Run tests"
    echo -e "  $0 ${GREEN}test-v${NC}   - Run tests with verbose output"
    echo -e "  $0 ${GREEN}shell${NC}    - Open a shell in the container"
    echo -e "  $0 ${GREEN}rebuild${NC}  - Force rebuild the container"
}

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo -e "${YELLOW}Error: Docker is not running.${NC}"
        echo "Please start Docker and try again."
        exit 1
    fi
}

# Main logic based on arguments
case "$1" in
    start)
        check_docker
        echo -e "${GREEN}Starting the container...${NC}"
        docker compose up -d
        echo -e "${GREEN}Container started! API available at http://localhost:8000${NC}"
        ;;
    stop)
        check_docker
        echo -e "${GREEN}Stopping the container...${NC}"
        docker compose down
        echo -e "${GREEN}Container stopped.${NC}"
        ;;
    logs)
        check_docker
        echo -e "${GREEN}Showing logs (press Ctrl+C to exit)...${NC}"
        docker compose logs -f
        ;;
    test)
        check_docker
        echo -e "${GREEN}Running tests...${NC}"
        docker compose exec api pytest
        ;;
    test-v)
        check_docker
        echo -e "${GREEN}Running tests with verbose output...${NC}"
        docker compose exec api pytest -v
        ;;
    shell)
        check_docker
        echo -e "${GREEN}Opening shell in the container...${NC}"
        docker compose exec api /bin/bash
        ;;
    rebuild)
        check_docker
        echo -e "${GREEN}Rebuilding the container...${NC}"
        docker compose build --no-cache
        docker compose up -d
        echo -e "${GREEN}Container rebuilt and started!${NC}"
        ;;
    *)
        usage
        ;;
esac 