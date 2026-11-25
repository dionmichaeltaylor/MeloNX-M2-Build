#!/usr/bin/env python3
"""Summarize MeloNX/Ryujinx/MoltenVK runtime logs without modifying them.

Usage: python3 scripts/analyze-vulkan-log.py path/to/emulator.log
The parser is intentionally heuristic; inspect the matched lines before treating
counts as authoritative performance metrics.
"""
from __future__ import annotations
import collections
import json
import re
import sys
from pathlib import Path

PATTERNS = {
    "pipeline_cache_create": re.compile(r"vkCreatePipelineCache|CreatePipelineCache", re.I),
    "pipeline_cache_data_read": re.compile(r"vkGetPipelineCacheData|GetPipelineCacheData", re.I),
    "pipeline_cache_merge": re.compile(r"vkMergePipelineCaches|MergePipelineCaches", re.I),
    "graphics_pipeline_create": re.compile(r"vkCreateGraphicsPipelines|CreateGraphicsPipelines", re.I),
    "compute_pipeline_create": re.compile(r"vkCreateComputePipelines|CreateComputePipelines", re.I),
    "shader_module_create": re.compile(r"vkCreateShaderModule|CreateShaderModule", re.I),
    "shader_compile": re.compile(r"shader.{0,30}(compil|translat)|SPIR.?V.{0,30}(MSL|compil)|Metal.{0,30}compil", re.I),
    "cache_hit": re.compile(r"cache.{0,20}hit|hit.{0,20}cache", re.I),
    "cache_miss": re.compile(r"cache.{0,20}miss|miss.{0,20}cache", re.I),
    "memory_warning": re.compile(r"memory warning|memory pressure|allocation failed|out of memory|VK_ERROR_OUT_OF_DEVICE_MEMORY", re.I),
    "device_lost": re.compile(r"VK_ERROR_DEVICE_LOST|device lost", re.I),
    "validation_error": re.compile(r"validation error|VUID-", re.I),
    "crash_or_fatal": re.compile(r"fatal|uncaught exception|abort\(|segmentation fault|crash", re.I),
}
def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    counts = collections.Counter()
    samples = collections.defaultdict(list)
    total = 0
    for number, line in enumerate(path.read_text(errors="replace").splitlines(), 1):
        total += 1
        for key, pattern in PATTERNS.items():
            if pattern.search(line):
                counts[key] += 1
                if len(samples[key]) < 8:
                    samples[key].append({"line": number, "text": line[:500]})
    report = {
        "source_file": str(path),
        "total_lines": total,
        "counts": dict(counts),
        "samples": dict(samples),
        "limitations": [
            "Counts reflect logged messages, not Vulkan API calls unless the application logs each call.",
            "No matches do not prove an operation is absent; release builds may omit verbose logging.",
            "Use identical logging settings and test routes for A/B comparisons."
        ]
    }
    out = path.with_suffix(path.suffix + ".m2-analysis.json")
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"analysis": str(out), "total_lines": total, "counts": dict(counts)}, indent=2))
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
