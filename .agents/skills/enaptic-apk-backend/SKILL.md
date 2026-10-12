---
name: enaptic-apk-backend
description: Implement or review Enaptic’s APK queries, queued transaction plans and authenticated execution boundary.
---
Read ../../../docs/backend-design.md and ../../../docs/source-review.md.
Inspect the installed APK version and native interfaces before selecting an
adapter. Prefer structured native data; preserve APK version ordering, world
constraints, tags, origins and complete dependency plans.
Keep widgets backend-neutral and implement APK only. A mark is user intent,
not solver acceptance. Mixed changes need one coherent native transaction;
do not substitute separate install/remove loops.
Keep browsing unprivileged. Use argument arrays, a narrow authenticated helper
and native locking/hooks. Revalidate reviewed state before execution and
require a renewed review when resolved changes differ. Never inherit AUZiX
root shell strings, transformed paths or automatic repository replacement.
Verify mutation behavior in disposable roots before selected host acceptance;
report partial failure and .apk-new follow-up without promising rollback.
Planning and read-only work do not authorize host transactions.
