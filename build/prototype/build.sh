#!/bin/sh
set -eu
mkdir -p build/out
cc -std=gnu11 -Wall -Wextra -O2 -I native/apk-headers native/transaction.c -o build/out/enaptic-transaction -Wl,-l:libapk.so.3.0.0
cc -std=gnu11 -Wall -Wextra -O2 src/enaptic.c -o build/out/enaptic $(pkg-config --cflags --libs elementary)
cc -std=gnu11 -Wall -Wextra tests/search.c -o build/out/test-search
build/out/test-search
sh build/prototype/test-transaction.sh
apk info -v > build/out/compiler-packages.txt
sha256sum src/enaptic.c src/search.h backend/apk_backend.py backend/planner.py native/transaction.c build/out/enaptic-transaction build/out/enaptic > build/out/SHA256SUMS
echo 'COMPLETE: native Enaptic browser compiled; search grammar tests passed.'
