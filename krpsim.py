from parse_krpsim_file import parse_krpsim_file


if __name__ == "__main__":
    stock, processes, optimize = parse_krpsim_file("resources/ikea")
    print(stock.resources)
    for process in processes:
        print(process.name, process.needs, process.results, process.delay)
    print(optimize.goals)
