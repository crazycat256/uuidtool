from setuptools import setup, find_packages

setup(
    name="uuidtool",
    version="1.0",
    description="CLI tool to manipulate UUIDs",
    author="crazycat256",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "uuidtool=uuidtool.cli:main",
        ],
    },
    python_requires=">=3.10",
)