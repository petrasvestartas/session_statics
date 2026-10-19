#!/usr/bin/env bash
# Publish an example's scene to the session viewer under its own name, apart from the live scene.
#
#   bash/publish.sh <name>    data/output/view_<name>.pb   -> pb/view_<name>.pb
#                             data/output/view_<name>.yaml -> scenes/view_<name>.yaml
#
# The example writes both: the geometry and the manifest that names it and carries its texts.
# Open: https://petrasvestartas.github.io/session/?scene=view_<name>.yaml
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
source "$ROOT/../bash/lib/view.sh"

name="${1:?usage: bash/publish.sh <name>}"
geometry="$ROOT/data/output/view_${name}.pb"
manifest="$ROOT/data/output/view_${name}.yaml"
[ -s "$geometry" ] && [ -s "$manifest" ] || { echo "ERROR: run the example first, $geometry or $manifest is missing" >&2; exit 1; }

r2_require_credentials
r2_upload "$geometry" "pb/view_${name}.pb"
r2_upload "$manifest" "scenes/view_${name}.yaml"
r2_notify "view_${name}.pb"
echo "  open:  https://petrasvestartas.github.io/session/?scene=view_${name}.yaml"
