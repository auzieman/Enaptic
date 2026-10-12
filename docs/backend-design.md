# APK-first backend boundary

The UI stores user intent and stable package identities; the adapter owns APK
queries, candidate selection, transaction planning and native results.

| Operation | Result |
| --- | --- |
| capabilities | Supported actions/detail fields, authorization and cancellation behavior |
| list/search | Package identities, installed/candidate versions, status, origin and description |
| details | Available dependencies, files, licenses, size/source data; explicit unavailable fields |
| refresh | Index refresh result and new repository/catalog generation |
| plan(requests) | Native solver’s complete proposed transaction, reasons, constraints and available totals |
| apply(review) | Revalidated approved transaction plus progress, exit status and per-package outcome where available |

Package identity includes name, architecture, version and origin/tag where
relevant. Version ordering belongs to APK, not a generic string comparator.
Keep explicit world selections separate from solver-added dependencies.
Review mixed install/remove/upgrade requests as one native transaction; do not
implement a loop of unrelated `apk add`/`apk del` calls. Determine the appropriate
APK 3 solver interface before implementing mixed Apply.

Initial investigation: APK 3 query/structured output, native simulation and
libapk; evaluate apk-polkit-rs for authenticated execution. These are candidates,
not verified integrations. Prefer structured native data over fragile prose
parsing. Use argument arrays and validated package constraints; no user text
interpolated into a root shell. Do not run the whole GUI as root.

Bind a reviewed transaction to installed state, repository indexes, relevant
configuration, requested constraints and resolved actions. Before applying,
revalidate; if the solver’s plan changes, show a new review. Define binding and
lock behavior against the actual backend before claiming race prevention.

The interface leaves room for APT/DNF later. No implementations, daemon
framework or cross-platform sudo assumption are included in the first scope.

## Implemented native transaction path

APK 3.0.8 metadata is copied into a private root for preview. World constraints
are edited only in that copy; the separately licensed native bridge calls APK's
solver and exposes actual changes, estimates and a canonical identity record.
Identity includes old/new versions and package digests, repository tags and
reinstall status. Required packages retained after removing a world selection
are identified. Mixed installation/removal is one changeset, not a command loop.

The root-owned helper receives only bounded JSON over stdin after Polkit
administrator authorization. It rejects caller commands/paths. It checks the
package/source/key fingerprint before starting, then again after the bridge
opens the live database with APK's exclusive lock. The bridge re-solves and
compares exact native identities, then commits that same changeset without
releasing the lock. World edits remain in memory until APK commits. Package
predownload, signatures, hooks, triggers and protected config handling stay
with APK. Unknown bridge/solver results fail closed. APK 3.0.8 is required.

Root helper code and bridge installation permissions are verified before use.
A fixed safe environment is used; project/user code is not imported as root.
Normal UI closure is refused while a privileged operation is active. The helper
continues draining the native transaction if its GUI output consumer disappears;
no automatic package rollback or transaction cancellation is claimed.

Reload uses authenticated native apk update and reports incomplete refreshes.
Source edits and key trust coordinate with APK's lock. Source files are written
atomically with backups and a stale-file digest check. Comments/tags are retained.
The companion key is fetched over HTTPS and checked against a pinned fingerprint.
Trust and repository activation are separate reviewed operations. repositories.d
is displayed read-only in this implementation. Custom HTTPS sources are allowed;
known choices are restricted to matching branches, with no silent stable/edge mixing.
