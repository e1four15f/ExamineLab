import os, re


class Tester:
    def __init__(self, dir, code, tests, filename='code.'):
        self.dir = dir
        self.code = code
        self.in_content = [t.input for t in tests]
        self.ans_content = [t.output for t in tests]
        self.filename = filename

    def _compare_files(self, files_content1, files_content2):
        if len(files_content1) != len(files_content2):
            return False

        def cmp(a, b):
            return (a > b)-(a < b)

        for i, j in zip(files_content1, files_content2):
            if cmp(i, j) != 0:
                return False

        return True

    def _apply_tests(self):
        for out, ans in zip(self.out_content, self.ans_content):
            if not self._compare_files(out, ans):
                yield False
            else:
                yield True

    def _run_user_code(self):
        for i in range(len(self.in_content)):
            print('Running {}, test {}'.format(self.filename, i))
            dir = self.dir[1:]
            stdin = dir + 'in/' + str(i)
            stdout = dir + 'out/' + str(i)

            os.system('python ' + dir + self.filename + ' < ' + stdin + ' > ' + stdout)

    def _create_files(self):
        path = os.getcwd() + self.dir + '/'
        if not os.path.exists(path):
            os.makedirs(path)

        with open(path + self.filename, 'w') as file:
            file.write(re.sub(r'\r', '', self.code))

        for i in ['/in', '/ans', '/out']:
            if not os.path.exists(path + i):
                os.makedirs(path + i)

        for i in range(len(self.in_content)):
            with open(path + 'in/' + str(i), 'w', newline=os.linesep) as file:
                file.write(re.sub(r'\r', '', self.in_content[i]))
            with open(path + 'ans/' + str(i), 'w', newline=os.linesep) as file:
                file.write(re.sub(r'\r', '', self.ans_content[i]))

    def run(self):
        self._create_files()
        self._run_user_code()

        #generator = self._apply_tests()
        #for i, x in enumerate(generator):
        #    print('Test {} {}!'.format(i, 'passed' if x else 'failed'))
