"""
Run-time efficiency: to be completely honest, I don't know how to answer this question. I imagine there are
definitely more efficient ways to do this and am not really sure if this is linear/quadratic/exponential. If it was SQL I
would check the execution plans and indexing strategies with execution time to work on efficiency, I'm not sure what process
to use for python scripts
"""

PERFORM_TESTS = True


def load_raw_data():
    """Read the input file and break into a list of test cases. Sort each test case
    entry into normal/mutated lists for supplemental processing"""
    try:
        input_file = open("input.txt", "r")
    except:
        raise Exception(
            "Could not locate file './input.txt'. Check that file exists and try again."
        )
    input_file_lines = input_file.readlines()
    test_cases_raw = []
    norm_data_raw = []
    mut_data_raw = []
    for line in input_file_lines:
        if line == "\n" and (len(norm_data_raw) > 0 or len(mut_data_raw) > 0):
            """save results for a test_case if there is valid data and we've hit a newline. reset local variables"""
            test_cases_raw.append({"norm": norm_data_raw, "mut": mut_data_raw})
            norm_data_raw = []
            mut_data_raw = []
        else:
            """break the single line into an array using the ',' character and store in
            the appropriate NORM or MUT list"""
            raw_data = line.strip().split(",")
            if raw_data[0].upper().startswith("NORM"):
                raw_data.pop(0)  # remove the text "NORM" from the array of sample_ids
                norm_data_raw.append(raw_data)
            elif raw_data[0].upper().startswith("MUT"):
                raw_data.pop(0)  # remove the text "MUT" from the array of sample_ids
                mut_data_raw.append(raw_data)
            else:
                raise Exception(f"Unknown genotype encountered: '{line.strip()}'")
    if len(norm_data_raw) > 0 or len(mut_data_raw) > 0:
        """catch for files that do not end with an empty line"""
        test_cases_raw.append({"norm": norm_data_raw, "mut": mut_data_raw})
    print(test_cases_raw)
    return test_cases_raw


def load_mappings(test_cases):
    """review the test_case data and find unique sample-to-genotype mappings (if possible). this function returns
    a list of 'test_result' dicts which can be formatted as desired for final reporting to end user"""
    final_test_results = []
    for test_case in test_cases:
        final_result = {
            "norm_genotypes": [],
            "mut_genotypes": [],
            "nonunique": False,
            "inconsistent": False,
        }
        if "norm" in test_case:
            """load all of the NORM samples first"""
            for result_array in test_case["norm"]:
                for result in result_array:
                    if not result in final_result["norm_genotypes"]:
                        final_result["norm_genotypes"].append(result)
        if "mut" in test_case:
            """check all MUT mixtures after NORM samples are loaded"""
            for result_array in test_case["mut"]:
                result_index = 0
                mutation_counter = 0
                for result in result_array:
                    result_index += 1
                    if final_result["nonunique"] or final_result["inconsistent"]:
                        break
                    if not result in final_result["norm_genotypes"]:
                        """only 'count' a mutation if it is unique. if the sample exists in the NORM list already
                        do not count as a mutation. if this mutation is not the only possible mutation after comparing
                        to NORM list, mark as 'nonunique'. if all samples in  a mutation mixture exist in NORM list,
                        mark as inconclusive"""
                        mutation_counter += 1
                        if mutation_counter > 1:
                            final_result["nonunique"] = True
                        if not result in final_result["mut_genotypes"]:
                            final_result["mut_genotypes"].append(result)
                    elif result_index == len(result) and mutation_counter < 1:
                        final_result["inconsistent"] = True

        final_test_results.append(final_result)
    return final_test_results


def sort_sample_ids(result):
    """take the two lists of sample_ids and combine into a single sorted list"""
    full_list = []
    for r in result["norm_genotypes"]:
        full_list.append((int(r), "NORM"))
    for r in result["mut_genotypes"]:
        full_list.append((int(r), "MUT"))
    full_list = sorted(full_list, key=lambda x: x[0])
    return [f"{entry[0]},{entry[1]}" for entry in full_list]


def print_results(results):
    """take a list of results and format a display to the user"""
    for result in results:
        if result["inconsistent"]:
            print("INCONSISTENT\n")
        elif result["nonunique"]:
            print("NONUNIQUE\n")
        else:
            print(f"MUT COUNT: {len(result['mut_genotypes'])}")
            print(f"NORM COUNT: {len(result['norm_genotypes'])}")
            for sample in sort_sample_ids(result):
                print(sample)
            print()


def main():
    raw_data = load_raw_data()
    results = load_mappings(raw_data)
    print_results(results)


def test_sort_sample_ids():
    result = {"norm_genotypes": [0, 9, 1], "mut_genotypes": [3, 2]}
    assert sort_sample_ids(result) == ["0,NORM", "1,NORM", "2,MUT", "3,MUT", "9,NORM"]


def test_sample_mappings_no_mut():
    raw_data = [{"norm": [["0", "1"], ["1", "2"], ["0", "2"]], "mut": []}]
    assert load_mappings(raw_data) == [
        {
            "norm_genotypes": ["0", "1", "2"],
            "mut_genotypes": [],
            "nonunique": False,
            "inconsistent": False,
        }
    ]


def test_sample_mappings_no_norm():
    raw_data = [{"norm": [], "mut": [["0", "1"], ["1", "2"]]}]
    assert load_mappings(raw_data) == [
        {
            "norm_genotypes": [],
            "mut_genotypes": ["0", "1"],
            "nonunique": True,
            "inconsistent": False,
        }
    ]


def test_sample_mappings():
    raw_data = [{"norm": [["100", "110"]], "mut": [["110", "12"]]}]
    assert load_mappings(raw_data) == [
        {
            "norm_genotypes": ["100", "110"],
            "mut_genotypes": ["12"],
            "nonunique": False,
            "inconsistent": False,
        }
    ]


def tests():
    """some sample unit testing - set flag at top of code to 'True' to run tests"""
    print("Tests started..")
    test_sort_sample_ids()
    test_sample_mappings_no_mut()
    test_sample_mappings_no_norm()
    test_sample_mappings()
    print("All tests passed successfully.")


if __name__ == "__main__" and not PERFORM_TESTS:
    main()
elif PERFORM_TESTS:
    tests()
