import pytest
from pathlib import Path
from fmi_wrapper import run_fmpy_with_aerodyn_full_process


@pytest.fixture
def fmu_file(tmp_path):
    """Fixture to provide a mock FMU file."""
    fmu = tmp_path / "test.fmu"
    fmu.touch()  # Create an empty mock FMU
    return fmu


@pytest.fixture
def simulation_directory(tmp_path):
    """Fixture for creating a temporary simulation directory."""
    path_to_case = tmp_path / "test_case"
    path_to_case.mkdir()
    return path_to_case


def test_fmpy_with_aerodyn(fmu_file, simulation_directory):
    """Test FMU simulation with AeroDyn integration."""
    model_params = {"name": "DTU_10MW", "hub_radius": 2.8, "tower_height": 119.0}
    simulation_time = 10.0  # seconds

    # Run the simulation
    results = run_fmpy_with_aerodyn(
        fmu_path=str(fmu_file),
        path_to_case=simulation_directory,
        model_params=model_params,
        simulation_time=simulation_time,
    )

    # Validate results
    assert results, "FMU simulation returned empty results"
    assert 'HWindSpeed' in results, "HWindSpeed missing in results"
    assert 'BladePitch' in results, "BladePitch missing in results"
