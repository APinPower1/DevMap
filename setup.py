from setuptools import setup

setup(
    name="devmap",
    version="1.0.0",
    description="Visual Codebase Explorer — turns any project into an interactive dependency graph",
    author="Your Team Name",
    python_requires=">=3.8",
    py_modules=["main", "analyzer", "graph_builder"],
    install_requires=[
        "networkx",
    ],
    entry_points={
        "console_scripts": [
            "devmap=main:main",
        ]
    },
)