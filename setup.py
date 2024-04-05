# 05.04.2024

from pathlib import Path
from setuptools import setup, find_packages

base_dir = Path(__file__).resolve().parent


# Read version
version = {}
version_file = base_dir / "SpotDown" / "upload" / "version.py"
with open(version_file, encoding="utf-8") as f:
    exec(f.read(), version)


# Read requirements
requirements_file = base_dir / "requirements.txt"
with open(requirements_file, encoding="utf-8") as f:
    install_requires = f.read().splitlines()


# Read README.md
readme_file = base_dir / "README.md"
with open(readme_file, encoding="utf-8") as f:
    long_description = f.read()


setup(
    name="SpotDown",
    version=version["__version__"],
    author="Arrowar",
    author_email="author@example.com",
    description="A command-line program to download music",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Arrowar/spotdown",
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            "spotdown=SpotDown.main:run",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
