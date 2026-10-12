# Enaptic working agreement

Read README.md, docs/brief.md, docs/product-design.md, docs/backend-design.md
and docs/task.md before implementation. Follow Synaptic’s recognizable layout
and queued-change workflow using native EFL/Elementary widgets.

Implement APK only. Keep backend operations and capability reporting separate
from widgets; no placeholder APT/DNF implementations. APK owns solving,
signatures, database writes and hooks. The main GUI remains unprivileged.

Review the AUZiX package manager and AlpinE installer as reuse candidates,
not accepted imports. Keep Alpine paths and XDG state; do not inherit AUZiX
filesystem transformations, root-shell construction or repository replacement.

Use the project skills listed in docs/skills.md for the selected slice.
Use edge/BKC for native builds and signed APK publication. Record inputs,
logs and actual acceptance separately from compilation and planning.
Planning does not authorize host package/repository changes. Privileged Apply
must execute the transaction reviewed by the user and revalidate stale plans.

Keep an active objective in docs/task.md. Preserve unrelated projects and
settings. Follow docs/branching.md; do not tag scaffolds as releases.
