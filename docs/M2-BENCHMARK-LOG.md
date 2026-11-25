# M2 A/B benchmark log

Use one row per trial. Do not compare cold-cache runs with warm-cache runs.

| Date/time | Build label | IPA SHA-256 | MoltenVK version/hash | iPad/iOS | Game/update | Cache state (cold/warm) | JIT method | Docked/resolution/VSync | First controllable frame (s) | Route duration (min) | FPS p50 | FPS p95 | Frame-time p99 (ms) | Stutter count | Fast travels | Peak memory (if available) | Crash/log notes |
|---|---|---|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| | Stock control | | Stock | iPad Air M2 / iOS 27.x | BOTW | | StikDebug + universal.js | Docked / 1x / Switch | | | | | | | | | |

## Fixed test sequence

1. Cold launch and time to first controllable frame.
2. Traverse the same route for 10 minutes.
3. Repeat the route for 10 minutes.
4. Perform two fast travels.
5. Continue for another 10 minutes.
6. Note invisible terrain, missing objects, flicker, audio issues, and crashes.

Record graphics settings and game update exactly. Keep the original stock control unchanged.
