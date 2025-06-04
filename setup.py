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
    os.path.abspath("torchsparse/backend"), # If headers are included relative to this
    os.path.abspath("third_party/sparsehash/src"),
]

# Platform-specific compiler arguments
if platform.system() == "Windows":
    define_macros += [('SPARSEHASH_WINDOWS', None)]
    extra_compile_args = {
        "cxx": [
            "/MD",
            "/O2",
            "/EHsc",
            "/std:c++17",
            "/Zc:__cplusplus",
        ],
        "nvcc": [
            "-O3",
            "--use-local-env", # Use host compiler environment
            "-std=c++17",
            "-Xcompiler", "/MD", # Pass /MD to host compiler
            "-wd177"  # <--- ADD THIS LINE TO SUPPRESS WARNING 177
        ],
    }
else: # Linux/macOS
    extra_compile_args = {
        "cxx": ["-g", "-O3", "-fopenmp", "-std=c++17"],
        "nvcc": [
            "-O3",
            "-std=c++17",
            "-wd177"  # <--- ADD THIS LINE TO SUPPRESS WARNING 177
        ],
    }

setup(
    name="torchsparse",
    version=version,
    packages=find_packages(),
    ext_modules=[
        extension_type(
            "torchsparse.backend",
            sources,
            include_dirs=include_dirs,
            define_macros=define_macros,
            extra_compile_args=extra_compile_args,
        )
    ],
    url="https://github.com/Stoobs/torchsparse", # Updated to your fork
    install_requires=[
        "numpy",
        "backports.cached_property",
        "tqdm",
        "typing-extensions",
        "wheel",
        "rootpath",
        "torch",
        "torchvision"
    ],
    cmdclass={"build_ext": BuildExtension},
    zip_safe=False,
)