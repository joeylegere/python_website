class GradeObj():

    def __init__(self):



        # When feedback can be released
        # Format as Y-m-d-H:M:S in 24hr time
        self.deadline = "2018-05-31-16:00:00"

        self.header = ""
        self.max_score = 1.0 # highest possible grade (excluding bonus)
        self.maxwait = 10 # seconds to wait before timeout


        self.functions = ["inclass7"]
        self.classes = []

        self.pts =  {"inclass7": 1.0
            }

        import string
        self.dec = dec = {chr(ord(k) + 1):k for k in string.ascii_letters + string.punctuation + " "}
        self.tests = {"inclass7": [ ('Pcwjpvtmz-!uif!uftu!dbtft!xjmm!cf!npsf!cpsjoh!uibo!uif!fybnqmft!jo!uif!opufcppl', self.dec)]
             }



    def inclass7(self, c, d):
        outstr = ""

        for i in c:
            outstr += d[i]

        return outstr
