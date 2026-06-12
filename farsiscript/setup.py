from setuptools import setup

setup(
    name='farsiscript',
    version='1.0.0',
    description='A Persian programming language with interpreter and C compiler',
    author='Your Name',
    py_modules=['tokenizer', 'parser', 'evaluator', 'compiler', 'main'],
    entry_points={
        'console_scripts': [
            'farsiscript=main:main',
        ],
    },
    install_requires=[],
)
