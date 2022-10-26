from setuptools import find_packages, setup

# Use README.md as the long_description for the package
with open("README.md", "r") as readme_file:
    long_description = readme_file.read()

setup(
    name="pyOSPParser",
    version="0.4.6",
    url="https://github.com/kevinksyTRD/pyOSPParser",
    description="A module to parse or deploy XML/JSON files for Open Simulation Platform.",
    long_description_content_type="text/markdown",
    long_description=long_description,
    license="Apache License 2.0",
    classifiers=[
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
    ],
    project_urls={
        "Source": "https://github.com/kevinksyTRD/pyOSPParser",
        "Bug Reports": "https://github.com/kevinksyTRD/pyOSPParser/issues",
    },
    packages=find_packages(),
    include_package_data=True,
    setup_requires=[
        'xmlschema~=1.2.2'
    ],
    install_requires=[
        'xmlschema~=1.2.2'
    ],
    python_requires=">=3.8",
    keywords="Open-Simulation-Platform Parser XML JSON",
)
