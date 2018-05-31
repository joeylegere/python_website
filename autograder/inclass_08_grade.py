class GradeObj():

    def __init__(self):



        # When feedback can be released
        # Format as Y-m-d-H:M:S in 24hr time
        self.deadline = "2018-05-31-16:00:00"

        self.header = ""
        self.max_score = 1.0 # highest possible grade (excluding bonus)
        self.maxwait = 10 # seconds to wait before timeout


        self.functions = ["inclass8"]
        self.classes = []

        self.pts =  {"inclass8": 0.50
            }

        self.tests = {"inclass8": ["This sentence needs more words.", "This sentence is overly ponderous, lacking direction, and clearly has too many words, and yet, it is still going, perhaps never to end--or not."]
             }

    def inclass8(self, s):
        s = s.split(" ")
        total_length = 0

        for i in range(len(s)):
            total_length = total_length + len(s[i])

        avg_length = total_length / len(s)

        return avg_length
