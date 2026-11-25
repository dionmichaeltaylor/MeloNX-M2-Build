# MeloNX M2 Build Kit

A reproducible iOS build workflow for MeloNX. The Apple build runs on a GitHub-hosted macOS runner with Xcode; ChatGPT's Linux environment cannot run Apple's iOS SDK or xcodebuild.

## Run the build

1. Open **Actions**.
2. Select **Build MeloNX iOS IPA**.
3. Choose **Run workflow**.
4. Keep the defaults for the first test: source `AzureDominus/melonx`, ref `XC-ios-ht`, runner `xcode-27`.
5. Start the run and download the `MeloNX-iOS-unsigned-...` artifact when it completes.

The artifact includes the unsigned IPA, SHA-256 checksum, source commit, and Xcode build log. The xlarge runner may cost more; check GitHub Actions billing first.

## Limitations and provenance

- The output is an **unsigned IPA**. Sign it using your trusted sideloading workflow (such as FlareStore). No Apple signing credentials are stored here.
- No emulator optimizations are applied in this first stage; this establishes a repeatable build pipeline.
- The selected source is the public mirror/fork `AzureDominus/melonx`, branch `XC-ios-ht`. Its relationship to authoritative Starforgejo sources and the installed 2.7 binary has not been verified. Confirm provenance before treating it as a production/performance fork.
- A successful archive/build is not yet demonstrated. After the first run, inspect the logs and test the signed app on the iPad.

## Source snapshot notes

The inspected snapshot documents macOS/Xcode/.NET 8 and contains `src/MeloNX/MeloNX.xcodeproj` with scheme `MeloNX`. A legacy `Ryujinx` target invokes `distribution/ios/xc-compile.sh`. The inspected .NET project targets `net8.0` / `ios-arm64`, enables Native AOT and Tiered PGO, and declares `-flto -Ofast -funroll-loops`. These are observations about that snapshot, not proof it exactly matches the installed app.

## Local helper

On macOS with Xcode and .NET 8 installed, run `scripts/build-unsigned-ipa.sh` from a checkout of the selected source tree.
