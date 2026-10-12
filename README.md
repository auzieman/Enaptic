# Enaptic

A native EFL package manager for AlpinE, following Synaptic's compact layout
and queued-change workflow. APK is the implemented backend; meta-packages and
Flatpak support are later work.

The current build browses installed/available packages, searches and filters,
queues multiple package marks, previews APK's complete transaction, and offers
confirmed authenticated Apply and Reload. Repositories now has configured
source controls and known compatible choices, with separate signing-key trust.
This is an early implementation, not a tagged release.

## Using Enaptic

Run `build/run.sh` after a native build. `--safe-theme` uses Elementary's
standard theme; the toolbar can switch between standard and system EFL themes.

- Ctrl-click selects several packages. Toolbar marks apply to the selection.
- Double-click toggles an install or available-upgrade mark. Removal is explicit.
- Search uses `+` for AND, `|` for OR, parentheses and quoted literals. AND binds
  first. Fields: `name:`, `description:`, `repo:`, `source:`, `license:`. Quote
  names containing operators, such as `"g++"`. Case folding currently covers ASCII.
- Preview Changes shows requested world changes, solver-added dependencies,
  retained required packages, estimated download size and installed-size delta.
- Apply requires confirmation and administrator authentication. It rejects stale
  package/source state or changed native package identities before committing.
- Reload fetches indexes from enabled repositories and refreshes results and
  available upgrades. It does not install updates. Read Cache only rereads indexes.
- Repositories enables, disables, adds and removes configured HTTPS sources.
  Comments/tags are retained and prior repository files backed up. Custom source
  URLs are supported; cross-release additions are rejected by the interface.
- Known choices include matching Alpine main/community and, on v3.24, the AlpinE
  companion feed. Trust Companion Key is a separate fingerprint-verified action.
  Additional repositories.d files are displayed for inspection, not edited here.

The GUI remains unprivileged. Install the reviewed helper separately with
`sudo sh auth/install-helper.sh`. This writes root-owned files under
`/usr/libexec/enaptic` and a Polkit action under `/usr/share/polkit-1/actions`.
Polkit retains successful active-session authorization temporarily; no password
is stored by Enaptic. Apply/Reload remain unavailable without this helper.
During an operation, progress is shown and normal window closure is blocked.
APK hooks and .apk-new configuration handling remain native APK behavior.
Failures may leave partial package changes; no rollback is promised.

## Build and validation

Maintainer native builds run through edge/BKC using a pinned Alpine/EFL compiler
image. `build/prototype/build.sh` is the pipeline entrypoint. It requires EFL
headers and libapk 3.0.8; retained API headers are under `native/apk-headers`.
The helper deliberately refuses Apply with another APK version until rebuilt.
The pipeline tests native search syntax plus stale-review rejection, installation
and mixed install/removal in a disposable APK root. Python adapter tests run with:

```sh
python3 -m unittest discover -s tests -p 'test_*.py'
```

[Current acceptance](docs/task.md), [feature map](docs/feature-map.md),
[backend design](docs/backend-design.md), [product design](docs/product-design.md)
and [project skills](docs/skills.md) distinguish implementation from validation.
Sorting, broader source discovery and additional package systems remain follow-ups.

## Local speech trial

The first host transaction installed eSpeak NG, Speech Dispatcher, its Python
bindings and Python ONNX Runtime. A local Australian female voice trial uses
**Kirra / magdalena** from Data Craftsman's en_AU LibriVox model. See
[speech setup](docs/speech.md). This is a separate development tool, not an
Enaptic screen reader or a global system voice setting.

## Licensing

Original GUI, Python adapter and tools: GPL-3.0-or-later; see LICENSE. The separate
native solver bridge and retained APK API headers: GPL-2.0-only, compatible with
the libapk they link to; see native/APK-LICENSE and native/UPSTREAM.md. They
communicate with the Python adapter through a process protocol. Voice weights
are not included in source; their CC BY 4.0 attribution stays alongside them.

Companions: [AlpinEifyd](https://github.com/auzieman/AlpinEifyd),
[E-Jamz](https://github.com/auzieman/E-Jamz),
[BlackKnight E Theme](https://github.com/auzieman/BlackKnight-E-Theme).
[Desktop walkthrough](https://youtu.be/JF7gO9Wty5I).
