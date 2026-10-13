# Flatpak browsing adapter

The user authorized shared browsing on October 12, 2026. Provider column and
All/APK/Flatpak selection share the native virtualized catalog and search.
Only APK rows can receive transaction marks; toolbar actions explicitly say
APK. Mark APK Upgrades is unavailable in the Flatpak-only view.

Flatpak CLI queries use explicit unellipsized columns, noninteractive output,
argument arrays and cached remote metadata. Default user and system
installations are read separately. Identity retains kind, app ID, architecture,
branch, origin remote and scope. Branch/scope collisions are not collapsed.
Extra named system installations are not yet included. Missing Flatpak or partial
query failures leave APK browsing available, with warnings in the status tooltip.

Details expose installed runtime, permissions and metadata, or cached remote
metadata for available refs. Displayed AppStream version text can lag the
actual commit; Flatpak decides update status. Cache freshness is stated rather
than promised. Read Cache rereads this data; APK Reload refreshes APK sources.

No Flatpak installation, update, remote edit or authenticated helper extension
is implemented. Those require a separate native Flatpak transaction/review path.
No host packages or remotes are changed by this browsing adapter.

Primary reference: https://docs.flatpak.org/en/latest/flatpak-command-reference.html
Installed command help and real host output verified the selected flags.
