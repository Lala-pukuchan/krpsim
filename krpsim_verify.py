from parse_krpsim_file import parse_krpsim_file
import sys
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from termcolor import colored

def parse_log_file(file_path):
    with open(file_path, "r") as file:
        lines = file.readlines()

    initial_stock = {}
    final_stock = {}
    processes = []
    processes_time = []

    for line in lines:
        line = line.strip()
        if not line or line == "==================":
            continue
        if "Initial Stock:" in line:
            stock_parts = line.split("{")[1].split("}")[0].split(", ")
            for part in stock_parts:
                key, value = part.split(": ")
                initial_stock[key.strip().strip("'").strip('"')] = int(value)
        elif "Final Stock:" in line:
            stock_parts = line.split("{")[1].split("}")[0].split(", ")
            for part in stock_parts:
                key, value = part.split(": ")
                final_stock[key.strip().strip("'").strip('"')] = int(value)
        elif "Consumed by" in line:
            process_name = line.split(")")[0].split("by ")[1]
            resource, quantity = line.split(")")[1].split(": ")
            processes.append(
                {
                    "name": process_name,
                    "consumed": {resource.strip().strip("'").strip('"'): int(quantity)},
                }
            )
        elif "Produced by" in line:
            process_name = line.split(")")[0].split("by ")[1]
            resource, quantity = line.split(")")[1].split(": ")
            processes.append(
                {
                    "name": process_name,
                    "produced": {resource.strip().strip("'").strip('"'): int(quantity)},
                }
            )
        elif line.startswith("Start:"):
            parts = line.split(", ")
            if len(parts) == 3:
                process_name = parts[0].split(": ")[1]
                start_time = int(parts[1].split(": ")[1])
                end_time = int(parts[2].split(": ")[1])
                processes_time.append(
                    {"name": process_name, "start_time": start_time, "end_time": end_time}
                )
            else:
                print(colored(f"Unexpected format in line: {line}", "red"))

    return initial_stock, final_stock, processes, processes_time

def verify_process_calculations(initial_stock, final_stock, processes):
    # Create a copy of the initial stock to modify it
    simulated_stock = initial_stock.copy()
    print("Simulated Stock:", simulated_stock)

    # Process each step
    for process in processes:
        if "consumed" in process:
            for resource, quantity in process["consumed"].items():
                if resource in simulated_stock:
                    if simulated_stock[resource] < quantity:
                        print(colored(f"Error: Not enough '{resource}' in stock to consume for process '{process['name']}'.", "red"))
                        print(colored(f"Stock available: {simulated_stock[resource]}, required: {quantity}", "cyan"))
                        return False
                    simulated_stock[resource] -= quantity
                else:
                    print(colored(f"Error: Trying to consume a resource '{resource}' that doesn't exist.", "red"))
                    return False

        if "produced" in process:
            for resource, quantity in process["produced"].items():
                if resource in simulated_stock:
                    simulated_stock[resource] += quantity
                else:
                    simulated_stock[resource] = quantity

    # Check if the simulated final stock matches the actual final stock
    for resource, quantity in final_stock.items():
        if simulated_stock.get(resource, 0) != quantity:
            print(colored(f"Mismatch in resource '{resource}': expected {quantity}, got {simulated_stock.get(resource, 0)}", "red"))
            return False

    # Optionally, check for any extra resources in the simulated stock not in final stock
    for resource in simulated_stock:
        if resource not in final_stock:
            print(colored(f"Extra resource '{resource}' in simulated stock not accounted for in final stock.", "red"))
            return False

    print("All processes verified successfully.")
    return True

if __name__ == "__main__":

    if len(sys.argv) > 2:
        file_name = sys.argv[1]
        log_file = sys.argv[2]
    else:
        print("python3 krpsim_verify.py <file_name> <log_file>")
        sys.exit(1)

    if file_name != log_file.replace(".log", ""):
        print("It's not a log file. Please input a log file.")
        sys.exit(1)

    # インプット用ファイルをパースする
    stock, processes, optimize = parse_krpsim_file(file_name)

    try:
        # ログファイルをパースする
        initial_stock, final_stock, processes, processes_time = parse_log_file(log_file)
        print("Initial Stock:", initial_stock)
        print("Final Stock:", final_stock)
        print("Processes:")
        for process in processes:
            print(process)

        # プロセスの計算を検証する
        if verify_process_calculations(initial_stock, final_stock, processes):
            print("Verification successful.")
            # グラフを描画する
            fig, ax = plt.subplots(figsize=(10, 8))
            ax.set_title("Processes Time")
            ax.set_xlabel("Time")
            ax.set_ylabel("Processes")

            # Generate a color map from a set of colors
            colors = list(mcolors.TABLEAU_COLORS)
            color_map = {}
            process_count = {}
            unique_process_index = 0

            for process in processes_time:
                base_name = process["name"]
                if base_name not in color_map:
                    # Assign a color to each unique process name
                    color_map[base_name] = colors[unique_process_index % len(colors)]
                    unique_process_index += 1

                # Count occurrences to make each bar unique
                if base_name in process_count:
                    process_count[base_name] += 1
                else:
                    process_count[base_name] = 1

                unique_name = f"{base_name} ({process_count[base_name]})"
                # Use the mapped color for the process
                ax.barh(unique_name, process["end_time"] - process["start_time"], left=process["start_time"], color=color_map[base_name])

            plt.tight_layout()
            plt.show()

        else:
            print(colored("Verification failed.", "red"))

    except Exception as e:
        print(colored(f"Error occurred: {e}", "red"))
        sys.exit(1)
