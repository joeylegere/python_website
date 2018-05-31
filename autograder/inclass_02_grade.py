class GradeObj():

    def __init__(self):



        # When feedback can be released
        # Format as Y-m-d-H:M:S in 24hr time
        self.deadline = "2018-05-24-14:20:00"

        self.header = ""
        self.max_score = 1.0 # highest possible grade (excluding bonus)
        self.maxwait = 10 # seconds to wait before timeout


        self.functions = ["inclass2"]
        self.classes = []

        self.pts =  {"inclass2": 0.20
            }

        self.tests = {"inclass2": [198, 224, 987, 1230, 565]
             }

    def inclass2(self, rt):

        if rt > 1000:
            return "too slow"
        elif rt < 200:
            return "too fast"
        else:
            return "good"


