"""
FΦRS33 Quantum Optimizer - Setup Configuration
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fors33",
    version="1.2.0",
    author="Joshua Hartman",
    description="FΦRS33 Quantum Optimizer: Topology-Aware Error Mitigation with Cloud Telemetry",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fors33/qcr",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "qiskit>=1.0.0",
        "qiskit-ibm-runtime>=0.15.0",
        "networkx>=3.0",
        "numpy>=1.20.0",
        "requests>=2.28.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "flake8>=6.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "fors33=fors33.core:main",
        ],
    },
)
