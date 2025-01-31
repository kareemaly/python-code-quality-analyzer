"""
Setup configuration for code analyzer package
"""

from setuptools import setup, find_packages

setup(
    name="code-analyzer",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click>=8.1.7",
        "rich>=13.7.0",
        "radon>=6.0.1",
        "pathlib>=1.0.1",
        "typing-extensions>=4.9.0",
    ],
    entry_points={
        "console_scripts": [
            "code-analyzer=code_analyzer.__main__:cli",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool for analyzing Python code complexity and quality",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/code-analyzer",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
) 