#!/bin/sh
set -eu
project=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
[ "$(id -u)" = 0 ]
install -d -m 0755 /usr/libexec/enaptic /usr/share/polkit-1/actions
install -m 0644 "$project"/backend/helper.py "$project"/backend/planner.py "$project"/backend/native_bridge.py "$project"/backend/sources.py /usr/libexec/enaptic/
install -m 0755 "$project"/auth/enaptic-helper /usr/libexec/enaptic/enaptic-helper
install -m 0755 "$project"/build/out/enaptic-transaction /usr/libexec/enaptic/enaptic-transaction
install -m 0644 "$project"/auth/org.auzietek.enaptic.policy /usr/share/polkit-1/actions/org.auzietek.enaptic.policy
