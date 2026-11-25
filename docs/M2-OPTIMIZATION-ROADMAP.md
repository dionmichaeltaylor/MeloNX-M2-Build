# MeloNX M2 Optimization Roadmap

Status: research and implementation plan  
Target: iPad Air M2, iOS 27.x, MeloNX 2.7 baseline  
Working branch: `m2-optimization-roadmap`

## Known-good baseline

The stock-MoltenVK control IPA boots Breath of the Wild and reaches open-world gameplay on the target iPad at approximately 30 FPS, with brief reported dips to 24–26 FPS. The earlier experimental MoltenVK lock patch reached the Nintendo splash screen but crashed before gameplay. Treat that patch as **rejected pending redesign**; do not use it as the base for the next test.

Keep the user's original MeloNX installation and the stock-MoltenVK control build untouched. Every experiment must have a distinct build identity and a rollback path.

## What we are borrowing from Longshot

Longshot's pipeline-state-list design records pipeline keys observed during real gameplay, ships a compact list of those keys, and reconstructs the pipelines locally from the user's own shader data before gameplay. This avoids shipping copyrighted game shaders and avoids first-use pipeline creation during play.

Longshot's MoltenVK-specific worker-cache work takes a different approach from our first patch: each preparation worker uses its own pipeline cache, then the worker caches are merged after the workers join. Its author also disables saved MoltenVK pipeline-cache load/save because reading a saved MoltenVK cache can still trigger serial Metal library compilation. We must not blindly transplant this design: MeloNX/Ryujinx has a different renderer lifecycle and may share caches during active gameplay.

## Technical facts and constraints

- MeloNX is a C#/Swift iOS emulator based on Ryujinx. Its GPU path uses Vulkan through MoltenVK; its CPU path already has a Profiled Persistent Translation Cache (PTC).
- MoltenVK's SPIR-V to MSL conversion and Metal library compilation are distinct costs. MoltenVK documentation describes pipeline-cache serialization as a way to retain MSL shader source, but this only helps if the application actually creates, saves, and reloads a compatible Vulkan pipeline cache.
- A pipeline cache is device/driver/build sensitive. Never copy arbitrary cache blobs between different MoltenVK builds or devices without checking the cache header/UUID and handling rejection safely.
- Game-specific pipeline keys or shader data must be generated from the user's own game session. Do not package game ROMs, keys, shader binaries, or copyrighted assets in CI artifacts.
- The previous global-lock patch changed multiple synchronization paths at once and failed the BOTW boot test. It is not an acceptable candidate for another blind rebuild.

## Roadmap and gates

### M0 — Reproducible baseline and diagnostics (first)
1. Preserve a stock-MoltenVK control.
2. Record exact IPA hash, MoltenVK version/hash, device/iOS, game title/update, graphics settings, and JIT method for each run.
3. Capture emulator logs around startup, shader compilation, pipeline creation, and the crash point.
4. Record frame-time percentiles and stutter events, not only average FPS.
5. Record cache directory layout and whether the app actually calls `vkGetPipelineCacheData` / `vkCreatePipelineCache`.

**Gate:** a repeatable BOTW open-world run and a useful log from the same session.

### M1 — Persistent cache audit (first implementation target)
1. Trace Ryujinx/MeloNX pipeline-cache creation, lifetime, serialization, and reload.
2. Confirm whether MoltenVK is built with pipeline-cache serialization support (`MVK_USE_CEREAL`) and whether MeloNX persists the cache.
3. Add safe, versioned cache metadata: GPU/device identity, MoltenVK version, pipeline-cache UUID, app build, and schema version.
4. On mismatch or corruption, discard the cache and rebuild; never fail game startup because a cache is stale.
5. Add counters for cache hits/misses, bytes read/written, conversion time, and Metal library compile time where feasible.

**Gate:** prove cache reuse across two launches without changing rendered output or introducing startup regressions.

### M2 — Pipeline warm-up based on observed use
1. Investigate whether the renderer can record pipeline keys seen in normal play.
2. Store only keys/metadata generated locally from the user's own session.
3. On later launches, warm only pipelines that can be reconstructed from valid local shader/module data.
4. Bound warm-up by time and memory budget; prioritize frequently used pipelines.
5. Never assume Longshot's binary pipeline-state format or precompiled list can be reused directly.

**Gate:** fewer first-use pipeline stalls on a repeatable route, with no missing draws or crashes.

### M3 — Conservative compilation concurrency
1. First profile whether pipeline creation is actually serialized in MeloNX's workload.
2. Prototype per-worker pipeline caches only in a dedicated shader-preparation phase where worker ownership is explicit.
3. Merge worker caches only after workers have joined; do not merge concurrently with writes.
4. Keep the active gameplay cache path unchanged in the first prototype.
5. If per-worker caches are impossible, prototype narrowly scoped per-shader-module locking in a separate branch with stress tests for cache reads, writes, merges, duplicate shader modules, and destruction.

**Gate:** build succeeds, validation/stress tests pass, and BOTW passes the same boot and traversal test as stock MoltenVK. No performance claim without repeated A/B measurements.

### M4 — Memory and missing-render investigation
1. Instrument guest memory, MoltenVK resource allocation, Metal heap usage, and eviction events.
2. Reproduce the reported invisible terrain/objects with exact location, settings, and logs.
3. Determine whether the symptom is missing draw submission, shader/pipeline readiness, texture residency, or resource eviction.
4. Change one allocator/budget policy at a time. Do not simply raise memory limits.
5. Keep a conservative fallback path for devices without the required memory capabilities.

**Gate:** the same scene renders correctly over repeated visits and extended play, with no increase in crashes or memory pressure.

## Benchmark protocol

For each build, use the same save, docked mode, resolution, VSync, and graphics settings. Record:
- cold launch and time to first controllable frame;
- first traversal of a fixed route;
- second traversal of the same route;
- two fast travels;
- 20–30 minutes of play;
- frame-time p50/p95/p99, shader/pipeline compile counts, cache hits/misses, peak memory, and crash logs.

Run at least three comparable trials per build where practical. Distinguish cold shader cache from warm shader cache. Do not compare different cache states as if they were equivalent.

## Immediate next engineering task

Audit the MeloNX/Ryujinx GPU pipeline-cache path and MoltenVK build flags before writing another concurrency patch. The first code change should be observability or a safe cache-lifecycle fix, not another broad lock rewrite.
