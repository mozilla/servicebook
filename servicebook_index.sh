#!/bin/sh -x


mkindex() {
  sqluri=$(grep servicebook_db servicebook.ini | awk '{print $NF}')
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

mkdir /app/index
if test -f servicebook.ini; then
    mkindex && exit 0
else
  echo "Can't continue without app configuration" >&2
fi
