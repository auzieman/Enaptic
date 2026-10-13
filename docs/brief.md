# Product brief

User direction, October 12, 2026: an E-App clone of Synaptic, called Enaptic.
Use familiar package-management controls and layout, styled for Enlightenment.
Avoid a store/dashboard redesign. Native package browsing, updates and queued
transactions are the core; automatic upgrade marking is useful, automatic
installation is not selected.

Target first: AlpinE, Alpine 3.24 x86_64, APK 3.0.8 observed on this host.
Other systems are an architectural consideration, not first-release deliverables.
Read-only Flatpak browsing is now authorized; Flatpak transactions and
service/channel concepts remain separate follow-ups.

Keep an ordinary 12 GB i3 workstation comfortable: virtualized package rows,
asynchronous reads, debounced search, bounded logs and no continuously animated
chrome. Initial performance measurements must report dataset, host and method;
no invented latency or memory results.
