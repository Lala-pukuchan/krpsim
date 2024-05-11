from parse_krpsim_file import parse_krpsim_file
import sys
import matplotlib.pyplot as plt


def parse_log_file(file_path):
    with open(file_path, "r") as file:
        lines = file.readlines()

    initial_stock = {}
    final_stock = {}
    processes = []
    processes_time = []

    for line in lines:
        line = line.strip()
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
                print(f"Unexpected format in line: {line}")


    return initial_stock, final_stock, processes, processes_time


def verify_process_calculations(initial_stock, processes):
    # Create a copy of the initial stock to modify it
    simulated_stock = initial_stock.copy()
    print("Simulated Stock:", simulated_stock)

    # Process each step
    for process in processes:
        if "consumed" in process:
            for resource, quantity in process["consumed"].items():
                if resource in simulated_stock:
                    simulated_stock[resource] -= quantity
                else:
                    print(
                        f"Error: Trying to consume a resource '{resource}' that doesn't exist."
                    )
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
            print(
                f"Mismatch in resource '{resource}': expected {quantity}, got {simulated_stock.get(resource, 0)}"
            )
            return False

    # Optionally, check for any extra resources in the simulated stock not in final stock
    for resource in simulated_stock:
        if resource not in final_stock:
            print(
                f"Extra resource '{resource}' in simulated stock not accounted for in final stock."
            )
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
        if verify_process_calculations(initial_stock, processes):
            print("Verification successful.")
        else:
            print("Verification failed.")

        # グラフを描画する
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.set_title("Processes Time")
        ax.set_xlabel("Time")
        ax.set_ylabel("Processes")
        for process in processes_time:
            ax.barh(process["name"], process["end_time"] - process["start_time"], left=process["start_time"])
        plt.tight_layout()
        plt.show()

    except Exception as e:
        print(e)
        sys.exit(1)
