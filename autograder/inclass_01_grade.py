class GradeObj():

    def __init__(self):



        # When feedback can be released
        # Format as Y-m-d-H:M:S in 24hr time
        self.deadline = "2018-05-24-13:45:00"

        self.header = ""
        self.max_score = 1.0 # highest possible grade (excluding bonus)
        self.maxwait = 10 # seconds to wait before timeout


        self.functions = ["inclass1"]
        self.classes = []

        self.pts =  {"inclass1": 0.20
            }

        self.tests = {"inclass1": [(1, 2, 3), (2, 6, 4), (3, 6, 9), (-5, -3, -1), (1, 1, 1)]
             }

    def inclass1(self, x, y, z):
        return max((x, y, z))
