#!/bin/bash
set -e

CHRONOSVERSION=2.3.4

sudo apt-key adv --keyserver keyserver.ubuntu.com --recv E56151BF
DISTRO=$(lsb_release -is | tr '[:upper:]' '[:lower:]')
CODENAME=$(lsb_release -cs)

# Add the repository
echo "deb http://repos.mesosphere.com/${DISTRO} ${CODENAME} main" | 
  sudo tee /etc/apt/sources.list.d/mesosphere.list

sudo apt-get -qq update

sudo apt-get -y --force-yes install mesos chronos=$CHRONOSVERSION*
