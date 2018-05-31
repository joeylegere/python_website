"""
An autograder for Python assignments.
Refactoring old copy starting 04-05-17
"""

import os
import importlib

from multiprocessing import Process, Value, Manager

import nbformat


def test_execute(compiled, retval):
    """
    Attempts to execute compiled Python bytecode to check for "unrunnable"
    code, e.g. anything with calls to undefined functions.
    """

    try:
        namespace = {}
        exec(compiled, namespace)
        retval.value = 1
        return True

    except:
        retval.value = 0
        return False

class Formatter(object):
    """
    Given a filename, an id, and a boolean, creates cleaned code that
    should run, with error-prone code commented out.
    """

    def __init__(self, *args, **kwargs):

        self.infile = args[0]
        self.notebook = kwargs.get('notebook', True)
        self.maxwait = kwargs.get('maxwait', 5)
        self.unwanted_imports = kwargs.get('unwanted_imports', ['this', "multiprocessing", "time"])
        self.unwanted_functions = kwargs.get('unwanted_functions', ["help", "print"])

        self.code = self.clean_code()

    def validate_code_cell(self, raw_code):
        """
        Test if a code cell can run by itself.
        #:   Indicates the line contains an unwanted import.
        ##:  Indicates the cell had a syntax error.
        ###: Indicates the cell could not run for other reasons
             (usually calling an undefined function)
        """

        formatted_code = [""] * 3

        # Remove any inconvenient functions like sleep or help
        # Comment out with a single #
        for row in raw_code.split("\n"):

            added_1 = False
            for fun in self.unwanted_functions:
                if fun in row and "(" in row and ")" in row:
                    ident = row[0:row.find(fun)]
                    trail = row[row.find(fun):]
                    formatted_code[0] += "\n%spass # %s" % (ident, trail)
                    added_1 = True
                    break

            if any(lib in row for lib in self.unwanted_imports) and not added_1 and 'import' in row:
                added_1 = True
                formatted_code[0] += "\n# %s" % row
            if not added_1:
                formatted_code[0] += "\n%s" % row

        # Comment out syntactically incorrect code with ##
        try:
            compiled = compile(formatted_code[0], "placeholder.py", "exec")
            formatted_code[1] = formatted_code[0]
        except:
            for row in formatted_code[0].split("\n"):
                formatted_code[1] += "\n## %s" % row

        # now instantiate a new namespace and comment out "unrunnable"
        # code, using ###.
        # (this handles calls to undefined functions)
        if 'compiled' in locals():
            retval = Value('d', 1)
            proc = Process(target=test_execute, args=(compiled, retval))
            proc.start()
            proc.join(self.maxwait)
            if proc.is_alive():
                proc.terminate()
                retval.value = 0

            if retval.value == 1:
                formatted_code[2] = formatted_code[1]
            else:
                final_code = ""
                for row in formatted_code[1].split("\n"):
                    final_code += "\n### %s" % row
        else:
            formatted_code[2] = formatted_code[1]

        return formatted_code[2]


    def clean_code(self):
        """
        Extract useable code from infile and save it as a .py file.
        """

        if self.notebook is True:
            notebook = nbformat.read(self.infile, 4)
            code_cells = []
            for cell in notebook["cells"]:
                if cell["cell_type"] == "code":
                    code_cells.append(cell)
        else:
            _ = open("self.infile", "r")
            code_cells = [_.read()]
            _.close()

        clean_code = ""
        # Comment out unuseable cells
        for cell in code_cells:
            raw_code = cell['source']
            fmt = self.validate_code_cell(raw_code)
            clean_code += fmt + "\n\n"

        return clean_code

