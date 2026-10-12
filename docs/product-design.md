# Synaptic-style interface

| Area | Initial behavior |
| --- | --- |
| Menu/toolbar | Reload, Mark All Upgrades, Apply; search and Preferences |
| Left filters | All, installed, not installed, upgradable, broken, marked; origin; sections when metadata exists |
| Package table | Status icon/check, package name, installed version, candidate version, short description |
| Lower details | Description, dependencies/reverse dependencies, installed files, repository/source, license and sizes when available |
| Context menu | Mark install, removal, upgrade, reinstall or version selection when APK adapter supports the action |
| Status bar | Visible/total packages, marked actions, freshness, active operation |
| Apply review | Requested actions and solver-added changes, removals, download size, disk change, warnings and confirmation |

Use one main window with resizable sidebar/details pane. Keyboard selection,
search, sorting, scrolling and context menus must work on large catalogs.
Missing metadata is explicitly unavailable, not guessed from names. Alpine
does not necessarily supply Debian-style sections or installed-file metadata
for packages that have not been downloaded.

## Reload and upgrades

Reload refreshes enabled repository indexes, then updates the view. Offer an
explicit preference to automatically mark available upgrades after a successful
reload; first default remains manual marking until user preference is settled.
Mark All Upgrades obtains APK’s proposed upgrade transaction. Existing marks
must be reconciled visibly rather than silently replaced. Apply remains separate.
Prefetch/download-only is a distinct capability to investigate; never describe
index refresh as downloading or installing the upgrades themselves.

## Repository controls

Show enabled URL, Alpine branch/release, tag, architecture applicability and
trusted-key fingerprint. Editing sources and trusting keys are distinct actions.
Preserve existing repository entries, comments and constraints. Explain candidate
origin and dependency origins. Do not silently add edge/testing to a stable host.
Current host sources: Alpine v3.24 main/community and the AlpinE base feed.
The new companion feed is published but not configured on this host.

## Authentication and transaction state

Read-only browsing does not prompt for root. Authenticate only for operations
requiring privilege. Planned states: reading, refreshing, marked, solving,
review-ready, authenticating, applying, completed, failed, stale.
UI remains responsive and permits only one active transaction. Cancellation
during a native transaction is supported only where APK can safely provide it;
closing a window must not blindly kill package hooks or imply rollback.
Report partial failures honestly, retain bounded logs and surface .apk-new
configuration follow-up. Filesystem changes and hooks are not generally reversible.

## Extended sources and bundles

Repository management includes configured-source toggles, add/remove controls,
refresh status, and a curated catalog of verified compatible sources. Display
source trust separately from activation. Offer AlpinE companion packages as
ordinary APK results, including future meta-package bundles with inspectable
dependencies.

Future Flatpak results share the search surface but carry explicit backend,
remote and user/system scope. Provide source filters and separate details and
transaction reviews; do not treat Flatpak as another APK repository.
