"""
Setup configuration for code analyzer package
"""

from setuptools import find_namespace_packages, setup

setup(
    name="python-code-quality-analyzer",
    version="1.0.0",
    packages=find_namespace_packages(include=["code_analyzer*"]),
    include_package_data=True,
    package_data={
        "code_analyzer": [
            "commands/*.py",
            "config/*.py",
            "metrics/*.py",
            "formatters/*.py",
            "analyzers/*.py",
        ],
    },
    install_requires=[
        "click>=8.1.7",
        "rich>=13.7.0",
        "radon>=6.0.1",
        "pathlib>=1.0.1",
        "typing-extensions>=4.9.0",
        "pyyaml>=6.0.1",
    ],
    entry_points={
        "console_scripts": [
            "code-analyzer=code_analyzer.__main__:cli",
        ],
    },
    author="Kareem Elbahrawy",
    author_email="kareemelbahrawy@gmail.com",
    description="A powerful tool for analyzing Python code complexity, quality, and maintainability",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/kareemaly/python-code-quality-analyzer",
    project_urls={
        "Bug Tracker": "https://github.com/kareemaly/python-code-quality-analyzer/issues",
        "Documentation": "https://github.com/kareemaly/python-code-quality-analyzer#readme",
        "Source Code": "https://github.com/kareemaly/python-code-quality-analyzer",
    },
    keywords="code analysis, complexity, maintainability, quality, metrics, static analysis",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
)
