from multiprocessing import Pool, cpu_count

tuples = (
    ('test1',),
    ('test2',),
    ('test3',),
    ('test4',),
)

def printmulti(tuples):
    return tuples[0]

def main():
    num_cores = cpu_count()
    with Pool(num_cores) as pool:
        for result in pool.imap_unordered(printmulti,tuples):
            print(result)

if __name__ == "__main__":
    main()