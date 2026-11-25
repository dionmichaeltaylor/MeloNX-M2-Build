#!/usr/bin/env bash
set -euo pipefail
PROJECT="src/MeloNX/MeloNX.xcodeproj"
SCHEME="MeloNX"
if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "This script must run on macOS with Xcode installed." >&2
  exit 2
fi
command -v xcodebuild >/dev/null
command -v dotnet >/dev/null
xcodebuild -version
dotnet --info
xcodebuild -resolvePackageDependencies -project "$PROJECT" -scheme "$SCHEME"
DERIVED="${DERIVED_DATA_PATH:-$PWD/.build/DerivedData}"
xcodebuild -project "$PROJECT" -scheme "$SCHEME" -configuration Release -sdk iphoneos -destination 'generic/platform=iOS' -derivedDataPath "$DERIVED" CODE_SIGNING_ALLOWED=NO CODE_SIGNING_REQUIRED=NO build
APP="$DERIVED/Build/Products/Release-iphoneos/MeloNX.app"
test -d "$APP"
OUT="${1:-$PWD/MeloNX-unsigned.ipa}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/Payload"
ditto "$APP" "$TMP/Payload/MeloNX.app"
(cd "$TMP" && /usr/bin/zip -qry "$OUT" Payload)
shasum -a 256 "$OUT"
echo "Created unsigned IPA: $OUT"
