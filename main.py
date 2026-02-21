import csv
from collections import namedtuple

def main():
    with open("params-output.csv") as tests_file:
        csv_reader = csv.reader(filter(lambda row: row[0] != "#", tests_file))
        headers = next(csv_reader)
        TestCase = namedtuple("TestCase", headers)
        for row in csv_reader:
            test_case = TestCase(*row)
            print(test_case)

if __name__ == "__main__":
    main()