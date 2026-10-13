# Validation — October 12, 2026

Final edge/BKC run: 58679c21-c1eb-4db5-bd30-05012d583554; status complete.
Source bundle SHA256: 4960378fa5e6b4690662dd6fe1550e41a7d55e8a1aefb651a0ba93f1b5e511d4.
Native compiler image: sha256:95b932cbd2899218225a6783074acfba1cd26abae142f1ec26ba8f13c3c83f8f.

Native compilation and search tests passed. Disposable APK-root tests rejected
a changed review without installation, then installed zlib and applied a mixed
zlib removal/libbz2 installation through one native changeset.
Ten Python adapter/source-validation tests passed on host Python 3.14.

The host helper and Polkit policy were installed after explicit user approval.
Real Reload succeeded for all three enabled sources. The host speech trial
completed 77 installations with no removals or upgrades, through the reviewed
helper, with successful APK exit. This host trial used existing sudo
authorization to invoke the same installed helper; interactive Polkit password
entry has not been end-to-end acceptance tested. Policy inspection confirms
auth_admin_keep for an active session.

Repository dialog checked at 920×650; source controls and key fingerprints are
visible. Source confirmation was opened and cancelled; sources and key trust
were not changed. Main package table, Ctrl-selection and double-click marks
were exercised natively; a nine-package upgrade preview completed. The Apply
confirmation was opened, its package changes/totals inspected and Cancel used.
No pending host upgrade was committed.

Speech Dispatcher and ONNX Runtime Python imports passed. The Australian
voice trial generated WAV output using two inference threads; the user chose
Kirra after hearing samples. The weights, config, model card, upstream
attribution and revision/hash receipt are stored locally and not in Git.

Nine APK packages and six Flatpak components remained pending at the final
check. No host upgrade was applied, and no Flatpak management implementation
is claimed. This is source publication, not a tagged binary/APK release.

## Flatpak browsing follow-up

Native build 5294f4dd-16f2-46d1-afb3-2ac9fa5e5a1d completed; native search
and disposable APK transaction checks still pass. Fourteen Python tests pass
with the final interpreted Flatpak adapter. Full provider identities are distinct:
5,939 Flatpak rows and six updates on this host, plus 28,679 APK rows.
Installed and remote ref formats normalize before merging; scope/origin/branch
remain distinct. Native All/APK/Flatpak selection, search and installed Chrome
details were exercised. Installed Wine Gecko runtime details were checked
separately after making installed lookup explicitly filter ref kind.
Flatpak-only selections cannot mark packages through APK controls.
No Flatpak changes, source edits or host upgrades were executed.
