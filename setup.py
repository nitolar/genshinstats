from setuptools import setup

setup(
    name="genshinstats",
    version="1.4.12.7",
    author="nitolar",
    packages=["genshinstats"],
    description="A python library that can get the stats of Genshin Impact players using Hoyoverse's API.",
    keywords="api wrapper mihoyo genshin genshin-impact".split(),
    python_requires=">=3.7",
    url="https://github.com/niolar/genshinstats",
    project_urls={
#        "Documentation": "https://thesadru.github.io/pdoc/genshinstats/",
        "Issue tracker": "https://github.com/nitolar/genshinstats/issues",
    },
    install_requires=["requests", "browser-cookie3"],
    author_email="kontakt.nitolarplay@gmail.com",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
)
