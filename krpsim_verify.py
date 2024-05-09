from parse_krpsim_file import parse_krpsim_file
import sys
import matplotlib.pyplot as plt


def parse_log_file(file_path):
    with open(file_path, "r") as file:
        lines = file.readlines()

    processes = []
    stocks = []
    current_process = {}
    tasks = []
    start_times = []
    end_times = []
    durations = []

    for line in lines:
        if line.startswith("process:"):
            if current_process:
                processes.append(current_process)
            current_process = {"name": line.strip().split(": ")[1]}
        elif line.startswith("Executed:"):
            parts = line.strip().split(", ")
            start_time = int(parts[1].split(": ")[1])
            end_time = int(parts[2].split(": ")[1])
            tasks.append(current_process.get("name"))
            start_times.append(start_time)
            end_times.append(end_time)
            durations.append(end_time - start_time)
        elif line.startswith("Consumed:"):
            if current_process:
                consumed = line.strip().split(": ")[1]
                consumed_quantity = line.strip().split(": ")[2]
                current_process["consumed"] = {
                    "resource": consumed,
                    "quantity": consumed_quantity,
                }
        elif line.startswith("Produced:"):
            if current_process:
                produced = line.strip().split(": ")[1]
                produced_quantity = line.strip().split(": ")[2]
                current_process["produced"] = {
                    "resource": produced,
                    "quantity": produced_quantity,
                }
        elif line.startswith("Stock:"):
            stock_parts = line.strip().split("{")[1].split("}")[0].split(", ")
            stock_dict = {}
            for part in stock_parts:
                key, value = part.split(": ")
                stock_dict[key.strip("'")] = int(value)
            stocks.append(stock_dict)

    if current_process:
        processes.append(current_process)

    return stocks, processes, tasks, start_times, end_times, durations


def check_each_process(processes_log, processes):
    for process_log in processes_log:
        name = process_log["name"]
        if processes:
            exist = False
            for process in processes:
                if process.name == name:
                    exist = True
                    consumed_item = process_log["consumed"].get("resource")
                    if consumed_item in process.needs:
                        if process.needs[consumed_item] != int(
                            process_log["consumed"].get("quantity")
                        ):
                            print(f"Process {name} consumed quantity is not correct")
                            exit(1)
                    else:
                        print(
                            f"Process {name} consumed item does not exist in the needs"
                        )
                        exit(1)
                    produced_item = process_log["produced"].get("resource")
                    if produced_item in process.results:
                        if process.results[produced_item] != int(
                            process_log["produced"].get("quantity")
                        ):
                            print(f"Process {name} produced quantity is not correct")
                            exit(1)
                    else:
                        print(
                            f"Process {name} produced item does not exist in the results"
                        )
                        exit(1)
            if not exist:
                print(f"Process {name} does not exist in the processes list")
                exit(1)


def check_each_stock(stocks_log, processes_log, processes):
    current_stock = stocks_log[0]
    for i in range(1, len(stocks_log)):
        process_name = processes_log[i - 1].get("name")
        for process in processes:

            # 同一プロセスを実行
            if process.name == process_name:
                for item in process.needs:
                    if item in current_stock:
                        current_stock[item] -= int(process.needs[item])
                for item in process.results:
                    if item in current_stock:
                        current_stock[item] += int(process.results[item])
                    else:
                        current_stock[item] = int(process.results[item])

        # ログとの比較
        if current_stock != stocks_log[i]:
            print(f"Stocks are not correct at process {i}")
            print(f"Estimated Stock: {current_stock}")
            print(f"Stock Log      : {stocks_log[i]}")
            exit(1)


def plot_processes(tasks, start_times, durations):
    # Create a figure and an axes.
    fig, ax = plt.subplots()

    colors = [
        "tab:blue",
        "tab:orange",
        "tab:green",
        "tab:red",
        "tab:purple",
        "tab:brown",
        "tab:pink",
        "tab:gray",
        "tab:olive",
        "tab:cyan",
    ]

    # Plot each task as a bar.
    for i, task in enumerate(tasks):
        color = colors[i % len(colors)]
        ax.broken_barh(
            [(start_times[i], durations[i])], (i - 0.4, 0.8), facecolors=color
        )

    # Set labels and title
    ax.set_xlabel("Time")
    ax.set_ylabel("Processes")
    ax.set_title("Process Execution Timeline")
    ax.set_yticks(range(len(tasks)))
    ax.set_yticklabels(tasks)

    # Show grid
    ax.grid(True)

    # Show the plot
    plt.show()


if __name__ == "__main__":

    if len(sys.argv) > 2:
        file_name = sys.argv[1]
        log_file = sys.argv[2]
    else:
        print("python3 krpsim_verify.py <file_name> <log_file>")
        sys.exit(1)

    # インプット用ファイルをパースする
    stock, processes, optimize = parse_krpsim_file(file_name)
    # ログファイルをパースする
    stocks_log, processes_log, tasks, start_times, end_times, durations = (
        parse_log_file(log_file)
    )
    # プロセス内容をチェックする
    check_each_process(processes_log, processes)
    # ストック内容をチェックする
    check_each_stock(stocks_log, processes_log, processes)
    # プロセスの実行時間をプロットする
    plot_processes(tasks, start_times, durations)
