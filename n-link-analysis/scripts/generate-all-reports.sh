#!/bin/bash
# Generate all reports and assets via the N-Link API
#
# This script orchestrates the full report generation pipeline:
#   1. Generate trunkiness dashboard (aggregates branch analysis)
#   2. Generate human-readable report with charts
#   3. Render markdown reports to styled HTML
#   4. Render basin geometry visualizations as PNG images
#
# Prerequisites:
#   - API server running on $API_BASE (default: http://localhost:28000)
#   - Branch analysis data already computed (branches_all_*.parquet files)
#   - Basin pointcloud data for image rendering
#
# Usage:
#   ./generate-all-reports.sh [OPTIONS]
#
# Options:
#   --api-base URL     API base URL (default: http://localhost:28000)
#   --tag TAG          Data tag (default: bootstrap_2025-12-30)
#   --n N              N-link rule value (default: 5)
#   --skip-trunkiness  Skip trunkiness dashboard generation
#   --skip-human       Skip human report generation
#   --skip-html        Skip HTML rendering
#   --skip-basins      Skip basin image rendering
#   --basins-only LIST Comma-separated list of basins to render (default: all)
#   --comparison-grid  Generate comparison grid instead of individual images
#   --dry-run          Show what would be done without executing
#   --help             Show this help message
#
# Examples:
#   ./generate-all-reports.sh
#   ./generate-all-reports.sh --skip-basins
#   ./generate-all-reports.sh --basins-only "Massachusetts,United_States"
#   ./generate-all-reports.sh --comparison-grid

set -e

# Default configuration
API_BASE="${API_BASE:-http://localhost:28000}"
TAG="bootstrap_2025-12-30"
N=5
SKIP_TRUNKINESS=false
SKIP_HUMAN=false
SKIP_HTML=false
SKIP_BASINS=false
BASINS_ONLY=""
COMPARISON_GRID=false
DRY_RUN=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --api-base)
            API_BASE="$2"
            shift 2
            ;;
        --tag)
            TAG="$2"
            shift 2
            ;;
        --n)
            N="$2"
            shift 2
            ;;
        --skip-trunkiness)
            SKIP_TRUNKINESS=true
            shift
            ;;
        --skip-human)
            SKIP_HUMAN=true
            shift
            ;;
        --skip-html)
            SKIP_HTML=true
            shift
            ;;
        --skip-basins)
            SKIP_BASINS=true
            shift
            ;;
        --basins-only)
            BASINS_ONLY="$2"
            shift 2
            ;;
        --comparison-grid)
            COMPARISON_GRID=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --help)
            head -40 "$0" | tail -35
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Helper functions
log_step() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}▶ $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

log_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

log_error() {
    echo -e "${RED}✗ $1${NC}"
}

log_info() {
    echo -e "  $1"
}

