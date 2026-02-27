#!/bin/bash
set -e

# ──────────────────────────────────────────────
# Docker Swarm deployment script for ipsec-back
# ──────────────────────────────────────────────

STACK_NAME="${STACK_NAME:-ipsec-back}"
DOCKER_REGISTRY="${DOCKER_REGISTRY:-localhost:5000}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
IMAGE_NAME="${DOCKER_REGISTRY}/ipsec-back:${IMAGE_TAG}"

usage() {
    echo "Usage: $0 {build|push|deploy|update|status|logs|rm}"
    echo ""
    echo "Commands:"
    echo "  build    Build the Docker image"
    echo "  push     Push the image to the registry"
    echo "  deploy   Deploy (or update) the stack to Docker Swarm"
    echo "  update   Build, push, and redeploy the stack"
    echo "  status   Show running services and tasks"
    echo "  logs     Show logs for a service (web|nginx)"
    echo "  rm       Remove the stack from Swarm"
    exit 1
}

check_swarm() {
    if ! docker info --format '{{.Swarm.LocalNodeState}}' 2>/dev/null | grep -q "active"; then
        echo "ERROR: Docker Swarm is not initialized."
        echo "Run: docker swarm init"
        exit 1
    fi
}

check_network() {
    if ! docker network ls --format '{{.Name}}' | grep -q "^core_gateway_network$"; then
        echo "Creating overlay network: core_gateway_network"
        docker network create --driver overlay --attachable core_gateway_network
    fi
}

build() {
    echo "Building image: ${IMAGE_NAME}"
    docker build -t "${IMAGE_NAME}" .
    echo "Build complete."
}

push() {
    echo "Pushing image: ${IMAGE_NAME}"
    docker push "${IMAGE_NAME}"
    echo "Push complete."
}

deploy() {
    check_swarm
    check_network

    echo "Deploying stack: ${STACK_NAME}"
    DOCKER_REGISTRY="${DOCKER_REGISTRY}" IMAGE_TAG="${IMAGE_TAG}" \
        docker stack deploy -c docker-compose.yml "${STACK_NAME}"
    echo ""
    echo "Stack '${STACK_NAME}' deployed. Check status with:"
    echo "  $0 status"
}

update() {
    build
    push
    deploy
    echo ""
    echo "Update complete. Swarm will perform a rolling update."
}

status() {
    check_swarm
    echo "=== Services ==="
    docker stack services "${STACK_NAME}"
    echo ""
    echo "=== Tasks ==="
    docker stack ps "${STACK_NAME}" --no-trunc
}

logs() {
    local service="${2:-web}"
    docker service logs -f "${STACK_NAME}_${service}"
}

remove() {
    echo "Removing stack: ${STACK_NAME}"
    docker stack rm "${STACK_NAME}"
    echo "Stack removed."
}

# ─── Main ───
case "${1}" in
    build)  build ;;
    push)   push ;;
    deploy) deploy ;;
    update) update ;;
    status) status ;;
    logs)   logs "$@" ;;
    rm)     remove ;;
    *)      usage ;;
esac
