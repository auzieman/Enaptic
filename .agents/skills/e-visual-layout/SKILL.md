---
name: e-visual-layout
description: Design and review Enaptic’s Synaptic-style native EFL package table, filters, details and transaction views.
---
Read ../../../docs/product-design.md and ../../../docs/task.md. Use Synaptic’s
recognizable toolbar/sidebar/table/lower-details structure and queued Apply
workflow. Inspect a concrete reference and current implementation before edits.
Use shared blue-metal/ice-blue accents where appropriate while keeping dense
package text conventional, compact and readable. Native virtualized widgets
and keyboard/scroll/focus behavior matter more than decorative chrome.
Preview normal and constrained sizes, long names, empty/error/loading states
and large catalogs. Distinguish fixtures from real backend data. Record how
previews and runtime measurements were produced; compilation is not visual
acceptance. Keep static resources cached and background activity bounded.
Origin: adapted from media-player’s e-visual-layout skill; package-manager
layout takes precedence over player/rack and desktop-scene choices.
