class GradeObj():

    def __init__(self):



        # When feedback can be released
        # Format as Y-m-d-H:M:S in 24hr time
        self.deadline = "2018-05-29-13:25:00"

        self.header = ""
        self.max_score = 1.0 # highest possible grade (excluding bonus)
        self.maxwait = 10 # seconds to wait before timeout


        self.functions = ["inclass3"]
        self.classes = []

        self.pts =  {"inclass3": 0.50
            }

        self.tests = {"inclass3": ["Where did you come from, where did you go, where did you come from cotton eye Joe?", "N vwls hrr"]
             }

    def inclass3(self, s):
        vowels = "aeiouAEIOU"
        count = 0

        for i in s:
            if i in vowels:
                count += 1

        return count
