#!/usr/bin/env python3
"""Apply low-overhead M2 Vulkan capability diagnostics to the pinned MeloNX source."""
from pathlib import Path

path = Path("source/src/Ryujinx.Graphics.Vulkan/PipelineCacheManager.cs")
text = path.read_text()
anchor = """            _createFlags = SupportsNonBlockingPipelineCreation
                ? PipelineCacheCreateFlags.ExternallySynchronizedBitExt
                : 0;
"""
replacement = anchor + """            bool pipelineCreationCacheControlExtension =
                physicalDevice.IsDeviceExtensionPresent("VK_EXT_pipeline_creation_cache_control");
            PhysicalDeviceProperties deviceProperties = physicalDevice.PhysicalDeviceProperties;
            Logger.Notice.PrintMsg(
                LogClass.Gpu,
                $"M2 Vulkan diagnostics: GPU={physicalDevice.DeviceName}; " +
                $"vendor=0x{deviceProperties.VendorID:X4}; device=0x{deviceProperties.DeviceID:X4}; " +
                $"driverVersion=0x{deviceProperties.DriverVersion:X8}; " +
                $"pipelineCreationCacheControlExtension={pipelineCreationCacheControlExtension}; " +
                $"pipelineCreationCacheControlFeature={SupportsNonBlockingPipelineCreation}; " +
                $"nonBlockingPipelineCreationEnabled={SupportsNonBlockingPipelineCreation}; " +
                $"pipelineWorkers={workerCount}; pipelineCaches={workerCount + 1}.");
"""
if text.count(anchor) != 1:
    raise SystemExit(f"Expected exactly one PipelineCacheManager insertion point; found {text.count(anchor)}")
if "M2 Vulkan diagnostics:" in text:
    raise SystemExit("Diagnostics already applied; refusing duplicate patch")
path.write_text(text.replace(anchor, replacement))
print("Applied M2 Vulkan capability diagnostics to PipelineCacheManager.cs")
