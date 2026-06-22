from setuptools import setup, find_packages

setup(
    name='farsiscript-lang',
    version='0.2.5',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    entry_points={
        'console_scripts': [
            'farsiscript=farsiscript.main:main',
        ],
    },
)
