"""Setup configuration for the Crypto Trading Platform."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="crypto-trading-platform",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Production-grade cryptocurrency algorithmic trading and backtesting platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/Crypto-Algo-Trading-Strategy-Optimization-via-Backtesting",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "pytest-asyncio>=0.21.1",
            "black>=23.12.1",
            "flake8>=6.1.0",
            "pylint>=3.0.3",
            "mypy>=1.7.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "crypto-trading=src.cli:main",
        ],
    },
)
