# Observed-pipeline warm-up design (MeloNX M2)

Status: design contract only; no runtime pipeline capture has been wired in yet.

## Why this is the first Longshot idea to adapt

Longshot's observed pipeline-state list is useful because it records *which pipeline configurations were used*, then reconstructs them locally from the user's own shader/module data. It does not require shipping game shaders or ROM-derived binaries. This is conceptually safer for MeloNX than copying Longshot's binary cache format or blindly sharing MoltenVK cache blobs.

## Proposed local record format (schema 1)

One JSON Lines record per observed pipeline:

- `schema`: integer, initially 1
- `renderer_build`: MeloNX/Ryujinx source revision or app build fingerprint
- `gpu_family`: device GPU family (not a user identifier)
- `moltenvk_version`: runtime MoltenVK version
- `pipeline_cache_uuid`: Vulkan physical-device pipeline cache UUID
- `pipeline_kind`: graphics or compute
- `pipeline_key_hash`: stable hash of canonical pipeline create parameters
- `shader_module_keys`: local references/hashes to shader modules already held in the local cache
- `last_seen_unix_ms`: last observation time
- `use_count`: local count, saturating integer

Do not serialize raw game assets, shader source, SPIR-V, keys, title IDs, save data, or copyrighted content into a shareable manifest.

## Replay contract

1. Validate schema, renderer build compatibility, GPU family, MoltenVK version, and pipeline-cache UUID.
2. Resolve every shader module key against the local shader/module cache.
3. Reconstruct the pipeline using the normal renderer pipeline creation path.
4. On any missing module, validation error, incompatible identity, or creation failure, skip the record and continue normal gameplay.
5. Warm-up is time- and memory-bounded; prioritize high-use records and stop before foreground frame deadlines are threatened.
6. Record warm-up attempts, successful creations, skips, failures, elapsed time, and peak memory.

## Required source audit before implementation

- Identify the actual pipeline creation wrappers and canonical descriptor structures.
- Determine whether the renderer already has a stable pipeline key/hash.
- Trace shader module lifetime and whether modules survive long enough to reconstruct pipelines.
- Identify a safe point before gameplay where the render device and shader cache are ready.
- Establish whether the existing pipeline cache already performs the same work, to avoid duplicate caches.

## First prototype gate

Capture records during a repeatable BOTW route, restart the app, replay only locally resolvable records, and compare cold/warm route frame-time p95/p99 over at least three trials. No record may be replayed across a mismatched renderer build or pipeline-cache UUID. A failed warm-up must never prevent game launch.
