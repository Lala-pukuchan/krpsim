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

        try:
            if ":" in line:
                parts = line.split(":")
                if len(parts) == 2 and parts[1].isdigit():
                    stock.add_resource(parts[0], int(parts[1]))
                    stock.add_raw_material(parts[0])
                else:
                    match = re.match(r"(\w+):\(([^)]+)\):\(([^)]+)\):(\d+)", line)
                    if match:
                        name = match.group(1)
                        needs_part = match.group(2)
                        results_part = match.group(3)
                        delay = int(match.group(4))
                        needs = dict(item.split(":") for item in needs_part.split(";"))
                        results = dict(item.split(":") for item in results_part.split(";"))
                        for key, value in needs.items():
                            needs[key] = int(value)
                        for key, value in results.items():
                            results[key] = int(value)
                        processes.append(Process(name, needs, results, int(delay)))
                    elif line.startswith("optimize"):
                        _, goals = line.split(":")
                        goals = goals.strip("()")
                        optimize = Optimize(goals.split(";"))
            else:
                raise ValueError(f"Invalid line format: {line}")  # 追加
        except Exception as e:
            print(f"Error parsing line '{line}': {e}")
    return stock, processes, optimize