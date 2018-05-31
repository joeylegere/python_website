class GradeObj():

    def __init__(self):



        # When feedback can be released
        # Format as Y-m-d-H:M:S in 24hr time
        self.deadline = "2018-05-29-14:10:00"

        self.header = ""
        self.max_score = 1.0 # highest possible grade (excluding bonus)
        self.maxwait = 10 # seconds to wait before timeout


        self.functions = ["inclass5"]
        self.classes = []

        self.pts =  {"inclass5": 0.50
            }

        self.tests = {"inclass5": [ (7, 3), (21, 7)]
             }

    def inclass5(self, x, y):
        return (x % y == 0)
