from setuptools import setup, find_packages

setup(
    name="odg",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "python-docx",
        "pydantic",
        "pydantic-settings",
        "jinja2",
        "pyyaml",
    ],
    entry_points={
        "console_scripts": [
            "odg=odg.main:main",
        ],
    },
)