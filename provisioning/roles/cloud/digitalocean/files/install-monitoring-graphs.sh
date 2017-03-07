#!/bin/sh
set -e
#
# This script is meant for quick & easy install via:
#   'curl -sSL https://do-agent.sh | sh'
# or:
#   'wget -qO- https://do-agent.sh | sh'

supported_distros="Ubuntu 14 or higher, Debian 8, or Centos 6 higher"

command_exists() {
  command -v "$@" > /dev/null 2>&1
}

# Check if this is a forked Linux distro
check_forked() {

  # Check for lsb_release command existence, it usually exists in forked distros
  if command_exists lsb_release; then
    # Check if the `-u` option is supported
    set +e
    lsb_release -a -u > /dev/null 2>&1
    lsb_release_exit_code=$?
    set -e

    # Check if the command has exited successfully, it means we're in a forked distro
    if [ "$lsb_release_exit_code" = "0" ]; then
      # Print info about current distro
      cat <<-EOF
      You're using '$lsb_dist' version '$dist_version'.
EOF

      # Get the upstream release info
      lsb_dist=$(lsb_release -a -u 2>&1 | tr '[:upper:]' '[:lower:]' | grep -E 'id' | cut -d ':' -f 2 | tr -d '[[:space:]]')
      dist_version=$(lsb_release -a -u 2>&1 | tr '[:upper:]' '[:lower:]' | grep -E 'codename' | cut -d ':' -f 2 | tr -d '[[:space:]]')

      # Print info about upstream distro
      cat <<-EOF
      Upstream release is '$lsb_dist' version '$dist_version'.
EOF
    else
      if [ -r /etc/debian_version ] && [ "$lsb_dist" != "ubuntu" ]; then
        # We're Debian and don't even know it!
        lsb_dist=debian
        dist_version="$(cat /etc/debian_version | sed 's/\/.*//' | sed 's/\..*//')"
        case "$dist_version" in
          8|'Kali Linux 2')
            dist_version="jessie"
          ;;
          7)
            dist_version="wheezy"
          ;;
        esac
      fi
    fi
  fi
}

