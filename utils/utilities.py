import logging


def set_logging(file_level: int = logging.DEBUG, console_level: int = logging.INFO, filename: str = "discord.log") -> tuple[logging.Logger, logging.StreamHandler]:
	"""Sets up logging for the bot."""
	
	logger = logging.getLogger("discord") # discord.py logger
	logger.setLevel(logging.DEBUG)
	log_formatter = logging.Formatter(fmt="[{asctime}] [{levelname:<8}] {name}: {message}", datefmt="%Y-%m-%d %H:%M:%S", style="{")

	# File-logs
	file_handler = logging.FileHandler(filename=filename, encoding="utf-8", mode='w')
	file_handler.setFormatter(log_formatter)
	file_handler.setLevel(file_level)
	logger.addHandler(file_handler)

	# Console-logs
	console_handler = logging.StreamHandler()
	console_handler.setFormatter(log_formatter)
	console_handler.setLevel(console_level)
	logger.addHandler(console_handler)

	return logger, console_handler