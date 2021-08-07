import setuptools

setuptools.setup(
    name="rhk_interface",
    version='0.1',
    description='RHK R9 interface to make measurements and plot data',
    author='Kotaro Taga',
    author_email='taga@issp.u-tokyo.ac.jp',
    url='https://github.com/hoopdev/RHK-interface',
    license="MIT",
    packages=setuptools.find_packages(),
    classifiers=[
    "Development Status :: 1 - Planning"
    ],
    install_requires=[
        "numpy",
        "xarray",
        "plotly",
    ],
    python_requires='>=3',
)