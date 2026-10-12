#!/bin/sh
set -eu
fixture=$(mktemp -d)
trap 'rm -rf "$fixture"' EXIT
mkdir -p "$fixture/etc/apk" "$fixture/var/cache/apk"
printf '%s\n' 'https://dl-cdn.alpinelinux.org/alpine/v3.24/main' > "$fixture/etc/apk/repositories"
apk --root "$fixture" --keys-dir /etc/apk/keys --initdb --scripts=no --commit-hooks=no add alpine-baselayout >/dev/null
request() {
 world="$1"; identity="$2"
 printf '0\n%s\n%s0\n%s\n%s' "$(printf %s "$world" | wc -c)" "$world" "$(printf %s "$identity" | wc -c)" "$identity"
}
world=$(printf 'alpine-baselayout\nzlib\nX');world=${world%X}
request "$world" '' | build/out/enaptic-transaction plan "$fixture" > "$fixture/plan"
identity=$(sed -n '/^IDENTITY$/,/^END_IDENTITY$/{ /^IDENTITY$/d; /^END_IDENTITY$/d; p; }' "$fixture/plan"; printf X);identity=${identity%X}
# A deliberately altered review must reject before any package mutation.
if request "$world" 'tampered' | build/out/enaptic-transaction apply-test "$fixture" > "$fixture/reject" 2>&1; then exit 1; fi
! apk --root "$fixture" info -e zlib >/dev/null 2>&1
request "$world" "$identity" | build/out/enaptic-transaction apply-test "$fixture" > "$fixture/commit"
apk --root "$fixture" info -e zlib >/dev/null
# Mixed removal/install is one changeset: remove zlib, add libbz2.
world=$(printf 'alpine-baselayout\nlibbz2\nX');world=${world%X}
request "$world" '' | build/out/enaptic-transaction plan "$fixture" > "$fixture/plan"
identity=$(sed -n '/^IDENTITY$/,/^END_IDENTITY$/{ /^IDENTITY$/d; /^END_IDENTITY$/d; p; }' "$fixture/plan"; printf X);identity=${identity%X}
request "$world" "$identity" | build/out/enaptic-transaction apply-test "$fixture" > "$fixture/mixed"
! apk --root "$fixture" info -e zlib >/dev/null 2>&1
apk --root "$fixture" info -e libbz2 >/dev/null
cat "$fixture/reject" "$fixture/commit" "$fixture/mixed" > build/out/transaction-test.log
printf '%s\n' 'PASS: native stale-plan rejection, install and mixed install/removal in disposable root.'
