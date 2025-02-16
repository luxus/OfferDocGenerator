from setuptools import setup, find_packages

setup(
    name="odg",
    version="1.0.0",
    description="Offer Document Generator CLI Tool",
    packages=find_packages(),
    install_requires=[
        "PyYAML",
        "pydantic",
        "pytest"
    ],
    entry_points={
        'console_scripts': [
            'odg=main:main',
        ],
    },
)