class GradeHelper(object):
    """
    Class to help Autograder by grading functions and objects
    """


    def __init__(self, *args):

        self.maxwait = args[0]
        self.lenient = args[1]
        self.tolerance = args[2]
        self.places = args[3]


    def almost_equal(self, x, y):
        """
        Recursively compares lists, tuples, or numbers x, y for
        approximate equality with the given number of decimal digits
        """

        if isinstance(x, bool) and isinstance(y, bool): return x == y
        
        if type(x) != type(y):
            if (isinstance(x, tuple) or isinstance(x, list)) and (isinstance(y, tuple) or isinstance(y, list)):
                return all(self.almost_equal(a, b) for a, b in zip(x, y))

            return x == y # in case of int == float 

        if self.lenient is True:
            if isinstance(x, str):
                x = x.replace(" ", "")
                x = x.replace("\n", "")
                y = y.replace(" ", "")
                y = y.replace("\n", "")
                return (len(x) == len(y)) and (set(x) == set(y))
            elif isinstance(x, float) and isinstance(y, float):
                x = abs(x)
                y = abs(y)
                diff = abs(x - y)
                cutoff = min(self.tolerance * x, self.tolerance * y)
                return diff < cutoff
            else:
                return (x == y)

        if isinstance(x, list) or isinstance(x, tuple):
            return all(self.almost_equal(a, b) for a, b in zip(x, y))

        elif isinstance(x, float) or isinstance(x, int):
            return round(abs(x - y), self.places) == 0
        elif isinstance(x, set) or isinstance(x, str):
            return x == y
        else:
            return x == y


    def grade_function(self, fun, answer_fun, student_code, raw_code, gradeobj, shared):
        """
        Grades the given function with the given input.
        Returns -1 if the function is not defined
        Returns false in the case of an error.
        """

        in_vals = gradeobj.tests[fun]
        try:
            exec(student_code, globals(), locals())
            student_fun = globals()[fun]
        except Exception as e:
            shared["FEEDBACK"] += "\n    Test Failed"

        # iterate through inputs

        for inputs in in_vals:

            # Get correct answer.
            # Try/Except in case correct answer is to raise an error
            try:
                if isinstance(inputs, tuple) and len(inputs) > 1:
                    correct_answer = answer_fun(*inputs)
                else:
                    correct_answer = answer_fun(inputs)

                if isinstance(inputs, tuple) and 'destfile' in inputs:
                    _ = open('destfile')
                    correct_answer = _.read()
                    _.close()
            except Exception as e:
                correct_answer = e

            # Get student answer.
            try:
                if isinstance(inputs, tuple) and len(inputs) > 1:
                    student_answer = student_fun(*inputs)
                else:
                    student_answer = student_fun(inputs)

                if isinstance(inputs, tuple) and 'destfile' in inputs:
                    _ = open('destfile')
                    student_answer = _.read()
                    _.close()
            except Exception as e:
                student_answer = e

            pts = gradeobj.pts[fun]
            score = 0
            if self.almost_equal(correct_answer, student_answer):
                score = pts
                shared[fun] += pts

            # Format for Jupyter
            if isinstance(correct_answer, str):
                correct_answer = correct_answer.replace("\n", "\n\n")
            if isinstance(student_answer, str):
                student_answer = student_answer.replace("\n", "\n\n")

            shared["FEEDBACK"] += "\n    Test Case:                %s" % str(inputs)
            shared["FEEDBACK"] += "\n    Expected output:          %s" % str(correct_answer)

            shared["FEEDBACK"] += "\n    Your output:              %s" % str(student_answer)
            shared["FEEDBACK"] += "\n    Score:                    %s / %s" % (score, pts)
            shared["FEEDBACK"] += "\n\n"

        return True


class Autograder(object):
    """
    Higher level class to automatically grade a given file with a given
    grading script.
    """
    def __init__(self, *args, **kwargs):

        self.infile = args[0]

        gradeobj = args[1]
        x = importlib.import_module("autograder.%s_grade" % gradeobj)
        self.gradeobj = x.GradeObj()

        # Get student code
        fmt = Formatter(self.infile)
        self.raw_code = fmt.code
        self.student_code = compile(fmt.code, "", "exec")

        # Create the grading helper object
        maxwait = kwargs.get("maxwait", 15)
        lenient = kwargs.get("lenient", False)
        tolerance = kwargs.get('tolereance', 0.075)
        places = kwargs.get("dec_places", 5)

        self.grade_helper = GradeHelper(maxwait, lenient, tolerance, places)

        # For storing grades across subprocesses
        manager = Manager()
        self.shared= manager.dict()

        self.total_grade = 0


    def grade(self):

        # Instantiate the students funtions as locals():
        # We also put them into globals(), so that they can call their own subfunctions
        exec(self.student_code, globals())
        exec(self.student_code, locals())
        for question in self.gradeobj.tests.keys():
            self.shared[question] = 0
        self.shared["FEEDBACK"] = self.gradeobj.header + "\n\n"

        for fun in self.gradeobj.functions:
            max_score = self.gradeobj.pts[fun] * len(self.gradeobj.tests[fun])
            self.shared["FEEDBACK"] += "### Function: %s()" % fun
            if fun not in locals():
                self.shared["FEEDBACK"] += "\nYou have not defined %s" % fun
            else:
                answer_fun = getattr(self.gradeobj, fun)

                proc = Process(target=self.grade_helper.grade_function,
                               args=(fun, answer_fun, self.student_code, self.raw_code, \
                                     self.gradeobj, self.shared))
                proc.start()
                proc.join(self.gradeobj.maxwait)
                if proc.is_alive():
                    proc.terminate()
                    self.shared["FEEDBACK"] += "\n     Could not complete, took too long"

            self.shared["FEEDBACK"] += "\n#### TOTAL FOR: %s: %s / %s\n\n" % \
                            (fun, self.shared[fun], max_score)

        self.total_grade = sum(x if (type(x) == int or type(x) == float)\
                                        else 0 \
                                        for x in self.shared.values())

        self.shared['total_grade'] = self.total_grade
        self.shared['max_grade'] = self.gradeobj.max_score
        self.shared['deadline'] = self.gradeobj.deadline

        return True
