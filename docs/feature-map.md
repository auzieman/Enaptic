# Delivery and acceptance

| Slice | Features | Acceptance | State |
| --- | --- | --- | --- |
| EN-001 | Source/backend review and Synaptic layout reference | Record actual reusable code, API choices, license origins and reference screenshots | Preliminary source review complete; full upstream/layout review continues |
| EN-002 | Read-only native browser | Real installed/available data, origin and version columns, search/filter/sort, responsive virtualized list; no privileged mutations | Implemented; user accepted formatting/search; broader sorting remains open |
| EN-003 | Marks and transaction review | Install/remove/upgrade requests, native complete plan, dependencies, totals where available, stale-plan handling | Implemented native preview with estimated totals and identity binding |
| EN-004 | Authenticated Apply and Reload | Narrow helper, native locking/hooks, progress/errors, reconciliation, .apk-new follow-up; disposable-root evidence before host tests | Implemented; disposable-root and host helper trials passed |
| EN-005 | Update workflow and repositories | Mark All Upgrades, preserved sources, explicit key trust; no silent release mixing | Implemented source controls and known catalog; auto-mark preference deferred |
| EN-006 | Native APK distribution | Edge/BKC build, source/license notices, signed feed, installation/runtime evidence | Planned |

| EN-007 | Flatpak browsing and search | Explicit APK/Flatpak source badges and filters, remote identity, user/system scope, separate details and transaction reviews | Implemented read-only catalog/filter/details; native provider selection and installed details verified |

Design-only: future package-system adapters. Deferred: Flatpak installation,
background update service, unattended installation and download-only operation
until backend capability is established.

## Next delivery order

1. Finish EN-004 authenticated APK Apply and Reload. Reload pulls current
   indexes from enabled sources, then refreshes catalog/search/upgrades; it
   does not install upgrades. Review and revalidate the native transaction
   before Apply. Show progress, errors and partial refresh results clearly.
2. Expand EN-005 from informative repository details into source management:
   enable/disable configured sources, add/remove sources, and show refresh
   status, source URLs and signing-key fingerprints. Preserve comments, tags
   and existing entries; repository edits and key trust are distinct reviewed
   operations through the narrow authenticated helper.
3. Add a curated known-source catalog with release/architecture compatibility,
   provenance and explicit trust steps. Include the AlpinE companion feed.
   Do not invent a generic non-free switch or silently mix stable with edge.
   Verify each suggested source before offering it for activation.
4. Design companion-feed meta-packages for desktop, audio and development
   bundles. APK resolves their dependencies using already enabled sources.
   Meta-packages do not silently add repositories or trust signing keys.
   Package definitions/publication require their own edge/BKC validation.
5. Add EN-007 Flatpak search/browsing as a distinct adapter after the APK path
   is usable. Mark backend and remote on every result, distinguish user and
   system installations, and keep APK/Flatpak reviews separate. Search uses
   configured remotes; adding a remote is an explicit source-management step.

First host Apply trial remains a reviewed local text-to-speech installation.
Future Tek styling stays a separate theme prototype; native system-theme
following and a safe standard fallback remain Enaptic's appearance baseline.
