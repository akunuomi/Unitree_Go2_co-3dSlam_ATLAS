#!/usr/bin/env bash

# Source this file to load ROS2 + workspace env and DDS settings for Go2 LAN control.
# Example:
#   source scripts/go2_env.sh
#   source scripts/go2_env.sh 0 rmw_cyclonedds_cpp

# Defaults can be overridden before sourcing:
#   export GO2_ROS_SETUP=/opt/ros/humble/setup.bash
#   export GO2_DOMAIN_ID=0
#   export GO2_RMW=rmw_cyclonedds_cpp
#   export GO2_LOCALHOST_ONLY=0

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  echo "Please source this file instead of executing it."
  echo "Use: source scripts/go2_env.sh [domain_id] [rmw]"
  exit 1
fi

_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
_WORKSPACE_DIR="$(cd "${_SCRIPT_DIR}/.." && pwd)"

GO2_ROS_SETUP="${GO2_ROS_SETUP:-/opt/ros/humble/setup.bash}"
GO2_DOMAIN_ID="${1:-${GO2_DOMAIN_ID:-0}}"
GO2_RMW="${2:-${GO2_RMW:-rmw_cyclonedds_cpp}}"
GO2_LOCALHOST_ONLY="${GO2_LOCALHOST_ONLY:-0}"

if [[ ! -f "${GO2_ROS_SETUP}" ]]; then
  echo "ROS setup not found: ${GO2_ROS_SETUP}"
  return 1
fi

# shellcheck disable=SC1090
source "${GO2_ROS_SETUP}"

if [[ -f "${_WORKSPACE_DIR}/install/setup.bash" ]]; then
  # shellcheck disable=SC1091
  source "${_WORKSPACE_DIR}/install/setup.bash"
else
  echo "Workspace setup not found: ${_WORKSPACE_DIR}/install/setup.bash"
  echo "Build first: colcon build"
  return 1
fi

export ROS_DOMAIN_ID="${GO2_DOMAIN_ID}"
export ROS_LOCALHOST_ONLY="${GO2_LOCALHOST_ONLY}"
export RMW_IMPLEMENTATION="${GO2_RMW}"

printf 'GO2 env loaded: ROS_DOMAIN_ID=%s, ROS_LOCALHOST_ONLY=%s, RMW_IMPLEMENTATION=%s\n' \
  "${ROS_DOMAIN_ID}" "${ROS_LOCALHOST_ONLY}" "${RMW_IMPLEMENTATION}"
