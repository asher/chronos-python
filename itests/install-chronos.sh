#!/bin/bash
set -e

# Default version of chronos to test against if not set by the user
[[ -f /root/chronos-version ]] && source /root/chronos-version
CHRONOSVERSION="${CHRONOSVERSION:-2.4.0}"

sudo apt-key adv --keyserver keyserver.ubuntu.com --recv E56151BF
DISTRO=$(lsb_release -is | tr '[:upper:]' '[:lower:]')
CODENAME=$(lsb_release -cs)

# Add the repository
echo "deb http://repos.mesosphere.com/${DISTRO} ${CODENAME} main" | 
  sudo tee /etc/apt/sources.list.d/mesosphere.list

sudo apt-get -qq update

sudo apt-get -y --force-yes install mesos chronos=$CHRONOSVERSION*
