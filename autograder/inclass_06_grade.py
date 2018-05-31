class GradeObj():

    def __init__(self):



        # When feedback can be released
        # Format as Y-m-d-H:M:S in 24hr time
        self.deadline = "2018-05-31-16:00:00"

        self.header = ""
        self.max_score = 1.0 # highest possible grade (excluding bonus)
        self.maxwait = 10 # seconds to wait before timeout


        self.functions = ["inclass6"]
        self.classes = []

        self.pts =  {"inclass6": 0.20
            }

        self.tests = {"inclass6": [1, 2, 16, 256, 65536 ]
             }

    def inclass6(self, n):

        if n == 1:
            return 1

        seq = [1, 1]

        while sum(seq) < n:
            seq.append(seq[-1] + seq[-2])

        return len(seq)
