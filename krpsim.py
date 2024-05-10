from parse_krpsim_file import parse_krpsim_file
import logging
import sys
from collections import deque


def assign_priorities(processes, final_product, stock):

    for process in processes:
        process.priority = 0

    # ゴールから逆算して、優先度を割り当てる
    def recursive_priority_assignment(current_process, current_priority, stock):
        # 優先度を割り当てる
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
                recursive_priority_assignment(precursor, current_priority - 1, stock)

    # 最終成果物を生成するプロセスを見つける
    for process in processes:
        if final_product in process.results:
            recursive_priority_assignment(process, 10, stock)


def can_schedule(process, current_resources):
    return all(
        current_resources.get(resource, 0) >= quantity
        for resource, quantity in process.needs.items()
    )


def consume_resources(current_resources, process):
    for resource, quantity in process.needs.items():
        try:
            current_resources[resource] -= quantity
            logging.info(f"Consumed: {resource}: {quantity}")
        except KeyError:
            pass


def produce_resources(current_resources, process):
    for resource, quantity in process.results.items():
        try:
            current_resources[resource] += quantity
            logging.info(f"Produced: {resource}: {quantity}")
        except KeyError:
            current_resources[resource] = quantity
            logging.info(f"Produced: {resource}: {quantity}")


def update_resources(current_resources, process):
    logging.info(f"process: {process.name}")
    consume_resources(current_resources, process)
    produce_resources(current_resources, process)
    logging.info("Stock: %s", current_resources)


def parallel_schedule(stock, processes):
    executable_processes = deque(
        process
        for process in processes
        if can_schedule(process, stock.resources) and process.priority > 0
    )
    ongoing_processes = []
    time_elapsed = 0

    while True:
        if len(executable_processes) > 0:
            process = executable_processes.popleft()
            if can_schedule(process, stock.resources) and process.priority > 0:

                consume_resources(stock.resources, process)
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
                    produce_resources(stock.resources, process)
                    assign_priorities(
                        processes, optimize.final_product, stock.resources
                    )
                    continue
                else:
                    produce_resources(stock.resources, process)
                    assign_priorities(
                        processes, optimize.final_product, stock.resources
                    )
            else:
                print("How should I code here?")
        else:
            executable_processes = deque(
                process
                for process in processes
                if can_schedule(process, stock.resources) and process.priority > 0
            )
            time_elapsed = max(
                process.end_time for process in ongoing_processes if process.end_time
            )
            print("I feel it should be considered from min time to max time.")

            if len(executable_processes) == 0:
                break


# def parallel_schedule(stock, processes):
#    current_resources = stock.resources.copy()
#    executable_processes = [
#        process for process in processes if can_schedule(process, current_resources)
#    ]
#    ongoing_processes = []
#    time_elapsed = 0

#    # 現在実行中のプロセスがあるか、実行可能なプロセスがあるかを確認する
#    while executable_processes or ongoing_processes:
#        for process in executable_processes:
#            # その都度、次のプロセスが実行可能かどうかを確認する
#            if can_schedule(process, current_resources) and process.priority > 0:
#                # リソースを更新する
#                update_resources(current_resources, process)
#                # 時間を更新する
#                process.start_time = time_elapsed
#                process.end_time = time_elapsed + process.delay
#                logging.info(
#                    f"Executed: {process.name}, "
#                    f"Start Time: {process.start_time}, "
#                    f"End Time: {process.end_time}"
#                )
#                logging.info("-------------------")

#                # 現在実行中のプロセスに追加する
#                ongoing_processes.append(process)

#        # 実行中のプロセスが無ければ、終了する
#        if not ongoing_processes:
#            break

#        # 実行中のプロセスがあれば、時間を進める
#        eariest_end_time = min(
#            process.end_time for process in ongoing_processes if process.end_time
#        )
#        time_elapsed = eariest_end_time

#        # 実行中のプロセスが終了したら、実行中のプロセスから削除する
#        ongoing_processes = [
#            process for process in ongoing_processes if process.end_time != time_elapsed
#        ]
#        # 実行可能なプロセスを更新する
#        executable_processes = [
#            process for process in processes if can_schedule(process, current_resources)
#        ]
#        # 更新済みリソースで優先順位を更新する
#        if optimize.final_product:
#            assign_priorities(processes, optimize.final_product, current_resources)


# print(f"Final Stock: {current_resources}, Total Time: {time_elapsed}")


if __name__ == "__main__":

    if len(sys.argv) > 1:
        file_name = sys.argv[1]
    else:
        print("No file name provided as argument.")
        sys.exit(1)

    stock, processes, optimize = parse_krpsim_file(file_name)

    # 最終成果物が指定されている場合、優先度を割り当て、優先度の高い順にプロセスをソートする
    if optimize.final_product:
        assign_priorities(processes, optimize.final_product, stock.resources)
        processes.sort(key=lambda x: x.priority, reverse=True)

    # ログ機能を追加する
    logging.basicConfig(
        filename=file_name + ".log", level=logging.INFO, format="%(message)s"
    )

    logging.info("Stock: %s", stock.resources)
    logging.info("-------------------")
    parallel_schedule(stock, processes)
