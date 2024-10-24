import logging


class StructuralOutput:
    def __init__(self, log_file="structural.log"):
        self.logger = logging.getLogger("StructuralLogger")
        self.logger.setLevel(logging.DEBUG)

        # File handler for logging
        file_handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def log_results(self, message):
        self.logger.info(message)

    def log_error(self, message):
        self.logger.error(message)
