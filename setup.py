import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="OpenTurbineCoDe",
    version="0.0.2",
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
    install_requires = ["numpy", "jsonschema"],  #'json'
    extras_require={
        "high-fidelity": [
            "adflow",
            "multipoint"
        ],
        "gui": ["PyQt5", "pyqtgraph"],
        "meshing": ["PGL"],
        "controls": ["scp", "pandas"]
        # "low-fidelity": [],
    },
    package_data = {"openturbinecode": ["*.json"],
    "openturbinecode.master_GUI": ["Config.ui"],
    "openturbinecode.controls": ["ConfigControl_v3.ui"]},
    packages=[
        "openturbinecode",
        "openturbinecode.aerodynamics",
        "openturbinecode.aerostructural",
        "openturbinecode.controls",
        "openturbinecode.master_GUI",
        "openturbinecode.prepro",
        "openturbinecode.structure",
        "openturbinecode.utils",
        "openturbinecode.DLC_manager",
        "openturbinecode.meshing",
        "openturbinecode.sample_module",
    ],
    python_requires=">=3.6",
)