track_dist() {
  if command_exists curl; then
    #Only include the droplet_id if it was run from a droplet
    droplet_id=$(curl -m 1 http://169.254.169.254/metadata/v1/id 2> /dev/null || true)
    if [ "$droplet_id" = "" ]; then
      droplet=""
    else
      droplet="\"droplet_id\":${droplet_id}, "
    fi

    curl -s -X POST https://api.segment.io/v1/track \
      -H "Content-Type: application/json" \
      -H "Authorization: Basic NjVJcDJyYkpYcUVSWTFJeEUwSFZOQmQ2U0htR3QyMEMK" \
      -d "{\"anonymousId\": \"nobody\", \"type\": \"track\", \"properties\": {${droplet}\"os\": \"${1}\"}, \"event\": \"Agent Install Attempt\",\"writeKey\": \"65Ip2rbJXqERY1IxE0HVNBd6SHmGt20C\" }" > /dev/null
  fi
}

install_yum() {
  $sh_c 'echo "
[digitalocean-agent]
name=DigitalOcean agent
baseurl=https://repos.sonar.digitalocean.com/yum/\$basearch
failovermethod=priority
enabled=1
gpgcheck=1
gpgkey=https://repos.sonar.digitalocean.com/sonar-agent.asc
" > /etc/yum.repos.d/digitalocean-agent.repo'
  $sh_c 'rpm --import https://repos.sonar.digitalocean.com/sonar-agent.asc'
  $sh_c 'yum install do-agent -y'
}

install_apt() {
  $sh_c 'apt-get update'
  # Debian8.3 does not include https support out of the box
  $sh_c 'apt-get install -y apt-transport-https'
  $sh_c 'curl https://repos.sonar.digitalocean.com/sonar-agent.asc | apt-key add -'
  $sh_c 'echo "deb https://repos.sonar.digitalocean.com/apt main main" > /etc/apt/sources.list.d/digitalocean-agent.list'
  $sh_c 'apt-get update'
  $sh_c 'apt-get install do-agent -y'
}

do_install() {
  user="$(id -un 2>/dev/null || true)"

  sh_c='sh -c'
  if [ "$user" != 'root' ]; then
    if command_exists sudo; then
      sh_c='sudo -E sh -c'
    elif command_exists su; then
      sh_c='su -c'
    else
      cat >&2 <<-'EOF'
      Error: this installer needs the ability to run commands as root.
      We are unable to find either "sudo" or "su" available to make this happen.
EOF
      exit 1
    fi
  fi

  # perform some very rudimentary platform detection
  lsb_dist=''
  dist_version=''
  if command_exists lsb_release; then
    lsb_dist="$(lsb_release -si)"
  fi
  if [ -z "$lsb_dist" ] && [ -r /etc/lsb-release ]; then
    lsb_dist="$(. /etc/lsb-release && echo "$DISTRIB_ID")"
  fi
  if [ -z "$lsb_dist" ] && [ -r /etc/debian_version ]; then
    lsb_dist='debian'
  fi
  if [ -z "$lsb_dist" ] && [ -r /etc/fedora-release ]; then
    lsb_dist='fedora'
  fi
  if [ -z "$lsb_dist" ] && [ -r /etc/oracle-release ]; then
    lsb_dist='oracleserver'
  fi
  if [ -z "$lsb_dist" ]; then
    if [ -r /etc/centos-release ] || [ -r /etc/redhat-release ]; then
      lsb_dist='centos'
    fi
  fi
  if [ -z "$lsb_dist" ] && [ -r /etc/os-release ]; then
    lsb_dist="$(. /etc/os-release && echo "$ID")"
  fi

  lsb_dist="$(echo "$lsb_dist" | tr '[:upper:]' '[:lower:]')"

  case "$lsb_dist" in

    ubuntu)
      if command_exists lsb_release; then
        dist_version="$(lsb_release --codename | cut -f2)"
      fi
      if [ -z "$dist_version" ] && [ -r /etc/lsb-release ]; then
        dist_version="$(. /etc/lsb-release && echo "$DISTRIB_CODENAME")"
      fi
    ;;

    debian)
      dist_version="$(cat /etc/debian_version | sed 's/\/.*//' | sed 's/\..*//')"
      case "$dist_version" in
        8)
          dist_version="jessie"
        ;;
        7)
          dist_version="wheezy"
        ;;
      esac
    ;;

    oracleserver)
      # need to switch lsb_dist to match yum repo URL
      lsb_dist="oraclelinux"
      dist_version="$(rpm -q --whatprovides redhat-release --queryformat "%{VERSION}\n" | sed 's/\/.*//' | sed 's/\..*//' | sed 's/Server*//')"
    ;;

    fedora|centos)
      dist_version="$(rpm -q --whatprovides redhat-release --queryformat "%{VERSION}\n" | sed 's/\/.*//' | sed 's/\..*//' | sed 's/Server*//')"
    ;;

    *)
      if command_exists lsb_release; then
        dist_version="$(lsb_release --codename | cut -f2)"
      fi
      if [ -z "$dist_version" ] && [ -r /etc/os-release ]; then
        dist_version="$(. /etc/os-release && echo "$VERSION_ID")"
      fi
    ;;


  esac

  # Send OS to Segment so we know what to support in the future.
  track_dist "${lsb_dist}-${dist_version}"

  # Check if this is a forked Linux distro
  check_forked

  # Run setup for each distro accordingly
  case "$lsb_dist" in
    amzn)
        cat >&2 <<-'EOF'

          You appear to be trying to install the DigitalOcean agent on Amazon Linux. This is not yet supported, but might be in the future :)

EOF
      exit 0
      ;;

    debian)
      if [ "$dist_version" = "jessie" ]; then
        install_apt
        exit 0
      fi
      echo "Debian ${dist_version} is not currently supported. Try ${supported_distros}."
      exit 1
      ;;

    ubuntu)
      if [ "$dist_version" = "trusty" ] || [ "$dist_version" = "wily" ] || [ "$dist_version" = "xenial" ] || [ "$dist_version" = "yakkety" ]; then
        install_apt
        exit 0
      fi
      echo "Ubuntu ${dist_version} is not currently supported. Try ${supported_distros}."
      exit 1
      ;;

    centos)
      if [ "$dist_version" = "7" ] || [ "$dist_version" = "6" ]; then
        install_yum
        exit 0
      fi
      echo "Centos ${dist_version} is not currently supported. Try ${supported_distros}."
      exit 1
      ;;

    gentoo|'suse linux'|sle[sd]|'opensuse project'|opensuse|debian|oraclelinux|fedora)
        cat >&2 <<-'EOF'

          You appear to be trying to install the agent on an unsupported Operating System.
          While in Beta, we are only supporting ${supported_distros}.

EOF
      exit 0
      ;;
  esac

  cat >&2 <<-'EOF'

    Either your platform is not easily detectable, is not supported by this
    installer script or does not yet have a package for DigitalOcean's Agent.
    Please email dobeta@digitalocean.com to request support for this OS.

EOF
  exit 1
}

# wrapped up in a function so that we have some protection against only getting
# half the file during "curl do-agent.sh | sh"
do_install
