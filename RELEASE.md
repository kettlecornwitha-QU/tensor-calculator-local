# Release Guide

This document is the maintainer checklist for producing downloadable macOS app releases for `tensor_calc`.

## Scope

Current release target:

- Apple Silicon macOS

Current release artifacts:

- `Tensor Calculator.app.zip`
- `SHA256SUMS.txt`

## Before Releasing

Recommended checks:

- run the app locally in development mode
- build the packaged app locally
- open the packaged app on an Apple Silicon Mac
- verify the input wizard can complete a representative calculation
- verify the results pane and detached results window both render correctly
- verify save/load session still works
- verify export still works
- skim the README user-facing instructions

Helpful local checks:

```bash
python3 -m pip install -r requirements.txt
python3 -m gui.app
./package_standalone_app.command
```

## Local Packaging

Use this when you want a local `.app` bundle without publishing a GitHub release.

```bash
python3 -m pip install -r requirements.txt
./package_standalone_app.command
```

Expected output:

- `dist_apps/Tensor Calculator.app`

To zip it manually:

```bash
mkdir -p release_artifacts
ditto -c -k --keepParent "dist_apps/Tensor Calculator.app" "release_artifacts/Tensor Calculator.app.zip"
shasum -a 256 \
  "release_artifacts/Tensor Calculator.app.zip" \
  > "release_artifacts/SHA256SUMS.txt"
```

## GitHub Actions Packaging

Automated packaging is defined in:

- `.github/workflows/macos-app.yml`

The workflow:

- installs Python 3.12
- installs packaging/runtime dependencies from `requirements.txt`
- builds the standalone app
- zips the app
- uploads artifacts
- publishes release assets when a version tag is pushed

## Manual Test Run On GitHub

Use this to verify the workflow without cutting a public release.

Steps:

1. Push your branch to GitHub.
2. Open the repository Actions tab.
3. Run `Build macOS App` using `workflow_dispatch`.
4. Download the uploaded artifacts.
5. Open and test the app on an Apple Silicon Mac.

## Publishing A Release

The workflow publishes release assets automatically when you push a tag matching:

- `v*`

Example:

```bash
git tag v0.1.0
git push origin v0.1.0
```

Expected release assets:

- `Tensor Calculator.app.zip`
- `SHA256SUMS.txt`

## After Publishing

Recommended follow-up:

- download the release assets from GitHub Releases
- verify the checksum
- open the app from the downloaded zip
- confirm the README still matches the release behavior

## Known Assumptions

- packaging is currently built around Apple Silicon runners (`macos-14`)
- `.icns` generation may still fall back to the runtime SVG icon if `iconutil` rejects the generated iconset
- the release artifact is a zipped `.app`, not a notarized installer
