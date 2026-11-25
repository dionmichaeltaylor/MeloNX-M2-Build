#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-.}"
OUT="${2:-m2-pipeline-audit}"
mkdir -p "$OUT"

if [[ ! -d "$ROOT/src" ]]; then
  echo "Expected a MeloNX source checkout at: $ROOT" >&2
  exit 2
fi

# Capture exact source identity so audit findings are tied to a reproducible tree.
{
  git -C "$ROOT" rev-parse HEAD 2>/dev/null || echo "unknown"
  git -C "$ROOT" status --short 2>/dev/null || true
} > "$OUT/source-identity.txt"

# Find pipeline-cache lifecycle and pipeline creation call sites. Keep source lines
# intact; this is an inventory, not an automatic patcher.
rg -n -i --glob '*.{cs,cpp,h,hpp,m,mm,swift}' \
  'vk(Create|Get|Merge|Destroy)PipelineCache|PipelineCacheCreateInfo|pipelineCache|pipeline cache' \
  "$ROOT/src" > "$OUT/pipeline-cache-call-sites.txt" || true

rg -n -i --glob '*.{cs,cpp,h,hpp,m,mm,swift}' \
  'vkCreate(Graphics|Compute)Pipelines|CreateGraphicsPipelines|CreateComputePipelines|ShaderModule|SPIR-V|SPIRV|Metal.*(compile|library)|newLibraryWithSource|newLibraryWithData' \
  "$ROOT/src" > "$OUT/pipeline-and-shader-call-sites.txt" || true

rg -n -i --glob '*.{cs,cpp,h,hpp,m,mm,swift,xcconfig,pbxproj,cmake,txt,sh}' \
  'MVK_USE_CEREAL|MoltenVK|pipelineCache|ShaderCache|shader cache|PipelineCache' \
  "$ROOT/src" "$ROOT/distribution" > "$OUT/moltenvk-and-build-config.txt" || true

rg -n -i --glob '*.{cs,cpp,h,hpp,m,mm,swift}' \
  'SemaphoreSlim|Channel<|Task\.Run|Parallel\.ForEach|Task\.WhenAll|DispatchQueue|NSOperationQueue|ThreadPool|Create.*Pipeline' \
  "$ROOT/src" > "$OUT/concurrency-and-lifecycle-hints.txt" || true

echo "Audit complete: $OUT"
echo "Review pipeline-cache-call-sites.txt first, then trace ownership and synchronization."
