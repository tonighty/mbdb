import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name = 'mbdb',
	version = '0.6',
	packages = setuptools.find_packages(),
	url = 'https://github.com/tonighty/mbdb',
	author = 'mjr&bkva',
	author_email = 'mjr@feip.co',
	description = 'Simple Database Management System',
	long_description = long_description,
	long_description_content_type = "text/markdown",
	install_requires = ['ply']
)
