"""
Setup configuration for code analyzer package
"""

from setuptools import setup, find_packages

setup(
    name="python-code-quality-analyzer",
    version="0.4.0",
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
    author="Kareem Elbahrawy",
    author_email="kareem3d.a@gmail.com",
    description="A powerful tool for analyzing Python code complexity, quality, and maintainability",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/kareem3d/code-analyzer",
    project_urls={
        "Bug Tracker": "https://github.com/kareem3d/code-analyzer/issues",
        "Documentation": "https://github.com/kareem3d/code-analyzer#readme",
        "Source Code": "https://github.com/kareem3d/code-analyzer",
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