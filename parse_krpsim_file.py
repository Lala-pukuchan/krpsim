from Stock import Stock
from Process import Process
from Optimize import Optimize
import re


def parse_krpsim_file(file_path):
    stock = Stock()
    processes = []
    optimize = None

    with open(file_path, "r") as file:
        lines = file.readlines()

    for line in lines:
        line = line.strip()
        if line.startswith("#") or not line:
            continue

        if ":" in line:
            parts = line.split(":")
            if len(parts) == 2 and parts[1].isdigit():
                # This is a stock entry
                stock.add_resource(parts[0], int(parts[1]))
            else:
                # Use regular expression to extract parts
                match = re.match(r"(\w+):\(([^)]+)\):\(([^)]+)\):(\d+)", line)
                if match:
                    name = match.group(1)
                    needs_part = match.group(2)
                    results_part = match.group(3)
                    delay = match.group(4)

                    # Convert needs and results from string to dictionary
                    needs = dict(item.split(":") for item in needs_part.split(";"))
                    results = dict(item.split(":") for item in results_part.split(";"))

                    # Append the process
                    processes.append(Process(name, needs, results, int(delay)))
                elif line.startswith("optimize"):
                    # Optimize entry
                    _, goals = line.split(":")
                    optimize = Optimize(goals.split(";"))

    return stock, processes, optimize
