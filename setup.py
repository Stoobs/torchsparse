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

# Check CUDA environment
if os.name == 'nt':  # Windows
    cuda_path = os.getenv('CUDA_PATH')
    if cuda_path and os.path.exists(os.path.join(cuda_path, 'bin', 'nvcc.exe')):
        os.environ['CUDA_HOME'] = cuda_path

if (torch.cuda.is_available() and CUDA_HOME is not None) or (
    os.getenv("FORCE_CUDA", "0") == "1"
):
    device = "cuda"
    pybind_fn = f"pybind_{device}.cu"
    
    # Verify nvcc is accessible
    import subprocess
    try:
        nvcc_version = subprocess.check_output(['nvcc', '--version'], 
                                             stderr=subprocess.STDOUT,
                                             universal_newlines=True)
        print("NVCC version found:", nvcc_version.split('\n')[0])
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        print("Warning: NVCC not found in PATH. Please ensure CUDA is properly installed.")
        print(f"CUDA_HOME: {CUDA_HOME}")
        print(f"PATH: {os.environ.get('PATH', '')}")
        if not os.getenv("FORCE_CUDA", "0") == "1":
            print("Falling back to CPU build...")
            device = "cpu"
            pybind_fn = f"pybind_{device}.cpp"
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
    os.path.abspath("third_party/sparsehash/src"), # Keep for dense_hash_map etc.
    os.path.abspath("third_party/sparsehash/src/sparsehash/internal")
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
            "--use-local-env",
            "-std=c++17",
            "-Xcompiler", "/MD",
            "-w"  # Disable Warnings
        ],
    }
else: # Linux/macOS
    extra_compile_args = {
        "cxx": ["-g", "-O3", "-fopenmp", "-std=c++17"],
        "nvcc": [
            "-O3",
            "-std=c++17",
            "-w"  # Disable Warnings
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
    url="https://github.com/Stoobs/torchsparse",
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