#!/bin/bash
set -e

# N-Link Analysis - Docker Entrypoint
# Supports multiple services: api, basin-viewer, multiplex, tunneling, reports, all

SERVICE="${1:-api}"
shift 2>/dev/null || true

case "$SERVICE" in
    api)
        echo "Starting N-Link API on port 8000..."
        exec uvicorn nlink_api.main:app --host 0.0.0.0 --port 8000 "$@"
        ;;

    basin-viewer)
        echo "Starting Basin Geometry Viewer on port 8055..."
        exec python n-link-analysis/viz/dash-basin-geometry-viewer.py --host 0.0.0.0 --port 8055 "$@"
        ;;

    multiplex)
        echo "Starting Multiplex Analyzer on port 8056..."
        exec python n-link-analysis/viz/multiplex-analyzer.py --host 0.0.0.0 --port 8056 "$@"
        ;;

    tunneling)
        echo "Starting Tunneling Explorer on port 8060..."
        # Check if API URL is set for API mode
        if [ -n "$API_URL" ]; then
            echo "  API mode enabled: $API_URL"
            exec python n-link-analysis/viz/tunneling/tunneling-explorer.py \
                --host 0.0.0.0 --port 8060 --use-api --api-url "$API_URL" "$@"
        else
            exec python n-link-analysis/viz/tunneling/tunneling-explorer.py --host 0.0.0.0 --port 8060 "$@"
        fi
        ;;

    shell)
        echo "Starting interactive shell..."
        exec /bin/bash "$@"
        ;;

    test)
        echo "Running tests..."
        exec pytest nlink_api/tests/ -v "$@"
        ;;

    reports)
        echo "Starting Reports Gallery on port 8070..."
        cd /app/n-link-analysis/report/assets
        exec python -m http.server 8070 --bind 0.0.0.0 "$@"
        ;;

    all)
        echo "Starting all services..."
        echo "  API on port 8000"
        echo "  Basin Viewer on port 8055"
        echo "  Multiplex Analyzer on port 8056"
        echo "  Tunneling Explorer on port 8060"
        echo "  Reports Gallery on port 8070"

        # Start all services in background, API in foreground
        python n-link-analysis/viz/dash-basin-geometry-viewer.py --host 0.0.0.0 --port 8055 &
        python n-link-analysis/viz/multiplex-analyzer.py --host 0.0.0.0 --port 8056 &
        python n-link-analysis/viz/tunneling/tunneling-explorer.py --host 0.0.0.0 --port 8060 --use-api --api-url http://localhost:8000 &
        (cd /app/n-link-analysis/report/assets && python -m http.server 8070 --bind 0.0.0.0) &

        # API in foreground
        exec uvicorn nlink_api.main:app --host 0.0.0.0 --port 8000 "$@"
        ;;

    *)
        echo "Unknown service: $SERVICE"
        echo "Available services:"
        echo "  api          - N-Link REST API (port 8000)"
        echo "  basin-viewer - Basin Geometry Viewer dashboard (port 8055)"
        echo "  multiplex    - Multiplex Analyzer dashboard (port 8056)"
        echo "  tunneling    - Tunneling Explorer dashboard (port 8060)"
        echo "  reports      - Static reports gallery (port 8070)"
        echo "  all          - Start all services"
        echo "  shell        - Interactive bash shell"
        echo "  test         - Run test suite"
        exit 1
        ;;
esac
