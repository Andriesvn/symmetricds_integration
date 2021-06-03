from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in symmetricds_integration/__init__.py
from symmetricds_integration import __version__ as version

setup(
	name='symmetricds_integration',
	version=version,
	description='Integrate SymmetricDS into Frappe',
	author='AvN Technologies',
	author_email='info@avntech.net',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
