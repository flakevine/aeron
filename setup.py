import setuptools

with open("README.md", "r", encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name='sklORM',
    version='0.1',
    scripts=['skl.py'],
    author='Viktor Marinho',
    author_email='viktormpcs@gmail.com',
    description='A independent and simple sqlite3 ORM python module',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/flakevine/skl',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)