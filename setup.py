from setuptools import find_packages, setup


setup(
    name='elastic-ops-manager',
    packages=find_packages(include=['elastic_ops_manager']),
    version='0.0.1',
    license='MIT',
    long_description=open('README.md', 'r').read(),
    url='https://github.com/omnivector-solutions/elastic-ops-manager',
    install_requires=['jinja2'],
    python_requires='>=3.6',
    package_data={'elastic_ops_manager': ['templates/*']},
)
