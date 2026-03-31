from setuptools import setup, find_packages

setup(
    name="devmap",
    version="1.0.0",
    description="Visual Codebase Explorer — turns any project into an interactive dependency graph",
    author="Git_Gurus",
    python_requires=">=3.8",
    packages=find_packages(),
    package_data={
        "devmap": ["frontend/template.html"],
    },
    install_requires=[
        "networkx",
    ],
    entry_points={
        "console_scripts": [
            "devmap=devmap.main:main",
        ]
    },
)