---
name: e-native-apk-release
description: Build and prepare Enaptic’s native Alpine APK through edge BKC pipelines and verified signed repository publication.
---
Read ../../../docs/task.md and the workspace’s AlpinE/AGENTS.md and
AlpinE/docs/companion-apks.md before packaging. Use native abuild/APK on a
pinned Alpine release and record compiler, sources, checksums and dependencies.
Current signing/build home is edge; retired lab/factory targets are not defaults.
Reuse prepared inputs only after identity/checksum verification. Retain stable
logs; source compilation, package installation and UI/transaction acceptance
are distinct. Test installed launchers and assets, not just build-tree paths.
Keep the GUI unprivileged and document helper policy as part of the package.
Private signing material stays on edge outside source/artifacts/public content.
Preserve notices and publish the public-key fingerprint and install instructions.
A new feed must not silently replace existing repository trust. Publication
follows the current authorized task scope; scaffold creation alone is not a
release request.
