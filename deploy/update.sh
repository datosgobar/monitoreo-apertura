#!/usr/bin/env bash
set -e;

ssh_port=""
checkout_branch=""
host=""
login_user=""

usage() {
	echo "Usage: `basename $0`" >&2
	echo "(-s ssh_port)" >&2
	echo "(-b checkout branch)" >&2
	echo "(-h host to be provisioned) (-l login_user )"; >&2
}
if ( ! getopts "s:b:h:l:" opt); then
    usage;
	exit $E_OPTERROR;
fi

while getopts "s:b:h:l:" opt;do
	case "$opt" in
	s)
	  ssh_port="$OPTARG"
      ;;
	b)
	  checkout_branch="$OPTARG"
      ;;
	h)
	  host="$OPTARG"
      ;;
	l)
	  login_user="$OPTARG"
      ;;
	\?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      exit 1
      ;;
	esac
done

if [ ! "$ssh_port" ] || [ ! "$checkout_branch" ]  || [ ! "$host" ] || [ ! "$login_user" ]
then
    echo "Missing options..."
    usage
    exit 1
fi


extra_vars="ansible_port=$ssh_port \
        checkout_branch=$checkout_branch \
        ansible_user=$login_user"

echo "INFO: Running tasks with tag: quickly"
ansible-playbook site.yml --extra-vars "$extra_vars" -i "$host," --tags "quickly" --ask-sudo-pass
