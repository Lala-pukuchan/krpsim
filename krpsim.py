from parse_krpsim_file import parse_krpsim_file
import logging
import sys
from collections import deque

def assign_priorities(
    ongoing_processes, processes, final_product, stock, raw_materials
):
    # プロセスの優先度をリセットする
    for process in processes:
        process.priority = 0

    # ゴールから逆算して、優先度を割り当てる
    def recursive_priority_assignment(i, current_process, current_priority, stock):
        # 無限ループ回避
        i += 1
        if i > 5:
            return

        # 原材料を含むプロセスにボーナスを付与する
        bonus = False
        if current_priority == 10:
            for raw in raw_materials:
                if raw not in current_process.needs:
                    bonus = False
                    break
                bonus = True

        # 優先度を割り当てる
        if bonus:
            current_process.priority = current_priority + 1
        else:
            current_process.priority = current_priority

        # 在庫に必要材料が既にある場合は、優先度を下げる
        updated_needs = {
            resource: quantity - stock.get(resource, 0)
            for resource, quantity in current_process.needs.items()
            if (quantity - stock.get(resource, 0)) > 0
        }

        # 各プロセスでループする
        for precursor in processes:
            if precursor == current_process:
                continue
            # 必要なものを生成できるプロセスに対して、高い優先度を割り当てる
            if any(item in precursor.results for item in updated_needs):
                recursive_priority_assignment(i, precursor, current_priority - 1, stock)

    # 実行中のプロセスを考慮して、在庫を推定する
    copied_stock = stock.copy()
    estimated_stock = stock.copy()
    for ongoing_process in ongoing_processes:
        estimated_stock = produce_resources(copied_stock, ongoing_process)

    # 最終成果物を生成するプロセスを見つける
    for process in processes:
        if final_product in process.results:
            recursive_priority_assignment(0, process, 10, estimated_stock)

    processes.sort(key=lambda x: (x.priority, sum(x.results.values())), reverse=True)

def can_schedule(process, current_resources):
    return all(
        current_resources.get(resource, 0) >= quantity
        for resource, quantity in process.needs.items()
    )

def consume_resources(current_resources, process):
    for resource, quantity in process.needs.items():
        try:
            current_resources[resource] -= quantity
            logging.info(f"   (Consumed by {process.name}) {resource}: {quantity}")
        except KeyError:
            pass

def print_produced_resources(process):
    for resource, quantity in process.results.items():
        logging.info(f"   (Produced by {process.name}) {resource}: {quantity}")

def produce_resources(current_resources, process):
    for resource, quantity in process.results.items():
        try:
            current_resources[resource] += quantity
        except KeyError:
            current_resources[resource] = quantity
    return current_resources

def parallel_schedule(stock, processes, max_time):
    executable_processes = deque(
        process
        for process in processes
        if can_schedule(process, stock.resources) and process.priority > 0
    )
    ongoing_processes = []
    time_elapsed = 0

    logging.info("==================")
    logging.info(f"Time Elapsed: {time_elapsed}")
    logging.info("==================")

    while True:
        if len(ongoing_processes) > 0:
            for ongoing_process in ongoing_processes:
                if ongoing_process.end_time == time_elapsed:
                    produce_resources(stock.resources, ongoing_process)
                    print_produced_resources(ongoing_process)
                    ongoing_processes.remove(ongoing_process)
                    logging.info(
                        f"End: {ongoing_process.name}, "
                        f"End Time: {ongoing_process.end_time}"
                    )

        if time_elapsed >= max_time:
            logging.info(f"Maximum time {max_time} reached, stopping execution.")
            print("Maximum time reached, stopping execution.")
            break

        assign_priorities(
            ongoing_processes,
            processes,
            optimize.final_product,
            stock.resources,
            stock.raw_materials,
        )
        executable_processes = list(executable_processes)
        executable_processes.sort(
            key=lambda x: (x.priority, sum(x.results.values())), reverse=True
        )
        executable_processes = deque(executable_processes)

        if len(executable_processes) > 0:
            process = executable_processes.popleft()

            if can_schedule(process, stock.resources) and process.priority > 0:
                logging.info(f"Process start: {process.name}, Start Time: {time_elapsed}")
                consume_resources(stock.resources, process)
                assign_priorities(
                    ongoing_processes,
                    processes,
                    optimize.final_product,
                    stock.resources,
                    stock.raw_materials,
                )

                process.start_time = time_elapsed
                process.end_time = time_elapsed + process.delay

                logging.info(
                    f"Start: {process.name}, "
                    f"Start Time: {process.start_time}, "
                    f"Estimated End Time: {process.end_time}"
                )

                ongoing_processes.append(process)
                if can_schedule(process, stock.resources) and process.priority > 0:
                    executable_processes.append(process)
        else:
            if len(ongoing_processes) > 0:
                time_elapsed = min(
                    process.end_time
                    for process in ongoing_processes
                    if process.end_time
                )
                estimated_max_end_time = max(
                    process.end_time
                    for process in ongoing_processes
                    if process.end_time
                )
                logging.info("==================")
                logging.info(f"Time Elapsed: {time_elapsed}")
                logging.info(f"Current Stock: {stock.resources}")
                logging.info("==================")
                if time_elapsed <= estimated_max_end_time:
                    continue
            executable_processes = deque(
                process
                for process in processes
                if can_schedule(process, stock.resources) and process.priority > 0
            )
            if len(executable_processes) == 0:
                logging.info(f"End Time: {time_elapsed}")
                logging.info(f"Final Stock: {stock.resources}")
                print(f"End Time: {time_elapsed}")
                break

if __name__ == "__main__":
    if len(sys.argv) > 2:
        file_name = sys.argv[1]
        try:
            max_time = int(sys.argv[2])
        except ValueError:
            print("The delay parameter must be a number representing the maximum time.")
            sys.exit(1)
        if max_time < 0:
            print("The delay parameter must be a non-negative number.")
            sys.exit(1)
    else:
        print("Usage: krpsim <file> <delay>")
        sys.exit(1)

    try:
        stock, processes, optimize = parse_krpsim_file(file_name)
    except Exception as e:
        print(f"Error parsing file '{file_name}': {e}")
        sys.exit(1)

    # 最終成果物が指定されている場合、優先度を割り当て、優先度の高い順にプロセスをソートする
    if optimize.final_product:
        ongoing_processes = []
        assign_priorities(
            ongoing_processes,
            processes,
            optimize.final_product,
            stock.resources,
            stock.raw_materials,
        )

    # ログ機能を追加する
    logging.basicConfig(
        filename=file_name + ".log", level=logging.INFO, format="%(message)s", filemode="w"
    )

    logging.info("Initial Stock: %s", stock.resources)
    parallel_schedule(stock, processes, max_time)
    logging.info("Final Stock: %s", stock.resources)
    print("Final Stock: ", stock.resources)