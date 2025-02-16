from setuptools import setup, find_packages

setup(
    name="uuidtool",
    version="1.0",
    description="CLI tool to manipulate UUIDs",
    author="crazycat256",
    url="https://github.com/crazycat256/uuidtool",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "uuidtool=uuidtool.cli:main",
        ],
    },
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)