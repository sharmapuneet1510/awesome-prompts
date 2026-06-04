"""Setup script for token_optimizer"""

from setuptools import setup, find_packages

setup(
    name="token_optimizer",
    version="1.0.0",
    description="Intelligent query analysis before Claude dispatch",
    author="Claude Code",
    author_email="noreply@anthropic.com",
    python_requires=">=3.8",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8+",
    ],
)
