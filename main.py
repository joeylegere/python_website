import os
import shutil
import sqlite3
import logging

from multiprocessing import Process
from time import strftime, strptime, localtime, sleep
from flask import Flask, request, redirect, flash, render_template

from werkzeug.utils import secure_filename

try:
    import extensions
except:
    pass


UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = set(['zip', 'ipynb', 'py'])

# Create our loggers
terselog = logging.getLogger("terse")
terselog.setLevel(logging.DEBUG)
fh1 = logging.FileHandler("logs/submissions_terse.log")
formatter = logging.Formatter("%(asctime)s    %(levelname)s\t%(message)s", datefmt="%m/%d/%Y %H:%M:%S")
fh1.setFormatter(formatter)
terselog.addHandler(fh1)
terselog.info("Restarted")

verboselog = logging.getLogger("verbose")
verboselog.setLevel(logging.DEBUG)
fh2 = logging.FileHandler("logs/submissions_verbose.log")
fh2.setFormatter(formatter)
verboselog.addHandler(fh2)
verboselog.info("Restarted")

app = Flask(__name__)
app.config["PROPAGATE_EXCEPTIONS"]=True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2 MB
app.secret_key = os.environ['PYSITE_KEY']


# non-flask helper functions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def autograde(asst, fname):
    """
    Autogrades the given file, fname, using the template for asst.
    Returns the "shared" object from the autograder, a dictionary that contains
    string feedback and total grade for each question.
    """

    import autograder.autograder as autograder
    grader = autograder.Autograder(fname, asst, lenient=True, tolerance=0.001)

    p = Process(target=grader.grade)
    p.start()
    p.join(30)
    grade = grader.shared

    return grade


def save_grade(macid, shared, asst, fname, ip):


    while os.path.exists('semaphore'):
        sleep(0.1)
    # Lazily lock critical section
    with open('semaphore', 'w'):
        os.utime('semaphore')

    try:
        t = strftime("%Y-%m-%d-%H:%M:%S")

        grade = shared['total_grade']
        maxgrade = shared['max_grade']

        # Create a dictionary of individual question scores, remove extraneous data.
        meta = dict(shared)
        meta.pop("FEEDBACK", None)
        meta.pop("total_grade", None)
        meta.pop("max_grade", None)
        meta.pop('deadline', None)

        # Insert results into the database
        db = sqlite3.connect('grades.db')
        cur = db.cursor()
        query = """
                INSERT INTO grades (macid, assignment, time, grade, maxgrade, fname, meta)
                VALUES ("%s", "%s", "%s", %s, %s, "%s", "%s")
                """ % (macid, asst, t, grade, maxgrade, fname, meta)
        cur.execute(query)

        db.commit()
        db.close()

        # Only write log if we successfully added to db
        msg = "\n".join([macid + "\t" + fname, str(shared['FEEDBACK'])])  # message for verbose log with all feedback
        verboselog.info(msg)
        terselog.info("%s submitted %s from %s and got: %s / %s" % (macid, asst, ip, grade, maxgrade))

        # Remove lock
        os.remove('semaphore')

        return True

    except Exception as e: # Ensure we continue executing so we can free the semaphore
        os.remove('semaphore')
        terselog.warning("%s submitted %s from %s but encountered an error." % (macid, asst, ip))
        verboselog.warning(e)

        return False


def basic_feedback(shared):

    out = ["TOTAL: %s / %s" % (shared["total_grade"], shared["max_grade"])]
    hide = ["FEEDBACK", "total_grade", "max_grade", "linked_file", "submit_time", "deadline"]
    for k in shared.keys():
        if k not in hide: out.append("%s:    %s" % (k, float(shared[k])))

    return feedback_form(out)


def process_grade(shared, macid, asst, fname, ip):
    """
    Provides feedback if submitted past the deadline. Otherwise,
    updates the current saved grade and provides the total score.
    """

    curtime = localtime()
    deadline = shared["deadline"]

    if (macid, asst) in extensions.ext.keys():
        deadline = extensions.ext[(macid, asst)]

    deadline = strptime(deadline, "%Y-%m-%d-%H:%M:%S")

    if curtime > deadline:
        feedback = shared["FEEDBACK"]
        terselog.info("%s submitted %s from %s and received feedback" % (macid, asst, ip))
        verboselog.info("%s %s from %s feedback:" % (macid, asst, ip))
        verboselog.info(feedback)
        return feedback_form(feedback.split("\n"))
    if save_grade(macid, shared, asst, fname, ip):
        return basic_feedback(shared)
    return feedback_form(["An error occured while processing your submission."])

@app.route("/upload", methods=["GET", "POST"])
def upload():

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No selected file')
            return redirect(request.url)
        f = request.files['file']
        asst = request.form['asst']
        macid = request.form['macid']
        # Handling common exceptions

        terselog.info("%s tried to upload %s" % (macid, asst))

        if f.filename == '':
            flash('No selected file')
            return redirect(request.url)
        elif asst == "None":
            flash("Specify the assignment number")
            return redirect(request.url)
        elif macid == "":
            flash("Enter your macid")
            return redirect(request.url)

        elif not allowed_file(f.filename):
            flash("Invalid extension. Upload a .ipynb file")
            return redirect(request.url)

        # If valid file, accept it and save:
        if f:

            # save a copy for archiving
            t = strftime("%Y-%m-%d-%H:%M:%S")
            ip = request.environ["REMOTE_ADDR"]
            filename = "%s_%s_%s_%s" % (t, ip, macid,
                                        secure_filename(f.filename))
            fname1 = os.path.join(app.config['UPLOAD_FOLDER'], asst, filename)

            if not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], asst)):
                os.mkdir(os.path.join(app.config['UPLOAD_FOLDER'], asst))
            f.save(fname1)

            # save a copy to grade, overwrite most recent upload if it exists
            filename = secure_filename(f.filename)
            if not os.path.exists(os.path.join("./autograder", asst)):
                os.mkdir(os.path.join("./autograder", asst))

            fname2 = os.path.join("./autograder", asst, macid) + ".ipynb"
            shutil.copyfile(fname1, fname2)

            terselog.info("%s submitted %s for grading from %s" % (macid, asst, ip))
            try:
                shared = autograde(asst, fname2)
            except Exception as e:
                terselog.warning("%s encountered an exception while grading %s." % (macid, asst))
                verboselog.warning(e)
                verboselog.warning("Occured in: %s" % fname1)
                return feedback_form(["An error occured while processing your submission."])
            
            return process_grade(shared, macid, asst, fname1, ip)

    return render_template("ul_basic.html")


@app.route('/feedback')
def feedback_form(msg):
    if isinstance(msg, str):
        flash(msg)
    else:
        for m in msg:
            flash(m)
    return render_template("base.html")


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/outline')
def outline():
    return render_template('outline.html')


@app.route('/content')
def content():
    return render_template('content.html')


if __name__ == "__main__":
    app.run(host = '0.0.0.0', port=16384, threaded=True)
