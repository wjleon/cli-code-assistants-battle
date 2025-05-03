from setuptools import setup, find_packages

setup(
    name="deepl_integration",
    version="0.1.0",
    description="A Python integration with the DeepL API",
    author="DeepL Integration Team",
    author_email="example@example.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "pydantic>=1.8.0",
        "python-dotenv>=0.15.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
