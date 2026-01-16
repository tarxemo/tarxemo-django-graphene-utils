from setuptools import setup, find_packages

setup(
    name="tarxemo-django-graphene-utils",
    version="0.1.2",
    author="TarXemo",
    description="Shared Django Graphene utilities and DTOs for efficient API development",
    long_description=open("README.md").read() if open("README.md").read() else "",
    long_description_content_type="text/markdown",
    url="https://github.com/tarxemo/tarxemo-django-graphene-utils",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Django",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "Django",
        "graphene-django",
        "graphene",
        "graphql-core",
    ],
)
