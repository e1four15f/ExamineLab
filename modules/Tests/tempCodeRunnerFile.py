def perform_testing(self, user_pr_path, input_dir, test_paths, test_preproc = None, input_preproc = None, args = None):
        
    print('in perform_testing')
    tests = [self.get_tests_by_paths(test_paths, preproc = test_preproc)]
    inputs = list(load_from(input_dir, preproc = input_preproc))
    program_outs = []
    for pr_input in inputs:
        program_outs.add(self.spawn_user_proc(user_pr_path, pr_input, args)
    passed = {}

    print(program_outs)
    for i, b in verification.verifyMultiple(program_outs, tests):
        passed[test_paths[i]] = b
        
    return passed