class GradeObj():

    def __init__(self):

        # When feedback can be released
        # Format as Y-m-d-H:M:S in 24hr time
        self.deadline = "2018-06-05-12:59:59"

        self.header = ""
        self.max_score = 20.0 # highest possible grade (excluding bonus)
        self.maxwait = 10 # seconds to wait before timeout


        self.functions = ["heron", "estimate_pi", "knuts", "ksg", "wizard_change", "letter_grade", "specific_sum"]
        self.classes = []

        self.pts =  {"heron": 1.0,
                     "estimate_pi": 1.0,
                     "knuts":1.0,
                     "ksg":1.0,
                     "wizard_change":0.75,
                     "letter_grade":0.5,
                     "specific_sum": 1.0
            }

        self.tests = {"heron": [(13, 14, 15), (10, 9, 8), (12, 16, 20), (36, 60, 48)],
                     "estimate_pi": [5, 10, 27, 17],
                     "knuts":[(1, 2, 3), (3, 4, 0), (5, 0, 3), (0, 3, 7)],
                     "ksg":[1024, 1015, 314],
                     "wizard_change":[(1, 2, 3, 3, 4, 4), (1, 2, 3, 0, 2, 1), (3, 4, 1, 0, 0, 2), (33, 19, 1, 570, 39, 0)],
                     "letter_grade":[40, 50, 55, 60, 65, 70, 75, 80],
                     "specific_sum": [(500, 3, 5), (400, 2, 3), (700, 7, 13)]
             }

    def heron(self, a, b, c):
        s = (a + b + c) / 2
        A = (s * (s - a) * (s - b) * (s - c)) ** 0.5

        return A


    def estimate_pi(self, N):
        s = 0

        for i in range(1, N + 1):
            s = s + 1 / (i ** 2)

        return (6 * s) ** 0.5

    def knuts(self, k, s, g):
        # Your code here.
        return k + s * 29 + g * 29 * 17

        return k

    def ksg(self, k):
        g = k // 493
        s = (k % 493) // 29
        k = k % 29

        return (k, s, g)

    def wizard_change(self, ck, cs, cg, k, s, g):

        ck = self.knuts(ck, cs, cg)
        k2 = self.knuts(k, s, g)

        if ck < k2:
            k2 = k2 - ck

        k, s, g = self.ksg(k2)

        return (k, s, g)

    def letter_grade(self, score):

        if score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        elif score >= 50:
            return "D"
        else:
            return "F"


    def specific_sum(self, N, x, y):

        return sum([i if i % x == 0 or i % y == 0 else 0 for i in range(N + 1)])
