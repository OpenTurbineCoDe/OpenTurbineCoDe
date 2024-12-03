import subprocess
import os


class ExternalModel:
    def __init__(self):
        self.state = 0.0
        self.parameter = 1.0
        self.external_program_path = "path_to_external_program"
        self.result_file = "result.txt"
        self.input_file = "input.txt"

    def initialize(self, initial_state, parameter):
        self.state = initial_state
        self.parameter = parameter
        print(f"Initialized with state={self.state}, parameter={self.parameter}")

    def call_external_program(self, input_value):
        # Write input to file
        with open(self.input_file, 'w') as f:
            f.write(f"{input_value}\n")

        # Call the external program
        subprocess.run([self.external_program_path, self.input_file, self.result_file], check=True)

        # Read result from file
        with open(self.result_file, 'r') as f:
            result = float(f.read().strip())

        return result

    def do_step(self, input, dt):
        # Call external program
        external_result = self.call_external_program(input)

        # Update state using the external result
        self.state += external_result * dt
        output = self.state * 2
        print(f"Stepping with input={input}, dt={dt}, state={self.state}, output={output}")
        return output

    def terminate(self):
        print("Terminating simulation")
        # Clean up files if necessary
        if os.path.exists(self.input_file):
            os.remove(self.input_file)
        if os.path.exists(self.result_file):
            os.remove(self.result_file)
