from setuptools import setup, find_packages

setup(
    name="teach-cli",
    version="0.0.1",
    description="A comprehensive teaching assistant CLI platform",
    author="飞少",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "teach=teach.cli:main",
        ],
    },
)
