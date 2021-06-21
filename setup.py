import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="OpenTurbineCoDe",
    version="0.0.1",
    author="",
    author_email="",
    description="Open Turbine Control co-Design package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/OpenTurbineCoDe/OpenTurbineCoDe",
    project_urls={
        "Bug Tracker": "https://github.com/OpenTurbineCoDe/OpenTurbineCoDe/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires = ["numpy"],  #'json'
    extras_require={
        "high-fidelity": [
            "adflow",
            "multipoint"
        ],
        # "low-fidelity": [],
        # 'openmdao>=3.4',
    },
    packages=[
        "openturbinecode",
        "openturbinecode.aerodynamics",
        "openturbinecode.aerostructural",
        "openturbinecode.controls",
        "openturbinecode.glue_code",
        "openturbinecode.master_GUI",
        "openturbinecode.prepro",
        "openturbinecode.structure",
        "openturbinecode.utils",
    ],
    python_requires=">=3.6",
)