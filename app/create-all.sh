#!/bin/bash
# Build und Deployment Script für Load Testing Application

set -e

# Konfiguration
IMAGE_NAME="load-test-app"
IMAGE_TAG="latest"
REGISTRY="${REGISTRY:-localhost:5000}"  # Passe an deine Registry an
NAMESPACE="load-testing"

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Funktionen
build_image() {
    print_status "Building Docker Image..."
    docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
    print_success "Docker Image built successfully"
}

tag_and_push() {
    if [ "$REGISTRY" != "localhost:5000" ]; then
        print_status "Tagging and pushing to registry..."
        docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}
        docker push ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}
        print_success "Image pushed to registry"
    else
        print_warning "Using localhost registry, skipping push"
    fi
}

deploy_to_k8s() {
    print_status "Deploying to Kubernetes..."
    
    # Update image in deployment
    if [ "$REGISTRY" != "localhost:5000" ]; then
        sed -i.bak "s|image: load-test-app:latest|image: ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}|g" k8s-manifests.yaml
    fi
    
    # Apply manifests
    kubectl apply -f k8s-manifests.yaml
    
    # Wait for deployment
    print_status "Waiting for deployment to be ready..."
    kubectl rollout status deployment/load-test-app -n ${NAMESPACE} --timeout=300s
    
    print_success "Deployment completed successfully"
}

check_deployment() {
    print_status "Checking deployment status..."
    
    echo "Pods:"
    kubectl get pods -n ${NAMESPACE} -l app=load-test-app
    
    echo -e "\nServices:"
    kubectl get svc -n ${NAMESPACE}
    
    echo -e "\nIngress:"
    kubectl get ingress -n ${NAMESPACE} 2>/dev/null || echo "No ingress found"
    
    echo -e "\nHPA:"
    kubectl get hpa -n ${NAMESPACE} 2>/dev/null || echo "No HPA found"
}

port_forward() {
    print_status "Setting up port forwarding..."
    print_warning "Press Ctrl+C to stop port forwarding"
    kubectl port-forward -n ${NAMESPACE} service/load-test-service 8080:80
}

run_load_test() {
    print_status "Running sample load test..."
    
    # Get service endpoint
    if kubectl get svc -n ${NAMESPACE} load-test-service &>/dev/null; then
        # Port forward in background
        kubectl port-forward -n ${NAMESPACE} service/load-test-service 8080:80 &
        PF_PID=$!
        sleep 5
        
        # Run test
        echo "Starting stress test via API..."
        curl -X POST http://localhost:8080/stress \
            -H "Content-Type: application/json" \
            -d '{
                "cpu_workers": 4,
                "memory_workers": 2,
                "duration": 60,
                "memory_size": "512M"
            }'
        
        echo -e "\n\nChecking metrics..."
        curl -s http://localhost:8080/metrics | jq .
        
        # Clean up
        kill $PF_PID 2>/dev/null || true
        print_success "Load test completed"
    else
        print_error "Service not found. Deploy first."
        exit 1
    fi
}

cleanup() {
    print_status "Cleaning up..."
    kubectl delete -f k8s-manifests.yaml --ignore-not-found=true
    print_success "Cleanup completed"
}

show_help() {
    echo "Load Testing Application - Build & Deploy Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build      - Build the Docker image"
    echo "  push       - Tag and push image to registry"
    echo "  deploy     - Deploy to Kubernetes"
    echo "  all        - Build, push and deploy"
    echo "  status     - Check deployment status"
    echo "  port       - Setup port forwarding to service"
    echo "  test       - Run a sample load test"
    echo "  cleanup    - Delete all resources"
    echo "  help       - Show this help"
    echo ""
    echo "Environment Variables:"
    echo "  REGISTRY   - Docker registry (default: localhost:5000)"
    echo ""
    echo "Examples:"
    echo "  $0 all                    # Build and deploy everything"
    echo "  REGISTRY=myregistry.com $0 push  # Push to specific registry"
    echo "  $0 test                   # Run load test"
}

# Main script logic
case "${1:-help}" in
    build)
        build_image
        ;;
    push)
        tag_and_push
        ;;
    deploy)
        deploy_to_k8s
        ;;
    all)
        build_image
        tag_and_push
        deploy_to_k8s
        check_deployment
        ;;
    status)
        check_deployment
        ;;
    port)
        port_forward
        ;;
    test)
        run_load_test
        ;;
    cleanup)
        cleanup
        ;;
    help|*)
        show_help
        ;;
esac

