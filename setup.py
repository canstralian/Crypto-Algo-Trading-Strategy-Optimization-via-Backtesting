"""Setup configuration for Crypto Strategy Optimizer."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="crypto-strategy-optimizer",
    version="1.0.0",
    author="Crypto Strategy Optimizer Contributors",
    description="Professional cryptocurrency algorithmic trading strategy optimization via backtesting",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/crypto-strategy-optimizer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "crypto-optimizer=cli:main",
        ],
    },
    include_package_data=True,
    keywords="cryptocurrency trading backtesting algorithmic-trading strategy-optimization",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/crypto-strategy-optimizer/issues",
        "Source": "https://github.com/yourusername/crypto-strategy-optimizer",
        "Documentation": "https://github.com/yourusername/crypto-strategy-optimizer/blob/main/README.md",
    },
)
