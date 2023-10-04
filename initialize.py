import datetime
import os


log_dir = "logs"


# Function to get the current timestamp
def get_current_timestamp():
    return datetime.datetime.now().strftime("%d-%m-%Y %H-%M-%S")


# Function to write a message to the log file and print it
def log_message(message, log_file):
    with open(log_file, "a") as file:
        file.write(
            f"{get_current_timestamp()} :: {message}\n"
        )  # TO REMOVE ALL TIMESTAMPS IN CODE
        # file.write(f"{message}\n")
    print(f"{get_current_timestamp()} :: {message}")


# Function to create log directory if it doesn't exist
def create_log_dir(log_dir):
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)


# Function to clean up old log files
def cleanup_old_logs(log_dir, max_files=10):
    log_files = sorted(os.listdir(log_dir), reverse=True)
    while len(log_files) > max_files:
        os.remove(os.path.join(log_dir, log_files.pop()))


# Function to get the current log file
def get_current_log_file(log_dir):
    now = get_current_timestamp()
    return os.path.join(log_dir, f"{now}.log")


# Function to initialize log file
def initialize_log_file():
    log_dir = "logs"
    create_log_dir(log_dir)
    log_file = get_current_log_file(log_dir)
    # Create the log file if it doesn't exist
    if not os.path.exists(log_file):
        with open(log_file, "w") as file:
            file.write("Log file created.\n")
    return log_file, log_dir
