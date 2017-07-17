#!/usr/bin/env bash
set -e;

ssh_port=""
checkout_branch=""
postgresql_user=""
postgresql_password=""
host=""
login_user=""
update=""

usage() {
	echo "Usage: `basename $0`" >&2
	echo "(-s ssh_port) (-b checkout branch)" >&2
	echo "(-p postgresql db user) (-P postgresql db password)" >&2
	echo "(-h host to be provisioned) (-l login_user )[-u]"; >&2
}
if ( ! getopts "s:b:p:P:h:l:u" opt); then
    usage;
	exit $E_OPTERROR;
fi

while getopts "s:b:p:P:h:l:u" opt;do
	case "$opt" in
	s)
	  ssh_port="$OPTARG"
      ;;
	b)
	  checkout_branch="$OPTARG"
      ;;
	p)
	  postgresql_user="$OPTARG"
      ;;
	P)
	  postgresql_password="$OPTARG"
      ;;
	h)
	  host="$OPTARG"
      ;;
	l)
	  login_user="$OPTARG"
      ;;
	u)
	  update="1"
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

if [ ! "$ssh_port" ] || [ ! "$host" ] || [ ! "$login_user" ] \
    || [ ! "$checkout_branch" ] || [ ! "$postgresql_user" ] || [ ! "$postgresql_password" ]
then
    echo "Missing options..."
    usage
    exit 1
fi


extra_vars="checkout_branch=$checkout_branch \
        ansible_user=$login_user \
        ansible_port=$ssh_port \
        postgresql_user=$postgresql_user \
        postgresql_password=$postgresql_password"

if [ -z "$update" ]; then
    ansible-playbook site.yml --extra-vars "$extra_vars" -i "$host," --ask-sudo-pass
else
    echo "INFO: Running tasks with tag: quickly"
    ansible-playbook site.yml --extra-vars "$extra_vars" -i "$host," --tags "quickly" --ask-sudo-pass
fi
