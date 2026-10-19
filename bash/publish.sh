#!/usr/bin/env bash
# Publish an example's scene to the session viewer under its own name, apart from the live scene.
#
#   bash/publish.sh <name>    data/output/view_<name>.pb -> pb/revisions/<sha256>.pb (gzip, immutable)
#                             and scenes/view_<name>.yaml naming it: top view, no grid, live
#
# The example writes only the session. As in view_live.sh, the geometry goes to a content-addressed key and
# only the small manifest is overwritten, so no cache can serve an old scene; an open page reloads on the relay.
# Open: https://petrasvestartas.github.io/session/?scene=view_<name>.yaml
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LIB="$ROOT/../bash/lib"
source "$LIB/view.sh"

name="${1:?usage: bash/publish.sh <name>}"
geometry="$ROOT/data/output/view_${name}.pb"
[ -s "$geometry" ] || { echo "ERROR: run the example first, $geometry is missing" >&2; exit 1; }

r2_require_credentials
r2_curl_config
scratch=$(mktemp -d)
trap 'rm -rf "$scratch"; rm -f "${R2_CURL_CONFIG:-}"' EXIT

# geometry: gzip, then a key named by its hash
payload="$scratch/geometry.gz"
gzip -n -6 -c "$geometry" > "$payload"
revision="pb/revisions/$(sha256sum "$payload" | cut -d' ' -f1).pb"
r2_revision "$payload" "$revision" gzip

# manifest: the scene opened from the top, no floor grid, reloaded on every publish, its one item that revision
cat > "$scratch/scene.yaml" <<YAML
{"name": "${name}", "live": true, "view": "top", "grid": false, "items": [{"file": "pb/view_${name}.pb", "name": "${name}", "at": [0, 0, 0]}]}
YAML
python3 "$LIB/view_manifest.py" "$scratch/scene.yaml" "$geometry" "$revision" "$scratch/view_${name}.yaml" gzip
r2_upload "$scratch/view_${name}.yaml" "scenes/view_${name}.yaml"
r2_notify "view_${name}.yaml"
echo "  open:  https://petrasvestartas.github.io/session/?scene=view_${name}.yaml"
