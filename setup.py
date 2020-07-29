import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

# get version
env = {}
with open("otter/version.py") as f:
	exec(f.read(), env)
version = env["__version__"]

setuptools.setup(
	name = "otter-grader",
	version = version,
	author = "Chris Pyles",
	author_email = "cpyles@berkeley.edu",
	description = "Python and Jupyter Notebook autograder",
	long_description = long_description,
	long_description_content_type = "text/markdown",
	url = "https://github.com/ucbds-infra/otter-grader",
	license = "BSD-3-Clause",
	packages = setuptools.find_packages(exclude=["test"]),
	classifiers = [
		"Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
	],
	install_requires=[
		"ipython==7.16.1",
		"dill==0.3.2",
		"docker==4.2.2",
		"jinja2==2.11.2",
		"nbconvert==5.6.1",
		"nbformat==5.0.7",
		"nb2pdf==0.6.0",
		"pandas==1.1.0",
		"pyyaml==5.3.1",
		"setuptools==49.2.0",
		"tqdm==4.48.0",
		"tornado==6.0.4",
	],
	scripts=["bin/otter"],
	package_data={
		"otter.service": ["templates/*.html"], 
		"otter.export": ["*.tplx"],
		"otter.generate": ["templates/*"],
	},
)
