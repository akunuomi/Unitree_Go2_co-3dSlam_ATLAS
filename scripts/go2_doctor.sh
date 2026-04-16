#!/usr/bin/env bash
set -euo pipefail

# Go2 LAN diagnostic for ROS2 DDS visibility.
# This script validates network reachability and topic discovery with current DDS settings.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

ROBOT_IP=""
DOMAIN_ID="${GO2_DOMAIN_ID:-0}"
RMW_IMPL="${GO2_RMW:-rmw_cyclonedds_cpp}"
TOPIC_TIMEOUT="${GO2_TOPIC_TIMEOUT:-6}"

usage() {
  cat <<'EOF'
Usage:
  scripts/go2_doctor.sh --robot-ip <IP> [--domain N] [--rmw NAME]
  scripts/go2_doctor.sh [--domain N] [--rmw NAME]

Examples:
  scripts/go2_doctor.sh --robot-ip 192.168.12.1
  scripts/go2_doctor.sh --domain 0 --rmw rmw_cyclonedds_cpp
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --robot-ip)
      ROBOT_IP="$2"
      shift 2
      ;;
    --domain)
      DOMAIN_ID="$2"
      shift 2
      ;;
    --rmw)
      RMW_IMPL="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      usage
      exit 2
      ;;
  esac
done

if [[ ! -x "${SCRIPT_DIR}/go2_run.sh" ]]; then
  echo "Missing executable: ${SCRIPT_DIR}/go2_run.sh"
  exit 1
fi

echo "== Go2 ROS2 LAN Doctor =="
echo "Workspace: ${WORKSPACE_DIR}"
echo "ROS_DOMAIN_ID: ${DOMAIN_ID}"
echo "RMW_IMPLEMENTATION: ${RMW_IMPL}"

if [[ -n "${ROBOT_IP}" ]]; then
  echo
echo "[1/4] Ping robot (${ROBOT_IP})"
  if ping -c 2 -W 1 "${ROBOT_IP}" >/dev/null 2>&1; then
    echo "PASS: Ping reachable"
  else
    echo "FAIL: Ping unreachable"
    echo "Hint: Check LAN, subnet, cable/Wi-Fi, and robot network mode."
    exit 1
  fi
fi

echo
echo "[2/4] ROS2 CLI check"
if ! command -v ros2 >/dev/null 2>&1; then
  echo "WARN: ros2 not found in current shell PATH. Will continue with wrapped env execution."
else
  echo "PASS: ros2 command found in current shell"
fi

echo
echo "[3/4] Topic discovery"
TOPICS_OUTPUT="$(timeout "${TOPIC_TIMEOUT}" "${SCRIPT_DIR}/go2_run.sh" --domain "${DOMAIN_ID}" --rmw "${RMW_IMPL}" -- ros2 topic list || true)"
if [[ -z "${TOPICS_OUTPUT}" ]]; then
  echo "FAIL: No topics discovered within ${TOPIC_TIMEOUT}s"
  echo "Hints:"
  echo "  - Ensure robot-side ROS2 publisher is running"
  echo "  - Ensure ROS_DOMAIN_ID matches robot"
  echo "  - Ensure ROS_LOCALHOST_ONLY=0"
  echo "  - Disable VPN/virtual NIC and retry"
  exit 1
fi

echo "PASS: Topic list received"

HAS_SPORT=0
HAS_LOW=0
if grep -q '^/\?lf/sportmodestate$' <<<"${TOPICS_OUTPUT}"; then
  HAS_SPORT=1
fi
if grep -q '^/\?lf/lowstate$' <<<"${TOPICS_OUTPUT}"; then
  HAS_LOW=1
fi

echo
echo "[4/4] Go2 expected topic check"
if [[ "${HAS_SPORT}" -eq 1 || "${HAS_LOW}" -eq 1 ]]; then
  echo "PASS: Found Go2 topic(s)"
  [[ "${HAS_SPORT}" -eq 1 ]] && echo "  - lf/sportmodestate"
  [[ "${HAS_LOW}" -eq 1 ]] && echo "  - lf/lowstate"
else
  echo "FAIL: Go2 expected topics not found"
  echo "Found topics (first 30):"
  echo "${TOPICS_OUTPUT}" | head -n 30
  echo "Hint: DDS domain/RMW mismatch is likely."
  exit 1
fi

echo
echo "Result: CONNECTIVITY LOOKS GOOD"
echo "Next command examples:"
echo "  scripts/go2_run.sh --domain ${DOMAIN_ID} --rmw ${RMW_IMPL} -- ros2 launch go2_driver_py driver.launch.py use_rviz:=true"
echo "  scripts/go2_run.sh --domain ${DOMAIN_ID} --rmw ${RMW_IMPL} -- ros2 run go2_twist_bridge twist_bridge"
