from parse_krpsim_file import parse_krpsim_file
import sys


def parse_log_file(file_path):
    with open(file_path, "r") as file:
        lines = file.readlines()

    processes = []
    stocks = []
    current_process = {}

    for line in lines:
        if line.startswith("process:"):
            if current_process:
                processes.append(current_process)
            current_process = {"name": line.strip().split(": ")[1]}
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

    return stocks, processes


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


def check_each_stock(stocks_log, processes_log):
    current_stock = stocks_log[0]
    for i in range(1, len(stocks_log)):
        print(f"Stock: {i-1}, {stocks_log[i-1]}")
        print(f"current_stock: {current_stock}")
        print(f"Process: {processes_log[i - 1]}")
        print(i - 1)
        print("----------------------------")
        
        consumed_item = processes_log[i - 1].get("consumed").get("resource")
        produced_item = processes_log[i - 1].get("produced").get("resource")
        if consumed_item in current_stock:
            current_stock[consumed_item] -= int(
                processes_log[i - 1].get("consumed").get("quantity")
            )
        if produced_item in current_stock:
            current_stock[produced_item] += int(
                processes_log[i - 1].get("produced").get("quantity")
            )
        else:
            current_stock[produced_item] = int(
                processes_log[i - 1].get("produced").get("quantity")
            )

        if current_stock != stocks_log[i]:
            print(f"Stocks are not correct at process {i}")
            print(f"Estimated Stock: {current_stock}")
            print(f"Stock Log      : {stocks_log[i]}")
            exit(1)


if __name__ == "__main__":

    if len(sys.argv) > 2:
        file_name = sys.argv[1]
        log_file = sys.argv[2]
    else:
        print("python3 krpsim_verify.py <file_name> <log_file>")
        sys.exit(1)

    stock, processes, optimize = parse_krpsim_file("resources/simple")

    stocks_log, processes_log = parse_log_file(log_file)

    check_each_process(processes_log, processes)
    check_each_stock(stocks_log, processes_log)
