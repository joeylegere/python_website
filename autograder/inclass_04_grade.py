class GradeObj():

    def __init__(self):



        # When feedback can be released
        # Format as Y-m-d-H:M:S in 24hr time
        self.deadline = "2018-05-29-13:50:30"

        self.header = ""
        self.max_score = 1.0 # highest possible grade (excluding bonus)
        self.maxwait = 10 # seconds to wait before timeout


        self.functions = ["inclass4"]
        self.classes = []

        self.pts =  {"inclass4": 0.50
            }

        self.tests = {"inclass4": [ ([1, 2, 3], [4, 5, 7]), ([0, 3, 1], [-5, 1, 2])]
             }

    def inclass4(self, x, y):

        s = 0
        for i in range(len(x)):
        
            s = s + x[i] * y[i]

        return s
