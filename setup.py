"""
Setup configuration for Multi-Agent Content Generation System.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="kasparro-agentic-content-generation",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Multi-Agent Content Generation System for product pages",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/kasparro-ai-agentic-content-generation-system",
    packages=find_packages(exclude=["tests*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "pydantic>=2.5.0",
        "pydantic-settings>=2.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.7.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "generate-content=agents.orchestrator:main",
        ],
    },
)
