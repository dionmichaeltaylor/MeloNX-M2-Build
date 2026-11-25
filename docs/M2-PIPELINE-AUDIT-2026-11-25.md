# MeloNX M2 pipeline audit — initial findings

Date: 2026-11-25
Target: MeloNX 2.7 / iPad Air M2 / iOS 27.x
Status: source identity pinned in build workflow; call-site audit not yet executed against the checkout

## Source identity and build provenance

The repository's baseline workflow explicitly clones the Starforgejo MeloNX repository and checks out commit `13700519f3abc4e6d7ed8a065b118b2cc59bcd67`, then verifies HEAD before building. This gives us a reproducible candidate source revision. It does **not** yet prove that this exact commit produced the user's installed 2.7 IPA; the build workflow has not yet produced a validated matching binary fingerprint.

The alternate `AzureDominus/melonx` / `XC-ios-ht` source configured in the generic build kit is a mirror/fork and must not be treated as authoritative for this optimization work.

## Confirmed architectural context

- MeloNX uses the Ryujinx-derived renderer and Vulkan through MoltenVK on iOS.
- MeloNX exposes a Shader Cache setting.
- The CPU-side Profiled Persistent Translation Cache (PTC) is separate from GPU shader/pipeline caching. PTC improves translated CPU-code reuse; it is not evidence that Vulkan pipeline caches persist.
- MoltenVK translates SPIR-V to MSL and compiles Metal libraries. A serialized Vulkan pipeline cache may retain MSL source, but a warm cache file can still incur Metal compilation when loaded.
- The previous broad MoltenVK global-lock patch is rejected for now: the experimental build crashed at BOTW's Nintendo splash screen, while the stock-MoltenVK control reached open-world gameplay around 30 FPS.

## Longshot research applied carefully

Longshot PR #650 describes per-worker pipeline caches during *dedicated preparation phases*, merged only after workers join. Its MoltenVK path also disables saved Vulkan pipeline-cache files because reload can serialize Metal library compilation. The PR reports strong synthetic throughput gains on an M4 Max / MoltenVK 1.4.2, but explicitly calls for a game A/B at the rebased head. Those results are not a prediction for iPad Air M2 or MeloNX.

Longshot PR #652 adds a compiler-service-aware precompile handoff: allow the title/game to start while slow compilation continues behind it, and log slow compiles. PR #664 bounds very large compute compiles so they do not occupy every worker. These are useful later-stage ideas, not safe first patches.

## Work performed in this repository

- Added a source-tree audit script to inventory pipeline-cache API calls, shader/pipeline creation sites, MoltenVK build flags, and concurrency/lifecycle hints.
- Added a runtime-log analyzer that counts explicitly logged cache, pipeline, shader, memory, validation, device-loss, and crash events. Counts are heuristic and cannot prove API calls that the app does not log.
- Added an observed-pipeline warm-up design contract. It defines a local-only metadata schema and strict compatibility/failure rules. It is not yet wired into the emulator runtime.

## Next actions

1. Run `scripts/audit-pipeline-cache.sh <official-source-checkout>` against the pinned source commit. Trace cache ownership, persistence, and worker lifecycle from the actual call sites.
2. Capture a verbose runtime log from the stock-MoltenVK control using a repeatable BOTW route; analyze it with `scripts/analyze-vulkan-log.py <log>`. Add native counters only at verified call sites.
3. Implement a capture-only pipeline-key recorder after identifying canonical pipeline descriptors and local shader-module lifetime. Do not implement replay until the key is stable and cache compatibility checks are proven.

## Non-goals for this phase

- No MoltenVK lock rewrite.
- No cache-file copying between installations/devices.
- No distribution of game-specific shaders, keys, ROMs, or pipeline binaries.
- No claim of FPS improvement until repeated on-device A/B trials.
