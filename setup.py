from setuptools import setup, find_packages

setup(
    name='libsanctions',
    version='0.0.1',
    description="",
    long_description="",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    keywords='pep poi persons popolo database',
    author='Friedrich Lindenberg',
    author_email='friedrich@pudo.org',
    url='http://opensanctions.org',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=[],
    include_package_data=True,
    zip_safe=False,
    test_suite='nose.collector',
    install_requires=[
        'unicodecsv==0.14.1',
        'normality>=0.4.2',
        'fingerprints>=0.4.0',
        'countrynames',
        'jsonschema>=2.6.0',
        'sqlalchemy>=1.1.0',
        'requests>=2.13',
        'boto3',
        'dalet',
        'lxml',
        'xlrd',
        'six'
    ],
    entry_points={},
    tests_require=[]
)
