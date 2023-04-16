from setuptools import setup, find_packages

setup(
    name='app',
    version='1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Flask',
        'Flask-WTF',
        'Flask-SQLAlchemy',
        'flask_session',
        'pandas'
        # add any additional dependencies here
    ],
)
