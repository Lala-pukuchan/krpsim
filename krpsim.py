from parse_krpsim_file import parse_krpsim_file
import logging
import sys
from collections import deque


def assign_priorities(ongoing_processes, processes, final_product, stock):

    # プロセスの優先度をリセットする
    for process in processes:
        process.priority = 0

    # ゴールから逆算して、優先度を割り当てる
    def recursive_priority_assignment(current_process, current_priority, stock):
        # 優先度を割り当てる
        current_process.priority = current_priority
        print(stock)
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
                recursive_priority_assignment(precursor, current_priority - 1, stock)

    # 実行中のプロセスを考慮して、在庫を推定する
    copied_stock = stock.copy()
    estimated_stock = stock.copy()
    for ongoing_process in ongoing_processes:
        estimated_stock = produce_resources(copied_stock, ongoing_process)

    # 最終成果物を生成するプロセスを見つける
    for process in processes:
        if final_product in process.results:
            recursive_priority_assignment(process, 10, estimated_stock)


def can_schedule(process, current_resources):
    return all(
        current_resources.get(resource, 0) >= quantity
        for resource, quantity in process.needs.items()
    )


def consume_resources(current_resources, process):
    logging.info("-------------------")
    for resource, quantity in process.needs.items():
        try:
            current_resources[resource] -= quantity
            logging.info(f"Consumed: {resource}: {quantity}")
        except KeyError:
            pass


def print_produced_resources(process):
    for resource, quantity in process.results.items():
        logging.info("-------------------")
        logging.info(f"Produced: {resource}: {quantity}")


def produce_resources(current_resources, process):
    for resource, quantity in process.results.items():
        try:
            current_resources[resource] += quantity
        except KeyError:
            current_resources[resource] = quantity
    return current_resources


def parallel_schedule(stock, processes):
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

        assign_priorities(
            ongoing_processes,
            processes,
            optimize.final_product,
            stock.resources,
        )

        if len(executable_processes) > 0:
            process = executable_processes.popleft()

            if can_schedule(process, stock.resources) and process.priority > 0:

                consume_resources(stock.resources, process)
                assign_priorities(
                    ongoing_processes,
                    processes,
                    optimize.final_product,
                    stock.resources,
                )

                process.start_time = time_elapsed
                process.end_time = time_elapsed + process.delay

                logging.info(
                    f"Executed: {process.name}, "
                    f"Start Time: {process.start_time}, "
                    f"End Time: {process.end_time}"
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
                logging.info("==================")
                if time_elapsed <= estimated_max_end_time:
                    continue
            executable_processes = deque(
                process
                for process in processes
                if can_schedule(process, stock.resources) and process.priority > 0
            )
            if len(executable_processes) == 0:
                break


if __name__ == "__main__":

    if len(sys.argv) > 1:
        file_name = sys.argv[1]
    else:
        print("No file name provided as argument.")
        sys.exit(1)

    stock, processes, optimize = parse_krpsim_file(file_name)

    # 最終成果物が指定されている場合、優先度を割り当て、優先度の高い順にプロセスをソートする
    if optimize.final_product:
        ongoing_processes = []
        assign_priorities(
            ongoing_processes, processes, optimize.final_product, stock.resources
        )
        processes.sort(key=lambda x: x.priority, reverse=True)

    # ログ機能を追加する
    logging.basicConfig(
        filename=file_name + ".log", level=logging.INFO, format="%(message)s"
    )

    logging.info("Stock: %s", stock.resources)
    logging.info("-------------------")
    parallel_schedule(stock, processes)
