from parse_krpsim_file import parse_krpsim_file
import logging
import sys


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
    current_resources = stock.resources.copy()
    executable_processes = [
        process for process in processes if can_schedule(process, current_resources)
    ]
    ongoing_processes = []
    time_elapsed = 0

    # 現在実行中のプロセスがあるか、実行可能なプロセスがあるかを確認する
    while executable_processes or ongoing_processes:
        for process in executable_processes:
            # その都度、次のプロセスが実行可能かどうかを確認する
            if can_schedule(process, current_resources):
                # リソースを更新する
                update_resources(current_resources, process)
                # 時間を更新する
                process.start_time = time_elapsed
                process.end_time = time_elapsed + process.delay
                logging.info(
                    f"Executed: {process.name}, "
                    f"Start Time: {process.start_time}, "
                    f"End Time: {process.end_time}"
                )
                logging.info("-------------------")

                # 現在実行中のプロセスに追加する
                ongoing_processes.append(process)

        # 実行中のプロセスが無ければ、終了する
        if not ongoing_processes:
            break

        # 実行中のプロセスがあれば、時間を進める
        eariest_end_time = min(
            process.end_time for process in ongoing_processes if process.end_time
        )
        time_elapsed = eariest_end_time

        # 実行中のプロセスが終了したら、実行中のプロセスから削除する
        ongoing_processes = [
            process for process in ongoing_processes if process.end_time != time_elapsed
        ]
        # 実行可能なプロセスを更新する
        executable_processes = [
            process for process in processes if can_schedule(process, current_resources)
        ]
        executable_processes = [
            process
            for process in executable_processes
            if all(
                process.name != ongoing_process.name
                for ongoing_process in ongoing_processes
            )
        ]

    print(f"Final Stock: {current_resources}, Total Time: {time_elapsed}")


if __name__ == "__main__":

    if len(sys.argv) > 1:
        file_name = sys.argv[1]
    else:
        print("No file name provided as argument.")
        sys.exit(1)

    stock, processes, optimize = parse_krpsim_file(file_name)

    # ログ機能を追加する
    logging.basicConfig(
        filename=file_name + ".log", level=logging.INFO, format="%(message)s"
    )

    logging.info("Stock: %s", stock.resources)
    logging.info("-------------------")

    parallel_schedule(stock, processes)
