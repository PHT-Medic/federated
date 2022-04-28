from setuptools import setup, find_packages

setup(
    author="Michael Graf",
    author_email="michael.graf@uni-tuebingen.de",
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    install_requires=[
        "pydantic",
        "cryptography",
        "numpy",
        "pycryptodome",
        "sqlmodel",
        ""
    ],
    version="0.0.1",
    license="MIT license",
    packages=find_packages(),
    name="pht_federated",
)
