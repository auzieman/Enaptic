# Current task — Flatpak browsing and provider selection

User authorized the next browsing slice on October 12, 2026. Keep APK
transactions separate; do not install/update Flatpak refs or edit remotes.
Add Provider column and All/APK/Flatpak selection; retain scope, remote,
architecture, kind and branch identities. Use existing cached remote metadata
and asynchronous catalog reads. Expose partial/missing metadata honestly.
Native edge/BKC runs 65498322-149a-4cad-9c0c-8d7cabf8bd68 and
5294f4dd-16f2-46d1-afb3-2ac9fa5e5a1d completed. Fourteen Python tests passed.
Cached host catalog contains 28,679 APK and 5,939 distinct Flatpak rows, with
six Flatpak updates. Installed/remote ref-prefix normalization is regression
tested. Provider selection/search and installed Chrome details were verified
in the native GUI; APK actions disable for Flatpak-only selection. Installed
Wine Gecko runtime details were also checked through the adapter. The final
interpreted adapter explicitly filters kind during installed lookup.
No Flatpak transactions/remotes or host upgrades were performed.

# Previous task — APK Apply, Reload and repositories

User scope: finish roadmap 1–3. Meta-packages and Flatpak management are deferred.
User explicitly approved root-owned helper and Polkit policy installation after
execution auto-review required approval. The unprivileged GUI retains temporary
Polkit authorization; it never stores passwords or runs as root.

Implemented: authenticated confirmed Apply/Reload, native locked transaction
identity validation, dependency/size previews, configured-source controls,
compatible known-source choices and separate pinned companion-key trust.
Search, multiple selection and batch/double-click marks remain implemented.

Validation: edge/BKC run 6694f33b-fb55-402e-81d9-39aabf4cc464 passed native
compilation/search, altered-review rejection and installation plus mixed
install/removal in a disposable APK root. Ten Python tests passed. A later
layout build is being verified; retain its final receipt separately.
Host helper Reload completed successfully across all three enabled sources.
A reviewed host transaction installed the speech tools and Python bindings:
77 installations, no removals/upgrades, successful APK exit. Detailed local
review/operation logs are retained under build/out. Python bindings import.
Kirra was chosen by the user after generated Australian female samples.

Repository dialog verified at 920×650 with source controls and key details
visible. Confirmation was opened and cancelled without changing sources.
Final native build: 58679c21-c1eb-4db5-bd30-05012d583554; passed compilation,
search and disposable transaction tests. Detailed evidence is in validation.md.
Apply confirmation with the nine pending upgrades was inspected and cancelled.
The canonical project is ~/Projects/Enaptic, with local enaptic/alpine-say
launchers. Validated source was published to auzieman/Enaptic main, development and
feature/apk-apply-and-sources (implementation commit 69b888c). No release
tag/APK publication is part of this pass.
No APK/Flatpak system updates were applied; pending updates are separate work.
No repository activation or signing-key trust change is claimed from the tests.
Future Tek styling remains a separate theme prototype.
