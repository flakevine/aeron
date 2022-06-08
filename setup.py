import setuptools

with open("README.md", "r", encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name='sklORM',
    version='0.1.1',
    scripts=[],
    author='Viktor Marinho',
    author_email='viktormpcs@gmail.com',
    description='A independent and simple sqlite3 ORM python module',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/flakevine/skl',
    packages=['skl'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)