# API call helper with error handling
api_call() {
    local method="$1"
    local endpoint="$2"
    local data="$3"
    local description="$4"

    if $DRY_RUN; then
        echo -e "${YELLOW}[DRY-RUN]${NC} Would call: $method $API_BASE$endpoint"
        if [ -n "$data" ]; then
            echo "  Data: $data"
        fi
        # Return empty JSON so parsing doesn't fail
        echo "{}"
        return 0
    fi

    local response
    local http_code

    if [ "$method" = "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST "$API_BASE$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data" 2>&1)
    else
        response=$(curl -s -w "\n%{http_code}" "$API_BASE$endpoint" 2>&1)
    fi

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        echo "$body"
        return 0
    else
        log_error "$description failed (HTTP $http_code)"
        echo "$body" | python3 -m json.tool 2>/dev/null || echo "$body"
        return 1
    fi
}

# Check API health
check_api() {
    log_step "Checking API connectivity"

    if $DRY_RUN; then
        log_warning "[DRY-RUN] Skipping API health check"
        return 0
    fi

    local health
    health=$(curl -s "$API_BASE/api/v1/health" 2>&1)

    if echo "$health" | grep -q '"status":"ok"'; then
        log_success "API is healthy at $API_BASE"
    else
        log_error "API health check failed"
        echo "$health"
        exit 1
    fi
}

# Generate trunkiness dashboard
generate_trunkiness() {
    if $SKIP_TRUNKINESS; then
        log_warning "Skipping trunkiness dashboard (--skip-trunkiness)"
        return 0
    fi

    log_step "Generating Trunkiness Dashboard (N=$N, tag=$TAG)"

    local data="{\"n\": $N, \"tag\": \"$TAG\"}"
    local result

    if result=$(api_call POST "/api/v1/reports/trunkiness" "$data" "Trunkiness dashboard"); then
        local elapsed=$(echo "$result" | python3 -c "import sys,json; print(f\"{json.load(sys.stdin).get('elapsed_seconds', 0):.2f}\")" 2>/dev/null || echo "?")
        local count=$(echo "$result" | python3 -c "import sys,json; print(len(json.load(sys.stdin).get('stats', [])))" 2>/dev/null || echo "?")
        log_success "Generated trunkiness stats for $count basins in ${elapsed}s"
    else
        log_warning "Trunkiness generation failed - continuing anyway"
    fi
}

# Generate human-readable report
generate_human_report() {
    if $SKIP_HUMAN; then
        log_warning "Skipping human report (--skip-human)"
        return 0
    fi

    log_step "Generating Human-Readable Report (tag=$TAG)"

    local data="{\"tag\": \"$TAG\"}"
    local result

    if result=$(api_call POST "/api/v1/reports/human" "$data" "Human report"); then
        local elapsed=$(echo "$result" | python3 -c "import sys,json; print(f\"{json.load(sys.stdin).get('elapsed_seconds', 0):.2f}\")" 2>/dev/null || echo "?")
        local figures=$(echo "$result" | python3 -c "import sys,json; print(len(json.load(sys.stdin).get('figures', [])))" 2>/dev/null || echo "?")
        local report_path=$(echo "$result" | python3 -c "import sys,json; print(json.load(sys.stdin).get('report_path', 'unknown'))" 2>/dev/null || echo "unknown")
        log_success "Generated report with $figures figures in ${elapsed}s"
        log_info "Report: $report_path"
    else
        log_warning "Human report generation failed - continuing anyway"
    fi
}

# Render HTML reports
render_html() {
    if $SKIP_HTML; then
        log_warning "Skipping HTML rendering (--skip-html)"
        return 0
    fi

    log_step "Rendering Markdown Reports to HTML"

    local data="{\"dry_run\": false}"
    local result

    if result=$(api_call POST "/api/v1/reports/render/html" "$data" "HTML rendering"); then
        local elapsed=$(echo "$result" | python3 -c "import sys,json; print(f\"{json.load(sys.stdin).get('elapsed_seconds', 0):.2f}\")" 2>/dev/null || echo "?")
        local count=$(echo "$result" | python3 -c "import sys,json; print(json.load(sys.stdin).get('count', 0))" 2>/dev/null || echo "?")
        local output_dir=$(echo "$result" | python3 -c "import sys,json; print(json.load(sys.stdin).get('output_dir', 'unknown'))" 2>/dev/null || echo "unknown")
        log_success "Rendered $count HTML files in ${elapsed}s"
        log_info "Output: $output_dir"

        # List generated files
        echo "$result" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for f in data.get('rendered', []):
    print(f'    - {f}')
" 2>/dev/null || true
    else
        log_warning "HTML rendering failed - continuing anyway"
    fi
}

# Render basin images
render_basin_images() {
    if $SKIP_BASINS; then
        log_warning "Skipping basin image rendering (--skip-basins)"
        return 0
    fi

    log_step "Rendering Basin Geometry Images (N=$N)"

    local data

    if $COMPARISON_GRID; then
        log_info "Mode: Comparison grid (all basins in one image)"
        data="{\"n\": $N, \"comparison_grid\": true, \"width\": 1600, \"height\": 1200}"
    elif [ -n "$BASINS_ONLY" ]; then
        # Convert comma-separated list to JSON array
        local cycles_json=$(echo "$BASINS_ONLY" | python3 -c "import sys; print('[' + ','.join(f'\"{c.strip()}\"' for c in sys.stdin.read().strip().split(',')) + ']')")
        log_info "Mode: Selected basins: $BASINS_ONLY"
        data="{\"n\": $N, \"cycles\": $cycles_json, \"width\": 1200, \"height\": 800}"
    else
        log_info "Mode: All basins (individual images)"
        data="{\"n\": $N, \"width\": 1200, \"height\": 800}"
    fi

    local result

    if result=$(api_call POST "/api/v1/reports/render/basins" "$data" "Basin image rendering"); then
        local elapsed=$(echo "$result" | python3 -c "import sys,json; print(f\"{json.load(sys.stdin).get('elapsed_seconds', 0):.2f}\")" 2>/dev/null || echo "?")
        local count=$(echo "$result" | python3 -c "import sys,json; print(json.load(sys.stdin).get('count', 0))" 2>/dev/null || echo "?")
        local output_dir=$(echo "$result" | python3 -c "import sys,json; print(json.load(sys.stdin).get('output_dir', 'unknown'))" 2>/dev/null || echo "unknown")
        log_success "Rendered $count basin images in ${elapsed}s"
        log_info "Output: $output_dir"

        # List generated files
        echo "$result" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for f in data.get('rendered', []):
    print(f'    - {f}')
" 2>/dev/null || true
    else
        log_error "Basin image rendering failed"
        return 1
    fi
}

# Generate gallery HTML
generate_gallery() {
    log_step "Generating Gallery HTML"

    if $DRY_RUN; then
        echo -e "${YELLOW}[DRY-RUN]${NC} Would run: python3 n-link-analysis/viz/create-visualization-gallery.py"
        return 0
    fi

    # Get the repo root (parent of n-link-analysis)
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local repo_root="$(cd "$script_dir/../.." && pwd)"

    if python3 "$repo_root/n-link-analysis/viz/create-visualization-gallery.py" 2>&1; then
        log_success "Gallery HTML generated"
    else
        log_warning "Gallery generation failed - continuing anyway"
    fi
}

# Print summary
print_summary() {
    log_step "Generation Complete"

    if $DRY_RUN; then
        log_warning "This was a dry run - no files were actually generated"
        return 0
    fi

    echo ""
    echo "Generated assets are available at:"
    echo "  - API static files: $API_BASE/static/assets/"
    echo "  - Reports Gallery:  http://localhost:28070/gallery.html"
    echo ""
    echo "To regenerate specific components:"
    echo "  ./generate-all-reports.sh --skip-basins     # Skip slow basin rendering"
    echo "  ./generate-all-reports.sh --comparison-grid # Single comparison image"
    echo ""
}

# Main execution
main() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║           N-Link Report Generation Pipeline                      ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"

    echo "Configuration:"
    echo "  API Base:    $API_BASE"
    echo "  Tag:         $TAG"
    echo "  N:           $N"
    echo "  Dry Run:     $DRY_RUN"

    if $DRY_RUN; then
        echo ""
        log_warning "DRY RUN MODE - No changes will be made"
    fi

    check_api
    generate_trunkiness
    generate_human_report
    render_html
    render_basin_images
    generate_gallery
    print_summary
}

main "$@"
