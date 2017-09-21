#!/bin/sh
set -e
cd /app
ARG=$(echo "$1" | tr "[:upper:]" "[:lower:]")

do_db_init() {
  python init_db.py
}

mkindex() {
  test -d /app/index || mkdir -p /app/index
  sqluri=$(grep ^sqluri servicebook.ini | awk '{print $NF}')
  if test -n "${sqluri}"; then
    if echo "${sqluri}" | grep -q 0.0.0.0; then
      echo "DB not configured" >&2
      exit 0
    else
      servicebook-reindex \
        --sqluri "${sqluri}" \
        --whoosh-root /app/index/
    fi
  else
    echo "DB not configured" >&2 && exit 0
  fi
}

start_app() {
  uwsgi --ini uwsgi.ini
}

case "$ARG" in
  "start")
    do_db_init
    mkindex
    start_app
    exit
  ;;
  "dbinit")
    do_db_init
    exit
  ;;
  "index")
    mkindex
    exit
  ;;
  *)
    exec $ARG
  ;;
esac
