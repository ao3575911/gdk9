from setuptools import setup, find_packages

setup(
    name="gdk9",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["numpy"],
    entry_points={
        "console_scripts": ["gdk9=main:main"]
    },
    author="GDk9 Labs",
    description="Physics-aware symbolic implication kernel"
)
