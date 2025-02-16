from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="odg",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Offer Document Generator CLI Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/username/odg",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Text Processing :: Markup",
    ],
    install_requires=[
        "PyYAML>=5.4.1,<6.0.0",
        "pydantic>=1.8.2,<2.0.0",
        "pytest>=7.3.0,<8.0.0"
    ],
    entry_points={
        'console_scripts': [
            'odg=main:main',
        ],
    },
    python_requires=">=3.8",
)
