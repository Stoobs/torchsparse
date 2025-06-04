import glob
import os
import platform

import torch
import torch.cuda
from setuptools import find_packages, setup
from torch.utils.cpp_extension import (
    CUDA_HOME,
    BuildExtension,
    CppExtension,
    CUDAExtension,
)

version_file = open("./torchsparse/version.py")
version = version_file.read().split("'")[1]
print("torchsparse version:", version)

if (torch.cuda.is_available() and CUDA_HOME is not None) or (
    os.getenv("FORCE_CUDA", "0") == "1"
):
    device = "cuda"
    pybind_fn = f"pybind_{device}.cu"
else:
    device = "cpu"
    pybind_fn = f"pybind_{device}.cpp"

sources = [os.path.join("torchsparse", "backend", pybind_fn)]
for fpath in glob.glob(os.path.join("torchsparse", "backend", "**", "*")):
    if (fpath.endswith("_cpu.cpp") and device in ["cpu", "cuda"]) or (
        fpath.endswith("_cuda.cu") and device == "cuda"
    ):
        sources.append(fpath)

extension_type = CUDAExtension if device == "cuda" else CppExtension

# Define macros and include directories
define_macros = []
include_dirs = [
    os.path.abspath("torchsparse/backend"),
    # Add path to vendored sparsehash headers
    os.path.abspath("third_party/sparsehash/src"),
]

# Platform-specific compiler arguments
if platform.system() == "Windows":
    define_macros += [('SPARSEHASH_WINDOWS', None)] # For sparsehash
    # For MSVC C++ compiler
    extra_compile_args = {
        "cxx": [
            "/MD",       # Use the multithreaded, DLL-specific version of the run-time library
            "/O2",       # Optimization for speed
            "/EHsc",     # Enable C++ EH (no SEH exceptions)
            "/std:c++17",# Explicitly set C++17 standard
            "/Zc:__cplusplus", # Ensure __cplusplus macro is correct
            # "/MP",     # Optional: build with multiple processes
        ],
        "nvcc": ["-O3", "--use-local-env", "-std=c++17", "-Xcompiler", "/MD"], # Added --use-local-env and /MD for nvcc
    }
else: # Linux/macOS
    extra_compile_args = {
        "cxx": ["-g", "-O3", "-fopenmp", "-std=c++17"], # Added -std=c++17 for consistency
        "nvcc": ["-O3", "-std=c++17"],
    }
    # On Linux, -lgomp is usually handled by PyTorch's build system or not needed if OpenMP is part of the toolchain.
    # If you face linker errors for OpenMP, you might need to add extra_link_args=['-lgomp']

setup(
    name="torchsparse",
    version=version,
    packages=find_packages(),
    ext_modules=[
        extension_type(
            "torchsparse.backend",
            sources,
            include_dirs=include_dirs, # Add include_dirs here
            define_macros=define_macros, # Add define_macros here
            extra_compile_args=extra_compile_args,
        )
    ],
    url="https://github.com/mit-han-lab/torchsparse", # Consider changing to your fork Stoobs/torchsparse
    install_requires=[
        "numpy",
        "backports.cached_property", # For Python < 3.8
        "tqdm",
        "typing-extensions",
        "wheel",
        "rootpath",
        "torch", # PyTorch will be installed by your GHA workflow
        "torchvision", # Torchvision will be installed by your GHA workflow
    ],
    # dependency_links is deprecated, PyTorch should be installed via pip from the specified index in GHA.
    # dependency_links=[
    #     'https://download.pytorch.org/whl/cu126'
    # ],
    cmdclass={"build_ext": BuildExtension},
    zip_safe=False,
)