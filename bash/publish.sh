#!/usr/bin/env bash
# Publish an example's scene to the session viewer under its own name, apart from the live scene.
#
#   bash/publish.sh <name>    data/output/view_<name>.pb   -> pb/revisions/<sha256>.pb (gzip, immutable)
#                             data/output/view_<name>.yaml -> scenes/view_<name>.yaml, naming that revision
#
# The example writes both: the geometry and the manifest that names it and carries its texts, view and
# live flag. As in view_live.sh, the geometry goes to a content-addressed key and only the small manifest
# is overwritten, so no cache can serve an old scene; a page with the scene open reloads on the relay.
# Open: https://petrasvestartas.github.io/session/?scene=view_<name>.yaml
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LIB="$ROOT/../bash/lib"
source "$LIB/view.sh"

name="${1:?usage: bash/publish.sh <name>}"
geometry="$ROOT/data/output/view_${name}.pb"
manifest="$ROOT/data/output/view_${name}.yaml"
[ -s "$geometry" ] && [ -s "$manifest" ] || { echo "ERROR: run the example first, $geometry or $manifest is missing" >&2; exit 1; }

r2_require_credentials
r2_curl_config
scratch=$(mktemp -d)
trap 'rm -rf "$scratch"; rm -f "${R2_CURL_CONFIG:-}"' EXIT

# geometry: gzip, then a key named by its hash
payload="$scratch/geometry.gz"
gzip -n -6 -c "$geometry" > "$payload"
revision="pb/revisions/$(sha256sum "$payload" | cut -d' ' -f1).pb"
r2_revision "$payload" "$revision" gzip

# manifest: the same scene with its item pointed at that revision
python3 "$LIB/view_manifest.py" "$manifest" "$geometry" "$revision" "$scratch/view_${name}.yaml" gzip
r2_upload "$scratch/view_${name}.yaml" "scenes/view_${name}.yaml"
r2_notify "view_${name}.yaml"
echo "  open:  https://petrasvestartas.github.io/session/?scene=view_${name}.yaml"
