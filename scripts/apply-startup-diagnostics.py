from pathlib import Path

path = Path("src/MeloNX/MeloNX/App/UI/MeloNXApp.swift")
source = path.read_text()

old = """    static func initializeEmulatorRuntime(environment: [EnvironmentVariable]) {
        runtimeInitializationLock.lock()
        defer { runtimeInitializationLock.unlock() }

        guard !didInitializeEmulatorRuntime else { return }
        didInitializeEmulatorRuntime = true

        SDL_SetMainReady()
        SDL_iPhoneSetEventPump(SDL_TRUE)
        SDL_Init(SDL_INIT_EVENTS | SDL_INIT_AUDIO)

        environment.forEach { env in
            env.set()
        }
        
        EnvironmentVariable(string: "HAS_TXM", value: ProcessInfo.processInfo.hasTXM && !ProcessInfo.processInfo.isiOSAppOnMac ? "1" : "0").set()

        RyujinxBridge.initialize()
        
        let cool: Bool
        if #available(iOS 19, *) {
            if ProcessInfo.processInfo.hasTXM {
                NativeSettingsManager.shared.setting(forKey: "DUAL_MAPPED_JIT", default: true).value = true
            }
            
            cool = NativeSettingsManager.shared.setting(forKey: "DUAL_MAPPED_JIT", default: true).value
        } else {
            cool = NativeSettingsManager.shared.setting(forKey: "DUAL_MAPPED_JIT", default: false).value
        }
        
        JIT26BreakpointHandler()
        
        if cool {
            EnvironmentVariable(string: "DUAL_MAPPED_JIT", value: "1").set()
            LaunchGameHandler.succeededJIT = RyujinxBridge.initialize_dualmapped()
        } else {
            EnvironmentVariable(string: "DUAL_MAPPED_JIT", value: "0").set()
        }
    }
"""

replacement = """    static func initializeEmulatorRuntime(
        environment: [EnvironmentVariable],
        onStage: ((String) -> Void)? = nil
    ) {
        onStage?("Waiting for runtime initialization lock")
        runtimeInitializationLock.lock()
        defer { runtimeInitializationLock.unlock() }

        guard !didInitializeEmulatorRuntime else {
            onStage?("Runtime was already initialized")
            return
        }
        didInitializeEmulatorRuntime = true

        onStage?("Initializing SDL")
        SDL_SetMainReady()
        SDL_iPhoneSetEventPump(SDL_TRUE)
        SDL_Init(SDL_INIT_EVENTS | SDL_INIT_AUDIO)

        onStage?("Applying runtime environment")
        environment.forEach { env in
            env.set()
        }
        
        EnvironmentVariable(string: "HAS_TXM", value: ProcessInfo.processInfo.hasTXM && !ProcessInfo.processInfo.isiOSAppOnMac ? "1" : "0").set()

        onStage?("Initializing native Ryujinx bridge")
        RyujinxBridge.initialize()
        
        let cool: Bool
        if #available(iOS 19, *) {
            if ProcessInfo.processInfo.hasTXM {
                NativeSettingsManager.shared.setting(forKey: "DUAL_MAPPED_JIT", default: true).value = true
            }
            
            cool = NativeSettingsManager.shared.setting(forKey: "DUAL_MAPPED_JIT", default: true).value
        } else {
            cool = NativeSettingsManager.shared.setting(forKey: "DUAL_MAPPED_JIT", default: false).value
        }
        
        onStage?("Initializing JIT breakpoint handler")
        JIT26BreakpointHandler()
        
        if cool {
            onStage?("Initializing dual-mapped JIT")
            EnvironmentVariable(string: "DUAL_MAPPED_JIT", value: "1").set()
            LaunchGameHandler.succeededJIT = RyujinxBridge.initialize_dualmapped()
            onStage?("Dual-mapped JIT initialization returned")
        } else {
            EnvironmentVariable(string: "DUAL_MAPPED_JIT", value: "0").set()
            onStage?("Dual-mapped JIT is disabled")
        }
        
        onStage?("Native runtime initialization finished")
    }
"""

if old not in source:
    raise SystemExit("Could not locate exact runtime initialization function; refusing to patch.")

source = source.replace(old, replacement)

old_view = """struct EmulatorRuntimeView<Content: View>: View {
    private let content: Content

    init(environment: [EnvironmentVariable], @ViewBuilder content: () -> Content) {
        MeloNXApp.initializeEmulatorRuntime(environment: environment)
        self.content = content()
    }

    var body: some View {
        content
    }
}
"""

new_view = """struct EmulatorRuntimeView<Content: View>: View {
    private let content: Content
    private let environment: [EnvironmentVariable]
    @State private var startupStage = "Preparing startup diagnostics"
    @State private var initialized = false

    init(environment: [EnvironmentVariable], @ViewBuilder content: () -> Content) {
        self.environment = environment
        self.content = content()
    }

    var body: some View {
        Group {
            if initialized {
                content
            } else {
                VStack(spacing: 16) {
                    ProgressView()
                    Text("MeloNX startup diagnostics")
                        .font(.headline)
                    Text(startupStage)
                        .font(.footnote)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal)
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
            }
        }
        .task {
            let stageBinding = $startupStage
            await Task.detached(priority: .userInitiated) {
                MeloNXApp.initializeEmulatorRuntime(environment: environment) { stage in
                    DispatchQueue.main.async {
                        stageBinding.wrappedValue = stage
                    }
                }
            }.value
            startupStage = "Native runtime initialized; loading interface"
            initialized = true
        }
    }
}
"""

if old_view not in source:
    raise SystemExit("Could not locate exact EmulatorRuntimeView; refusing to patch.")

path.write_text(source.replace(old_view, new_view))
print("Applied staged startup diagnostics to MeloNXApp.swift")
