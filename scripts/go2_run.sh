#!/usr/bin/env bash
set -euo pipefail

# Run any command with Go2 ROS2/DDS environment loaded.
# Example:
#   scripts/go2_run.sh -- ros2 topic list
#   scripts/go2_run.sh --domain 0 --rmw rmw_cyclonedds_cpp -- ros2 launch go2_driver_py driver.launch.py use_rviz:=true

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

DOMAIN_ID="${GO2_DOMAIN_ID:-0}"
RMW_IMPL="${GO2_RMW:-rmw_cyclonedds_cpp}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --domain)
      DOMAIN_ID="$2"
      shift 2
      ;;
    --rmw)
      RMW_IMPL="$2"
      shift 2
      ;;
    --)
      shift
      break
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: scripts/go2_run.sh [--domain N] [--rmw NAME] -- <command...>"
      exit 2
      ;;
  esac
done

if [[ $# -eq 0 ]]; then
  echo "No command given."
  echo "Usage: scripts/go2_run.sh [--domain N] [--rmw NAME] -- <command...>"
  exit 2
fi

# shellcheck disable=SC1091
source "${SCRIPT_DIR}/go2_env.sh" "${DOMAIN_ID}" "${RMW_IMPL}"

exec "$@"
