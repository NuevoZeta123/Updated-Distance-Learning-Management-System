from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key_here_change_in_production'

# MySQL Configuation
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '08037005637',
    'database': 'dlms_db'
}

def get_db():
    return mysql.connector.connect(**MYSQL_CONFIG)

# Upload Configuration
UPLOAD_FOLDER = 'static/uploads/videos'
ASSIGNMENT_FOLDER = 'static/uploads/assignments'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'wmv', 'mkv'}
ASSIGNMENT_EXTENSIONS = {'pdf', 'docx', 'doc', 'txt', 'jpg', 'jpeg', 'png', 'gif'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ASSIGNMENT_FOLDER'] = ASSIGNMENT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Ensure upload directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ASSIGNMENT_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_assignment_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ASSIGNMENT_EXTENSIONS

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'role' not in session or session['role'] != role:
                flash('Access denied. Insufficient permissions.', 'danger')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Routes
@app.route('/')
def index():
    return render_template('dlms_index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Please provide both email and password.', 'danger')
            return render_template('dlms_login.html')
        
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT user_id, full_name, email, password_hash, role, is_active FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        
        if user and check_password_hash(user[3], password):
            if user[5] == 0:
                flash('Your account has been deactivated. Contact administrator.', 'warning')
                return render_template('dlms_login.html')
            
            session['user_id'] = user[0]
            session['full_name'] = user[1]
            session['email'] = user[2]
            session['role'] = user[4]
            
            flash(f'Welcome, {user[1]}!', 'success')
            
            if user[4] == 'administrator':
                return redirect(url_for('admin_dashboard'))
            elif user[4] == 'lecturer':
                return redirect(url_for('lecturer_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('dlms_login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

# Administrator Routes
@app.route('/admin/dashboard')
@login_required
@role_required('administrator')
def admin_dashboard():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users WHERE role = 'student'")
    student_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM users WHERE role = 'lecturer'")
    lecturer_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM courses")
    course_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM lectures")
    lecture_count = cur.fetchone()[0]
    cur.close()
    conn.close()
    
    return render_template('dlms_admin_dashboard.html', 
                         student_count=student_count,
                         lecturer_count=lecturer_count,
                         course_count=course_count,
                         lecture_count=lecture_count)

@app.route('/admin/users')
@login_required
@role_required('administrator')
def admin_users():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT user_id, full_name, email, role, is_active FROM users ORDER BY user_id DESC")
    users = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('dlms_admin_users.html', users=users)

@app.route('/admin/create_user', methods=['GET', 'POST'])
@login_required
@role_required('administrator')
def admin_create_user():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        
        if not all([full_name, email, password, role]):
            flash('All fields are required.', 'danger')
            return render_template('dlms_admin_create_user.html')
        
        if role not in ['student', 'lecturer', 'administrator']:
            flash('Invalid role selected.', 'danger')
            return render_template('dlms_admin_create_user.html')
        
        password_hash = generate_password_hash(password)
        
        conn = get_db()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users (full_name, email, password_hash, role) VALUES (%s, %s, %s, %s)",
                       (full_name, email, password_hash, role))
            conn.commit()
            flash(f'User {full_name} created successfully!', 'success')
            return redirect(url_for('admin_users'))
        except Exception as e:
            conn.rollback()
            flash('Email already exists or database error.', 'danger')
        finally:
            cur.close()
            conn.close()
    
    return render_template('dlms_admin_create_user.html')

@app.route('/admin/toggle_user/<int:user_id>')
@login_required
@role_required('administrator')
def admin_toggle_user(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE users SET is_active = NOT is_active WHERE user_id = %s", (user_id,))
    conn.commit()
    cur.close()
    conn.close()
    flash('User status updated successfully.', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
@role_required('administrator')
def admin_delete_user(user_id):
    # Prevent self-deletion
    if user_id == session['user_id']:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin_users'))
    
    conn = get_db()
    cur = conn.cursor()
    
    # Check if this is the last administrator
    cur.execute("SELECT COUNT(*) FROM users WHERE role = 'administrator' AND is_active = TRUE")
    admin_count = cur.fetchone()[0]
    
    cur.execute("SELECT role FROM users WHERE user_id = %s", (user_id,))
    user_role = cur.fetchone()
    
    if user_role and user_role[0] == 'administrator' and admin_count <= 1:
        cur.close()
        conn.close()
        flash('Cannot delete the last active administrator.', 'danger')
        return redirect(url_for('admin_users'))
    
    # Delete the user (CASCADE will handle related records)
    try:
        cur.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
        conn.commit()
        flash('User deleted successfully.', 'success')
    except Exception as e:
        conn.rollback()
        flash('Error deleting user. Please try again.', 'danger')
    finally:
        cur.close()
        conn.close()
    
    return redirect(url_for('admin_users'))

@app.route('/admin/courses')
@login_required
@role_required('administrator')
def admin_courses():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""SELECT c.course_id, c.course_title, c.course_description, u.full_name, 
                   (SELECT COUNT(*) FROM lectures WHERE course_id = c.course_id) as lecture_count
                   FROM courses c 
                   LEFT JOIN users u ON c.lecturer_id = u.user_id 
                   ORDER BY c.course_id DESC""")
    courses = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('dlms_admin_courses.html', courses=courses)

# Lecturer Routes
@app.route('/lecturer/dashboard')
@login_required
@role_required('lecturer')
def lecturer_dashboard():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM courses WHERE lecturer_id = %s", (session['user_id'],))
    course_count = cur.fetchone()[0]
    cur.execute("""SELECT COUNT(*) FROM lectures l 
                   JOIN courses c ON l.course_id = c.course_id 
                   WHERE c.lecturer_id = %s""", (session['user_id'],))
    lecture_count = cur.fetchone()[0]
    cur.close()
    conn.close()
    
    return render_template('dlms_lecturer_dashboard.html', 
                         course_count=course_count,
                         lecture_count=lecture_count)

@app.route('/lecturer/courses')
@login_required
@role_required('lecturer')
def lecturer_courses():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""SELECT c.course_id, c.course_title, c.course_description,
                   (SELECT COUNT(*) FROM lectures WHERE course_id = c.course_id) as lecture_count
                   FROM courses c WHERE c.lecturer_id = %s 
                   ORDER BY c.course_id DESC""", (session['user_id'],))
    courses = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('dlms_lecturer_courses.html', courses=courses)

@app.route('/lecturer/create_course', methods=['GET', 'POST'])
@login_required
@role_required('lecturer')
def lecturer_create_course():
    if request.method == 'POST':
        course_title = request.form.get('course_title')
        course_description = request.form.get('course_description')
        
        if not course_title or not course_description:
            flash('All fields are required.', 'danger')
            return render_template('dlms_lecturer_create_course.html')
        
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO courses (course_title, course_description, lecturer_id) VALUES (%s, %s, %s)",
                   (course_title, course_description, session['user_id']))
        conn.commit()
        cur.close()
        conn.close()
        
        flash('Course created successfully!', 'success')
        return redirect(url_for('lecturer_courses'))
    
    return render_template('dlms_lecturer_create_course.html')

@app.route('/lecturer/upload_lecture', methods=['GET', 'POST'])
@login_required
@role_required('lecturer')
def lecturer_upload_lecture():
    if request.method == 'POST':
        lecture_title = request.form.get('lecture_title')
        lecture_description = request.form.get('lecture_description')
        course_id = request.form.get('course_id')
        video_file = request.files.get('video_file')
        
        if not all([lecture_title, lecture_description, course_id, video_file]):
            flash('All fields including video file are required.', 'danger')
            return redirect(url_for('lecturer_upload_lecture'))
        
        if video_file.filename == '':
            flash('No video file selected.', 'danger')
            return redirect(url_for('lecturer_upload_lecture'))
        
        if not allowed_file(video_file.filename):
            flash('Invalid file type. Allowed: mp4, avi, mov, wmv, mkv', 'danger')
            return redirect(url_for('lecturer_upload_lecture'))
        
        filename = secure_filename(video_file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        try:
            video_file.save(filepath)
            video_path = f"uploads/videos/{filename}"
            
            conn = get_db()
            cur = conn.cursor()
            cur.execute("""INSERT INTO lectures (lecture_title, lecture_description, video_path, course_id) 
                          VALUES (%s, %s, %s, %s)""",
                       (lecture_title, lecture_description, video_path, course_id))
            conn.commit()
            cur.close()
            conn.close()
            
            flash('Lecture uploaded successfully!', 'success')
            return redirect(url_for('lecturer_courses'))
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            flash('Error uploading lecture. Please try again.', 'danger')
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT course_id, course_title FROM courses WHERE lecturer_id = %s", (session['user_id'],))
    courses = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template('dlms_lecturer_upload.html', courses=courses)

@app.route('/lecturer/course/<int:course_id>/lectures')
@login_required
@role_required('lecturer')
def lecturer_course_lectures(course_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT course_title FROM courses WHERE course_id = %s AND lecturer_id = %s", 
               (course_id, session['user_id']))
    course = cur.fetchone()
    
    if not course:
        cur.close()
        conn.close()
        flash('Course not found or access denied.', 'danger')
        return redirect(url_for('lecturer_courses'))
    
    cur.execute("""SELECT lecture_id, lecture_title, lecture_description, upload_date 
                   FROM lectures WHERE course_id = %s ORDER BY upload_date DESC""", (course_id,))
    lectures = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template('dlms_lecturer_course_lectures.html', course=course, lectures=lectures, course_id=course_id)

@app.route('/lecturer/lecture/<int:lecture_id>/delete', methods=['POST'])
@login_required
@role_required('lecturer')
def delete_lecture(lecture_id):
    conn = get_db()
    cur = conn.cursor()
    
    # Check if lecture belongs to lecturer's course
    cur.execute("""SELECT l.lecture_id, l.video_path, c.course_id
                   FROM lectures l
                   JOIN courses c ON l.course_id = c.course_id
                   WHERE l.lecture_id = %s AND c.lecturer_id = %s""", 
               (lecture_id, session['user_id']))
    lecture = cur.fetchone()
    
    if not lecture:
        cur.close()
        conn.close()
        flash('Lecture not found or access denied.', 'danger')
        return redirect(url_for('lecturer_courses'))
    
    # Delete the video file if it exists
    if lecture[1] and os.path.exists(lecture[1]):
        try:
            os.remove(lecture[1])
        except:
            pass  # Continue even if file deletion fails
    
    # Delete the lecture (CASCADE will handle related records)
    try:
        cur.execute("DELETE FROM lectures WHERE lecture_id = %s", (lecture_id,))
        conn.commit()
        flash('Lecture deleted successfully.', 'success')
    except Exception as e:
        conn.rollback()
        flash('Error deleting lecture.', 'danger')
    
    cur.close()
    conn.close()
    return redirect(url_for('lecturer_course_lectures', course_id=lecture[2]))

# Student Routes
@app.route('/student/dashboard')
@login_required
@role_required('student')
def student_dashboard():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""SELECT COUNT(*) FROM enrollments WHERE student_id = %s""", (session['user_id'],))
    enrolled_count = cur.fetchone()[0]
    cur.close()
    conn.close()
    
    return render_template('dlms_student_dashboard.html', enrolled_count=enrolled_count)

@app.route('/student/courses')
@login_required
@role_required('student')
def student_courses():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""SELECT c.course_id, c.course_title, c.course_description, u.full_name,
                   (SELECT COUNT(*) FROM lectures WHERE course_id = c.course_id) as lecture_count
                   FROM courses c 
                   JOIN users u ON c.lecturer_id = u.user_id
                   WHERE c.course_id IN (SELECT course_id FROM enrollments WHERE student_id = %s)
                   ORDER BY c.course_id DESC""", (session['user_id'],))
    courses = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('dlms_student_courses.html', courses=courses)

@app.route('/student/course/<int:course_id>/unenroll', methods=['POST'])
@login_required
@role_required('student')
def student_unenroll_course(course_id):
    conn = get_db()
    cur = conn.cursor()
    
    # Check if student is enrolled
    cur.execute("SELECT enrollment_id FROM enrollments WHERE student_id = %s AND course_id = %s", 
               (session['user_id'], course_id))
    enrollment = cur.fetchone()
    
    if not enrollment:
        cur.close()
        conn.close()
        flash('You are not enrolled in this course.', 'danger')
        return redirect(url_for('student_courses'))
    
    # Check if student has submitted assignments or taken exams
    cur.execute("SELECT COUNT(*) FROM submissions WHERE student_id = %s AND assignment_id IN (SELECT assignment_id FROM assignments WHERE course_id = %s)", 
               (session['user_id'], course_id))
    submission_count = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM exam_attempts WHERE student_id = %s AND exam_id IN (SELECT exam_id FROM exams WHERE course_id = %s)", 
               (session['user_id'], course_id))
    attempt_count = cur.fetchone()[0]
    
    if submission_count > 0 or attempt_count > 0:
        cur.close()
        conn.close()
        flash('Cannot unenroll from course with submitted assignments or completed exams.', 'danger')
        return redirect(url_for('student_courses'))
    
    # Delete enrollment
    try:
        cur.execute("DELETE FROM enrollments WHERE student_id = %s AND course_id = %s", 
                   (session['user_id'], course_id))
        conn.commit()
        flash('Successfully unenrolled from course.', 'success')
    except Exception as e:
        conn.rollback()
        flash('Error unenrolling from course.', 'danger')
    
    cur.close()
    conn.close()
    return redirect(url_for('student_courses'))

@app.route('/student/enroll')
@login_required
@role_required('student')
def student_enroll():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""SELECT c.course_id, c.course_title, c.course_description, u.full_name
                   FROM courses c 
                   JOIN users u ON c.lecturer_id = u.user_id
                   WHERE c.course_id NOT IN (SELECT course_id FROM enrollments WHERE student_id = %s)
                   ORDER BY c.course_id DESC""", (session['user_id'],))
    courses = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('dlms_student_enroll.html', courses=courses)

@app.route('/student/enroll/<int:course_id>')
@login_required
@role_required('student')
def student_enroll_course(course_id):
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO enrollments (student_id, course_id) VALUES (%s, %s)",
                   (session['user_id'], course_id))
        conn.commit()
        flash('Successfully enrolled in course!', 'success')
    except:
        conn.rollback()
        flash('Already enrolled or error occurred.', 'danger')
    finally:
        cur.close()
        conn.close()
    return redirect(url_for('student_enroll'))

@app.route('/student/course/<int:course_id>/lectures')
@login_required
@role_required('student')
def student_course_lectures(course_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""SELECT course_id FROM enrollments 
                   WHERE student_id = %s AND course_id = %s""", (session['user_id'], course_id))
    enrollment = cur.fetchone()
    
    if not enrollment:
        cur.close()
        conn.close()
        flash('You are not enrolled in this course.', 'danger')
        return redirect(url_for('student_courses'))
    
    cur.execute("SELECT course_title FROM courses WHERE course_id = %s", (course_id,))
    course = cur.fetchone()
    
    cur.execute("""SELECT lecture_id, lecture_title, lecture_description, video_path, upload_date 
                   FROM lectures WHERE course_id = %s ORDER BY upload_date DESC""", (course_id,))
    lectures = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template('dlms_student_course_lectures.html', course=course, lectures=lectures, course_id=course_id)

@app.route('/student/lecture/<int:lecture_id>')
@login_required
@role_required('student')
def student_view_lecture(lecture_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""SELECT l.lecture_id, l.lecture_title, l.lecture_description, l.video_path, 
                   c.course_title, c.course_id
                   FROM lectures l
                   JOIN courses c ON l.course_id = c.course_id
                   WHERE l.lecture_id = %s""", (lecture_id,))
    lecture = cur.fetchone()
    
    if not lecture:
        cur.close()
        conn.close()
        flash('Lecture not found.', 'danger')
        return redirect(url_for('student_courses'))
    
    cur.execute("""SELECT course_id FROM enrollments 
                   WHERE student_id = %s AND course_id = %s""", (session['user_id'], lecture[5]))
    enrollment = cur.fetchone()
    cur.close()
    conn.close()
    
    if not enrollment:
        flash('Access denied. You are not enrolled in this course.', 'danger')
        return redirect(url_for('student_courses'))
    
    return render_template('dlms_student_view_lecture.html', lecture=lecture)

# ===== ASSIGNMENT ROUTES =====

# Lecturer: Create Assignment
@app.route('/lecturer/assignment/create/<int:course_id>', methods=['GET', 'POST'])
@login_required
@role_required('lecturer')
def create_assignment(course_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT course_title FROM courses WHERE course_id = %s AND lecturer_id = %s", 
               (course_id, session['user_id']))
    course = cur.fetchone()
    
    if not course:
        cur.close()
        conn.close()
        flash('Course not found or access denied.', 'danger')
        return redirect(url_for('lecturer_courses'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        due_date = request.form.get('due_date')
        total_points = request.form.get('total_points', 5)
        
        if not all([title, description, due_date]):
            flash('All fields are required.', 'danger')
            return render_template('dlms_create_assignment.html', course=course, course_id=course_id)
        
        cur.execute("""INSERT INTO assignments (course_id, title, description, due_date, total_points, created_by) 
                      VALUES (%s, %s, %s, %s, %s, %s)""",
                   (course_id, title, description, due_date, total_points, session['user_id']))
        conn.commit()
        cur.close()
        conn.close()
        
        flash('Assignment created successfully!', 'success')
        return redirect(url_for('lecturer_assignments', course_id=course_id))
    
    cur.close()
    conn.close()
    return render_template('dlms_create_assignment.html', course=course, course_id=course_id)

# Lecturer: View Assignments for a Course
@app.route('/lecturer/assignments/<int:course_id>')
@login_required
@role_required('lecturer')
def lecturer_assignments(course_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT course_title FROM courses WHERE course_id = %s AND lecturer_id = %s", 
               (course_id, session['user_id']))
    course = cur.fetchone()
    
    if not course:
        cur.close()
        conn.close()
        flash('Course not found or access denied.', 'danger')
        return redirect(url_for('lecturer_courses'))
    
    cur.execute("""SELECT assignment_id, title, description, due_date, total_points, created_at
                   FROM assignments WHERE course_id = %s ORDER BY due_date DESC""", (course_id,))
    assignments = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template('dlms_lecturer_assignments.html', course=course, assignments=assignments, course_id=course_id)

@app.route('/lecturer/assignment/<int:assignment_id>/delete', methods=['POST'])
@login_required
@role_required('lecturer')
def delete_assignment(assignment_id):
    conn = get_db()
    cur = conn.cursor()
    
    # Check if assignment belongs to lecturer's course
    cur.execute("""SELECT a.assignment_id, c.course_id
                   FROM assignments a
                   JOIN courses c ON a.course_id = c.course_id
                   WHERE a.assignment_id = %s AND c.lecturer_id = %s""", 
               (assignment_id, session['user_id']))
    assignment = cur.fetchone()
    
    if not assignment:
        cur.close()
        conn.close()
        flash('Assignment not found or access denied.', 'danger')
        return redirect(url_for('lecturer_courses'))
    
    # Check if assignment has been graded
    cur.execute("SELECT COUNT(*) FROM submissions WHERE assignment_id = %s AND status = 'graded'", (assignment_id,))
    graded_count = cur.fetchone()[0]
    
    if graded_count > 0:
        cur.close()
        conn.close()
        flash('Cannot delete assignment that has graded submissions.', 'danger')
        return redirect(url_for('lecturer_assignments', course_id=assignment[1]))
    
    # Delete the assignment (CASCADE will handle submissions)
    try:
        cur.execute("DELETE FROM assignments WHERE assignment_id = %s", (assignment_id,))
        conn.commit()
        flash('Assignment deleted successfully.', 'success')
    except Exception as e:
        conn.rollback()
        flash('Error deleting assignment.', 'danger')
    
    cur.close()
    conn.close()
    return redirect(url_for('lecturer_assignments', course_id=assignment[1]))

# Lecturer: View Submissions for an Assignment
@app.route('/lecturer/assignment/<int:assignment_id>/submissions')
@login_required
@role_required('lecturer')
def view_submissions(assignment_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""SELECT a.assignment_id, a.title, c.course_id, c.course_title
                   FROM assignments a
                   JOIN courses c ON a.course_id = c.course_id
                   WHERE a.assignment_id = %s AND c.lecturer_id = %s""", 
               (assignment_id, session['user_id']))
    assignment = cur.fetchone()
    
    if not assignment:
        cur.close()
        conn.close()
        flash('Assignment not found or access denied.', 'danger')
        return redirect(url_for('lecturer_courses'))
    
    cur.execute("""SELECT s.submission_id, s.student_id, u.full_name, s.file_path, s.submission_time, s.status, s.points
                   FROM submissions s
                   JOIN users u ON s.student_id = u.user_id
                   WHERE s.assignment_id = %s ORDER BY s.submission_time DESC""", (assignment_id,))
    submissions = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template('dlms_view_submissions.html', assignment=assignment, submissions=submissions)

# Lecturer: Grade Submission
@app.route('/lecturer/submission/<int:submission_id>/grade', methods=['GET', 'POST'])
@login_required
@role_required('lecturer')
def grade_submission(submission_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""SELECT s.submission_id, s.assignment_id, s.student_id, u.full_name, s.file_path, s.points, s.feedback, a.total_points
                   FROM submissions s
                   JOIN users u ON s.student_id = u.user_id
                   JOIN assignments a ON s.assignment_id = a.assignment_id
                   WHERE s.submission_id = %s""", (submission_id,))
    submission = cur.fetchone()
    
    if not submission:
        cur.close()
        conn.close()
        flash('Submission not found.', 'danger')
        return redirect(url_for('lecturer_courses'))
    
    if request.method == 'POST':
        points = request.form.get('points')
        feedback = request.form.get('feedback')
        
        cur.execute("""UPDATE submissions SET points = %s, feedback = %s, status = 'graded' WHERE submission_id = %s""",
                   (points, feedback, submission_id))
        conn.commit()
        cur.close()
        conn.close()
        
        flash('Submission graded successfully!', 'success')
        return redirect(url_for('view_submissions', assignment_id=submission[1]))
    
    cur.close()
    conn.close()
    return render_template('dlms_grade_submission.html', submission=submission)

# Student: View Assignments
@app.route('/student/assignments/<int:course_id>')
@login_required
@role_required('student')
def student_assignments(course_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""SELECT course_id FROM enrollments 
                   WHERE student_id = %s AND course_id = %s""", (session['user_id'], course_id))
    enrollment = cur.fetchone()
    
    if not enrollment:
        cur.close()
        conn.close()
        flash('You are not enrolled in this course.', 'danger')
        return redirect(url_for('student_courses'))
    
    cur.execute("SELECT course_title FROM courses WHERE course_id = %s", (course_id,))
    course = cur.fetchone()
    
    # Get all assignments for the course
    cur.execute("""SELECT a.assignment_id, a.title, a.description, a.due_date, a.total_points
                   FROM assignments a
                   WHERE a.course_id = %s ORDER BY a.due_date DESC""", (course_id,))
    all_assignments = cur.fetchall()
    
    # Auto-grade non-submissions past deadline
    for assignment in all_assignments:
        assignment_id = assignment[0]
        due_date = assignment[3]
        
        # Check if deadline has passed
        if due_date and due_date < datetime.now():
            # Check if student has a submission
            cur.execute("SELECT submission_id FROM submissions WHERE assignment_id = %s AND student_id = %s",
                       (assignment_id, session['user_id']))
            submission = cur.fetchone()
            
            # If no submission and deadline passed, auto-grade with 0
            if not submission:
                cur.execute("""INSERT INTO submissions (assignment_id, student_id, status, points) 
                              VALUES (%s, %s, 'graded', 0)""",
                           (assignment_id, session['user_id']))
                conn.commit()
    
    cur.execute("""SELECT a.assignment_id, a.title, a.description, a.due_date, a.total_points,
                          s.submission_id, s.file_path, s.points, s.status
                   FROM assignments a
                   LEFT JOIN submissions s ON a.assignment_id = s.assignment_id AND s.student_id = %s
                   WHERE a.course_id = %s ORDER BY a.due_date DESC""", (session['user_id'], course_id))
    assignments = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template('dlms_student_assignments.html', course=course, assignments=assignments, course_id=course_id)

# Lecturer: Allow Resubmission (Change Status Back to In Progress)
@app.route('/lecturer/submission/<int:submission_id>/allow-resubmission', methods=['POST'])
@login_required
@role_required('lecturer')
def allow_resubmission(submission_id):
    conn = get_db()
    cur = conn.cursor()
    
    # Get submission and verify lecturer owns the course
    cur.execute("""SELECT s.submission_id, a.assignment_id, a.course_id
                   FROM submissions s
                   JOIN assignments a ON s.assignment_id = a.assignment_id
                   WHERE s.submission_id = %s AND a.created_by = %s""",
               (submission_id, session['user_id']))
    submission = cur.fetchone()
    
    if not submission:
        cur.close()
        conn.close()
        flash('Submission not found.', 'danger')
        return redirect(url_for('lecturer_courses'))
    
    try:
        # Update status back to submitted so student can resubmit
        cur.execute("UPDATE submissions SET status = 'submitted', points = NULL, feedback = NULL WHERE submission_id = %s",
                   (submission_id,))
        conn.commit()
        cur.close()
        conn.close()
        
        flash('Status updated. Student can now resubmit this assignment.', 'success')
        return redirect(url_for('view_submissions', assignment_id=submission[1]))
    except Exception as e:
        cur.close()
        conn.close()
        flash('Error updating submission status.', 'danger')
        return redirect(url_for('view_submissions', assignment_id=submission[1]))

# Student: Submit Assignment
@app.route('/student/assignment/<int:assignment_id>/submit', methods=['GET', 'POST'])
@login_required
@role_required('student')
def submit_assignment(assignment_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""SELECT a.assignment_id, a.title, a.due_date, a.total_points, a.course_id, c.course_title
                   FROM assignments a
                   JOIN courses c ON a.course_id = c.course_id
                   WHERE a.assignment_id = %s""", (assignment_id,))
    assignment = cur.fetchone()
    
    if not assignment:
        cur.close()
        conn.close()
        flash('Assignment not found.', 'danger')
        return redirect(url_for('student_courses'))
    
    # Check if student already submitted and it's graded
    cur.execute("SELECT submission_id, status FROM submissions WHERE assignment_id = %s AND student_id = %s",
               (assignment_id, session['user_id']))
    existing = cur.fetchone()
    
    if existing and existing[1] == 'graded':
        cur.close()
        conn.close()
        flash('This assignment has been graded and cannot be resubmitted. Ask your lecturer to allow resubmission.', 'warning')
        return redirect(url_for('student_assignments', course_id=assignment[4]))
    
    if request.method == 'POST':
        assignment_file = request.files.get('assignment_file')
        
        if not assignment_file or assignment_file.filename == '':
            flash('Please select a file to submit.', 'danger')
            return render_template('dlms_submit_assignment.html', assignment=assignment)
        
        if not allowed_assignment_file(assignment_file.filename):
            flash('Invalid file type. Allowed: PDF, Word, Images, TXT', 'danger')
            return render_template('dlms_submit_assignment.html', assignment=assignment)
        
        filename = secure_filename(assignment_file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{session['user_id']}_{filename}"
        filepath = os.path.join(app.config['ASSIGNMENT_FOLDER'], filename)
        
        try:
            assignment_file.save(filepath)
            file_path = f"uploads/assignments/{filename}"
            
            # Check if student already submitted
            cur.execute("SELECT submission_id FROM submissions WHERE assignment_id = %s AND student_id = %s",
                       (assignment_id, session['user_id']))
            existing = cur.fetchone()
            
            if existing:
                # Update existing submission
                cur.execute("""UPDATE submissions SET file_path = %s, submission_time = NOW(), status = 'submitted' 
                              WHERE submission_id = %s""", (file_path, existing[0]))
            else:
                # Create new submission
                cur.execute("""INSERT INTO submissions (assignment_id, student_id, file_path, status) 
                              VALUES (%s, %s, %s, 'submitted')""",
                           (assignment_id, session['user_id'], file_path))
            
            conn.commit()
            cur.close()
            conn.close()
            
            flash('Assignment submitted successfully!', 'success')
            return redirect(url_for('student_assignments', course_id=assignment[4]))
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            flash('Error submitting assignment. Please try again.', 'danger')
            cur.close()
            conn.close()
    
    cur.close()
    conn.close()
    return render_template('dlms_submit_assignment.html', assignment=assignment)

# ===== Q&A ROUTES =====

# View Course Questions
@app.route('/course/<int:course_id>/questions')
@login_required
def view_course_questions(course_id):
    conn = get_db()
    cur = conn.cursor()
    
    # Check if user is enrolled in or teaches the course
    if session['role'] == 'student':
        cur.execute("""SELECT course_id FROM enrollments 
                       WHERE student_id = %s AND course_id = %s""", (session['user_id'], course_id))
        enrollment = cur.fetchone()
        if not enrollment:
            cur.close()
            conn.close()
            flash('You are not enrolled in this course.', 'danger')
            return redirect(url_for('student_courses'))
    elif session['role'] == 'lecturer':
        cur.execute("""SELECT course_id FROM courses 
                       WHERE course_id = %s AND lecturer_id = %s""", (course_id, session['user_id']))
        course_check = cur.fetchone()
        if not course_check:
            cur.close()
            conn.close()
            flash('Course not found or access denied.', 'danger')
            return redirect(url_for('lecturer_courses'))
    
    cur.execute("SELECT course_title FROM courses WHERE course_id = %s", (course_id,))
    course = cur.fetchone()
    
    cur.execute("""SELECT q.question_id, q.title, q.content, u.full_name, q.created_at,
                          (SELECT COUNT(*) FROM answers WHERE question_id = q.question_id) as answer_count
                   FROM questions q
                   JOIN users u ON q.student_id = u.user_id
                   WHERE q.course_id = %s
                   ORDER BY q.created_at DESC""", (course_id,))
    questions = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template('dlms_course_questions.html', course=course, course_id=course_id, questions=questions)

# Ask a Question
@app.route('/course/<int:course_id>/ask-question', methods=['GET', 'POST'])
@login_required
@role_required('student')
def ask_question(course_id):
    conn = get_db()
    cur = conn.cursor()
    
    # Verify student is enrolled
    cur.execute("""SELECT course_id FROM enrollments 
                   WHERE student_id = %s AND course_id = %s""", (session['user_id'], course_id))
    enrollment = cur.fetchone()
    
    if not enrollment:
        cur.close()
        conn.close()
        flash('You are not enrolled in this course.', 'danger')
        return redirect(url_for('student_courses'))
    
    cur.execute("SELECT course_title FROM courses WHERE course_id = %s", (course_id,))
    course = cur.fetchone()
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        
        if not all([title, content]):
            flash('All fields are required.', 'danger')
            return render_template('dlms_ask_question.html', course=course, course_id=course_id)
        
        cur.execute("""INSERT INTO questions (course_id, student_id, title, content) 
                      VALUES (%s, %s, %s, %s)""",
                   (course_id, session['user_id'], title, content))
        conn.commit()
        cur.close()
        conn.close()
        
        flash('Question posted successfully!', 'success')
        return redirect(url_for('view_course_questions', course_id=course_id))
    
    cur.close()
    conn.close()
    return render_template('dlms_ask_question.html', course=course, course_id=course_id)

# View Question Details and Answers
@app.route('/question/<int:question_id>')
@login_required
def view_question_detail(question_id):
    conn = get_db()
    cur = conn.cursor()
    
    # Get question details
    cur.execute("""SELECT q.question_id, q.course_id, q.title, q.content, u.full_name, u.user_id, q.created_at
                   FROM questions q
                   JOIN users u ON q.student_id = u.user_id
                   WHERE q.question_id = %s""", (question_id,))
    question = cur.fetchone()
    
    if not question:
        cur.close()
        conn.close()
        flash('Question not found.', 'danger')
        return redirect(url_for('student_courses'))
    
    course_id = question[1]
    
    # Check access
    if session['role'] == 'student':
        cur.execute("""SELECT course_id FROM enrollments 
                       WHERE student_id = %s AND course_id = %s""", (session['user_id'], course_id))
        enrollment = cur.fetchone()
        if not enrollment:
            cur.close()
            conn.close()
            flash('You are not enrolled in this course.', 'danger')
            return redirect(url_for('student_courses'))
    elif session['role'] == 'lecturer':
        cur.execute("""SELECT course_id FROM courses 
                       WHERE course_id = %s AND lecturer_id = %s""", (course_id, session['user_id']))
        course_check = cur.fetchone()
        if not course_check:
            cur.close()
            conn.close()
            flash('Course not found or access denied.', 'danger')
            return redirect(url_for('lecturer_courses'))
    
    # Get answers
    cur.execute("""SELECT a.answer_id, a.content, u.full_name, a.created_at
                   FROM answers a
                   JOIN users u ON a.lecturer_id = u.user_id
                   WHERE a.question_id = %s
                   ORDER BY a.created_at ASC""", (question_id,))
    answers = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template('dlms_question_detail.html', question=question, answers=answers, course_id=course_id)

# Answer a Question (Lecturer Only)
@app.route('/question/<int:question_id>/answer', methods=['POST'])
@login_required
@role_required('lecturer')
def answer_question(question_id):
    conn = get_db()
    cur = conn.cursor()
    
    # Get question and verify lecturer owns the course
    cur.execute("""SELECT q.question_id, q.course_id
                   FROM questions q
                   JOIN courses c ON q.course_id = c.course_id
                   WHERE q.question_id = %s AND c.lecturer_id = %s""", (question_id, session['user_id']))
    question = cur.fetchone()
    
    if not question:
        cur.close()
        conn.close()
        flash('Question not found or access denied.', 'danger')
        return redirect(url_for('lecturer_courses'))
    
    content = request.form.get('content')
    
    if not content:
        flash('Answer content is required.', 'danger')
    else:
        cur.execute("""INSERT INTO answers (question_id, lecturer_id, content) 
                      VALUES (%s, %s, %s)""",
                   (question_id, session['user_id'], content))
        conn.commit()
        flash('Answer posted successfully!', 'success')
    
    cur.close()
    conn.close()
    return redirect(url_for('view_question_detail', question_id=question_id))

# Delete Answer (Lecturer Only)
@app.route('/answer/<int:answer_id>/delete', methods=['POST'])
@login_required
@role_required('lecturer')
def delete_answer(answer_id):
    conn = get_db()
    cur = conn.cursor()
    
    # Get answer and verify lecturer posted it
    cur.execute("""SELECT a.answer_id, a.question_id
                   FROM answers a
                   WHERE a.answer_id = %s AND a.lecturer_id = %s""", (answer_id, session['user_id']))
    answer = cur.fetchone()
    
    if not answer:
        cur.close()
        conn.close()
        flash('Answer not found or access denied.', 'danger')
        return redirect(url_for('lecturer_courses'))
    
    question_id = answer[1]
    
    cur.execute("DELETE FROM answers WHERE answer_id = %s", (answer_id,))
    conn.commit()
    cur.close()
    conn.close()
    
    flash('Answer deleted successfully!', 'success')
    return redirect(url_for('view_question_detail', question_id=question_id))

# ===== EXAM ROUTES =====

# Lecturer: Create Exam
@app.route('/lecturer/exam/create/<int:course_id>', methods=['GET', 'POST'])
@login_required
@role_required('lecturer')
def create_exam(course_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT course_title FROM courses WHERE course_id = %s AND lecturer_id = %s", 
               (course_id, session['user_id']))
    course = cur.fetchone()
    
    if not course:
        cur.close()
        conn.close()
        flash('Course not found or access denied.', 'danger')
        return redirect(url_for('lecturer_courses'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        duration = request.form.get('duration')
        total_points = request.form.get('total_points', 100)
        camera_required = request.form.get('camera_required') == 'on'
        
        if not all([title, description, duration]):
            flash('All fields are required.', 'danger')
            return render_template('dlms_create_exam.html', course=course, course_id=course_id)
        
        cur.execute("""INSERT INTO exams (course_id, title, description, duration_minutes, total_points, camera_required, created_by) 
                      VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                   (course_id, title, description, duration, total_points, camera_required, session['user_id']))
        conn.commit()
        exam_id = cur.lastrowid
        cur.close()
        conn.close()
        
        flash('Exam created! Now add questions.', 'success')
        return redirect(url_for('add_exam_questions', exam_id=exam_id))
    
    cur.close()
    conn.close()
    return render_template('dlms_create_exam.html', course=course, course_id=course_id)

# Lecturer: Add Questions to Exam
@app.route('/lecturer/exam/<int:exam_id>/add-questions', methods=['GET', 'POST'])
@login_required
@role_required('lecturer')
def add_exam_questions(exam_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""SELECT e.exam_id, e.title, e.course_id, c.course_title
                   FROM exams e
                   JOIN courses c ON e.course_id = c.course_id
                   WHERE e.exam_id = %s AND c.lecturer_id = %s""", (exam_id, session['user_id']))
    exam = cur.fetchone()
    
    if not exam:
        cur.close()
        conn.close()
        flash('Exam not found or access denied.', 'danger')
        return redirect(url_for('lecturer_courses'))
    
    if request.method == 'POST':
        question_text = request.form.get('question_text')
        option_a = request.form.get('option_a')
        option_b = request.form.get('option_b')
        option_c = request.form.get('option_c')
        option_d = request.form.get('option_d')
        correct_answer = request.form.get('correct_answer')
        points = request.form.get('points', 1)
        
        if not all([question_text, option_a, option_b, option_c, option_d, correct_answer]):
            flash('All fields are required.', 'danger')
            return render_template('dlms_add_exam_questions.html', exam=exam)
        
        cur.execute("""INSERT INTO exam_questions (exam_id, question_text, option_a, option_b, option_c, option_d, correct_answer, points)
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                   (exam_id, question_text, option_a, option_b, option_c, option_d, correct_answer, points))
        conn.commit()
        flash('Question added successfully! Add more questions or finish.', 'success')
        cur.close()
        conn.close()
        return redirect(url_for('add_exam_questions', exam_id=exam_id))
    
    cur.execute("""SELECT exam_question_id, question_text, points FROM exam_questions 
                   WHERE exam_id = %s ORDER BY exam_question_id""", (exam_id,))
    questions = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template('dlms_add_exam_questions.html', exam=exam, questions=questions)

@app.route('/lecturer/exam/question/<int:question_id>/delete', methods=['POST'])
@login_required
@role_required('lecturer')
def delete_exam_question(question_id):
    conn = get_db()
    cur = conn.cursor()
    
    # Check if question belongs to lecturer's exam and if exam has been attempted
    cur.execute("""SELECT eq.exam_question_id, e.exam_id, c.course_id,
                          (SELECT COUNT(*) FROM exam_attempts WHERE exam_id = e.exam_id AND status = 'completed') as completed_attempts
                   FROM exam_questions eq
                   JOIN exams e ON eq.exam_id = e.exam_id
                   JOIN courses c ON e.course_id = c.course_id
                   WHERE eq.exam_question_id = %s AND c.lecturer_id = %s""", 
               (question_id, session['user_id']))
    question = cur.fetchone()
    
    if not question:
        cur.close()
        conn.close()
        flash('Question not found or access denied.', 'danger')
        return redirect(url_for('lecturer_courses'))
    
    # Don't allow deletion if exam has been completed by students
    if question[3] > 0:
        cur.close()
        conn.close()
        flash('Cannot delete question from exam that has been completed by students.', 'danger')
        return redirect(url_for('add_exam_questions', exam_id=question[1]))
    
    # Delete the question (CASCADE will handle exam_answers)
    try:
        cur.execute("DELETE FROM exam_questions WHERE exam_question_id = %s", (question_id,))
        conn.commit()
        flash('Question deleted successfully.', 'success')
    except Exception as e:
        conn.rollback()
        flash('Error deleting question.', 'danger')
    
    cur.close()
    conn.close()
    return redirect(url_for('add_exam_questions', exam_id=question[1]))

@app.route('/lecturer/exam/<int:exam_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('lecturer')
def edit_exam(exam_id):
    conn = get_db()
    cur = conn.cursor()
    
    # Check if exam belongs to lecturer and if it has been attempted
    cur.execute("""SELECT e.exam_id, e.title, e.description, e.duration_minutes, e.total_points, e.camera_required, c.course_title,
                          (SELECT COUNT(*) FROM exam_attempts WHERE exam_id = e.exam_id AND status = 'completed') as completed_attempts
                   FROM exams e
                   JOIN courses c ON e.course_id = c.course_id
                   WHERE e.exam_id = %s AND c.lecturer_id = %s""", 
               (exam_id, session['user_id']))
    exam = cur.fetchone()
    
    if not exam:
        cur.close()
        conn.close()
        flash('Exam not found or access denied.', 'danger')
        return redirect(url_for('lecturer_courses'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        camera_required = request.form.get('camera_required') == 'on'
        
        if not all([title, description]):
            flash('Title and description are required.', 'danger')
            return render_template('dlms_edit_exam.html', exam=exam)
        
        # Don't allow editing if exam has been completed by students
        if exam[7] > 0:
            cur.close()
            conn.close()
            flash('Cannot edit exam that has been completed by students.', 'danger')
            return redirect(url_for('view_course_exams', course_id=exam[0]))
        
        try:
            cur.execute("""UPDATE exams SET title = %s, description = %s, camera_required = %s 
                          WHERE exam_id = %s""", (title, description, camera_required, exam_id))
            conn.commit()
            flash('Exam updated successfully.', 'success')
        except Exception as e:
            conn.rollback()
            flash('Error updating exam.', 'danger')
        
        cur.close()
        conn.close()
        return redirect(url_for('view_course_exams', course_id=exam[0]))
    
    cur.close()
    conn.close()
    return render_template('dlms_edit_exam.html', exam=exam)

# View Course Exams
@app.route('/course/<int:course_id>/exams')
@login_required
def view_course_exams(course_id):
    conn = get_db()
    cur = conn.cursor()
    
    if session['role'] == 'student':
        cur.execute("""SELECT course_id FROM enrollments 
                       WHERE student_id = %s AND course_id = %s""", (session['user_id'], course_id))
        enrollment = cur.fetchone()
        if not enrollment:
            cur.close()
            conn.close()
            flash('You are not enrolled in this course.', 'danger')
            return redirect(url_for('student_courses'))
    elif session['role'] == 'lecturer':
        cur.execute("""SELECT course_id FROM courses 
                       WHERE course_id = %s AND lecturer_id = %s""", (course_id, session['user_id']))
        course_check = cur.fetchone()
        if not course_check:
            cur.close()
            conn.close()
            flash('Course not found or access denied.', 'danger')
            return redirect(url_for('lecturer_courses'))
    
    cur.execute("SELECT course_title FROM courses WHERE course_id = %s", (course_id,))
    course = cur.fetchone()
    
    cur.execute("""SELECT e.exam_id, e.title, e.description, e.duration_minutes, e.total_points, 
                          (SELECT COUNT(*) FROM exam_questions WHERE exam_id = e.exam_id) as question_count,
                          (SELECT COUNT(*) FROM exam_attempts WHERE exam_id = e.exam_id AND student_id = %s) as student_attempts,
                          (SELECT attempt_id FROM exam_attempts WHERE exam_id = e.exam_id AND student_id = %s ORDER BY start_time DESC LIMIT 1) as latest_attempt_id,
                          e.camera_required
                   FROM exams e
                   WHERE e.course_id = %s
                   ORDER BY e.created_at DESC""", (session['user_id'], session['user_id'], course_id))
    exams = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template('dlms_course_exams.html', course=course, course_id=course_id, exams=exams)

@app.route('/admin/exam/<int:exam_id>/delete', methods=['POST'])
@login_required
@role_required('administrator')
def admin_delete_exam(exam_id):
    conn = get_db()
    cur = conn.cursor()
    
    # Get exam info
    cur.execute("SELECT exam_id, title FROM exams WHERE exam_id = %s", (exam_id,))
    exam = cur.fetchone()
    
    if not exam:
        cur.close()
        conn.close()
        flash('Exam not found.', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    # Delete the exam (CASCADE will handle all related records)
    try:
        cur.execute("DELETE FROM exams WHERE exam_id = %s", (exam_id,))
        conn.commit()
        flash(f'Exam "{exam[1]}" deleted successfully.', 'success')
    except Exception as e:
        conn.rollback()
        flash('Error deleting exam.', 'danger')
    
    cur.close()
    conn.close()
    return redirect(url_for('admin_dashboard'))

# Student: Take Exam
@app.route('/exam/<int:exam_id>/take', methods=['GET', 'POST'])
@login_required
@role_required('student')
def take_exam(exam_id):
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""SELECT e.exam_id, e.course_id, e.title, e.duration_minutes, e.total_points, c.course_title, e.camera_required
                   FROM exams e
                   JOIN courses c ON e.course_id = c.course_id
                   WHERE e.exam_id = %s""", (exam_id,))
    exam = cur.fetchone()
    
    if not exam:
        cur.close()
        conn.close()
        flash('Exam not found.', 'danger')
        return redirect(url_for('student_courses'))
    
    cur.execute("""SELECT course_id FROM enrollments 
                   WHERE student_id = %s AND course_id = %s""", (session['user_id'], exam[1]))
    enrollment = cur.fetchone()
    
    if not enrollment:
        cur.close()
        conn.close()
        flash('You are not enrolled in this course.', 'danger')
        return redirect(url_for('student_courses'))
    
    if request.method == 'POST':
        cur.execute("""INSERT INTO exam_attempts (exam_id, student_id, status) 
                      VALUES (%s, %s, 'in_progress')""", (exam_id, session['user_id']))
        conn.commit()
        attempt_id = cur.lastrowid
        cur.close()
        conn.close()
        return redirect(url_for('exam_attempt', attempt_id=attempt_id))
    
    cur.close()
    conn.close()
    return render_template('dlms_take_exam.html', exam=exam)

# Student: Exam Attempt Page
@app.route('/exam-attempt/<int:attempt_id>')
@login_required
@role_required('student')
def exam_attempt(attempt_id):
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""SELECT a.attempt_id, a.exam_id, a.start_time, a.status, e.duration_minutes, e.title, e.total_points, e.camera_required
                   FROM exam_attempts a
                   JOIN exams e ON a.exam_id = e.exam_id
                   WHERE a.attempt_id = %s AND a.student_id = %s""", (attempt_id, session['user_id']))
    attempt = cur.fetchone()
    
    if not attempt:
        cur.close()
        conn.close()
        flash('Exam attempt not found.', 'danger')
        return redirect(url_for('student_courses'))
    
    if attempt[3] == 'completed':
        cur.close()
        conn.close()
        return redirect(url_for('exam_results', attempt_id=attempt_id))
    
    cur.execute("""SELECT eq.exam_question_id, eq.question_text, eq.option_a, eq.option_b, eq.option_c, eq.option_d, eq.points
                   FROM exam_questions eq
                   WHERE eq.exam_id = %s
                   ORDER BY eq.exam_question_id""", (attempt[1],))
    questions = cur.fetchall()
    
    cur.execute("""SELECT exam_question_id, student_answer FROM exam_answers 
                   WHERE attempt_id = %s""", (attempt_id,))
    answers = {row[0]: row[1] for row in cur.fetchall()}
    cur.close()
    conn.close()
    
    return render_template('dlms_exam_attempt.html', attempt=attempt, questions=questions, answers=answers, attempt_id=attempt_id)

# Student: Save Exam Answer
@app.route('/exam-attempt/<int:attempt_id>/answer', methods=['POST'])
@login_required
@role_required('student')
def save_exam_answer(attempt_id):
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""SELECT attempt_id FROM exam_attempts 
                   WHERE attempt_id = %s AND student_id = %s""", (attempt_id, session['user_id']))
    if not cur.fetchone():
        cur.close()
        conn.close()
        return {'error': 'Unauthorized'}, 403
    
    question_id = request.json.get('question_id')
    answer = request.json.get('answer')
    
    cur.execute("""SELECT answer_id FROM exam_answers 
                   WHERE attempt_id = %s AND exam_question_id = %s""", (attempt_id, question_id))
    existing = cur.fetchone()
    
    if existing:
        cur.execute("""UPDATE exam_answers SET student_answer = %s 
                      WHERE attempt_id = %s AND exam_question_id = %s""", (answer, attempt_id, question_id))
    else:
        cur.execute("""INSERT INTO exam_answers (attempt_id, exam_question_id, student_answer) 
                      VALUES (%s, %s, %s)""", (attempt_id, question_id, answer))
    
    conn.commit()
    cur.close()
    conn.close()
    
    return {'status': 'saved'}, 200

# Student: Submit Exam
@app.route('/exam-attempt/<int:attempt_id>/submit', methods=['POST'])
@login_required
@role_required('student')
def submit_exam(attempt_id):
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""SELECT a.attempt_id, a.exam_id FROM exam_attempts a
                   WHERE a.attempt_id = %s AND a.student_id = %s""", (attempt_id, session['user_id']))
    attempt = cur.fetchone()
    
    if not attempt:
        cur.close()
        conn.close()
        flash('Exam attempt not found.', 'danger')
        return redirect(url_for('student_courses'))
    
    # Calculate score
    cur.execute("""SELECT eq.exam_question_id, eq.correct_answer, eq.points, ea.student_answer
                   FROM exam_questions eq
                   LEFT JOIN exam_answers ea ON eq.exam_question_id = ea.exam_question_id AND ea.attempt_id = %s
                   WHERE eq.exam_id = %s""", (attempt_id, attempt[1]))
    questions = cur.fetchall()
    
    score = 0
    for q in questions:
        if q[2] and q[3] == q[1]:  # points, correct_answer, student_answer
            score += int(q[2])
    
    cur.execute("""UPDATE exam_attempts SET status = 'completed', score = %s, end_time = NOW() 
                   WHERE attempt_id = %s""", (score, attempt_id))
    conn.commit()
    cur.close()
    conn.close()
    
    flash('Exam submitted successfully!', 'success')
    return redirect(url_for('exam_results', attempt_id=attempt_id))

# Student: View Exam Results
@app.route('/exam-attempt/<int:attempt_id>/results')
@login_required
@role_required('student')
def exam_results(attempt_id):
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""SELECT a.attempt_id, a.exam_id, a.score, e.total_points, e.title, a.start_time, a.end_time, u.full_name
                   FROM exam_attempts a
                   JOIN exams e ON a.exam_id = e.exam_id
                   JOIN users u ON a.student_id = u.user_id
                   WHERE a.attempt_id = %s AND a.student_id = %s AND a.status = 'completed'""", 
               (attempt_id, session['user_id']))
    attempt = cur.fetchone()
    
    if not attempt:
        cur.close()
        conn.close()
        flash('Exam results not found.', 'danger')
        return redirect(url_for('student_courses'))
    
    cur.execute("""SELECT eq.exam_question_id, eq.question_text, eq.correct_answer, eq.option_a, eq.option_b, eq.option_c, eq.option_d, eq.points, ea.student_answer
                   FROM exam_questions eq
                   LEFT JOIN exam_answers ea ON eq.exam_question_id = ea.exam_question_id AND ea.attempt_id = %s
                   WHERE eq.exam_id = %s
                   ORDER BY eq.exam_question_id""", (attempt_id, attempt[1]))
    questions = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template('dlms_exam_results.html', attempt=attempt, questions=questions)

# Lecturer: Monitor Exams
@app.route('/lecturer/exam/<int:exam_id>/monitor')
@login_required
@role_required('lecturer')
def monitor_exams(exam_id):
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""SELECT e.exam_id, e.title, c.course_id, c.course_title
                   FROM exams e
                   JOIN courses c ON e.course_id = c.course_id
                   WHERE e.exam_id = %s AND c.lecturer_id = %s""", (exam_id, session['user_id']))
    exam = cur.fetchone()
    
    if not exam:
        cur.close()
        conn.close()
        flash('Exam not found or access denied.', 'danger')
        return redirect(url_for('lecturer_courses'))
    
    cur.execute("""SELECT a.attempt_id, a.student_id, u.full_name, a.status, a.start_time, a.score, e.total_points
                   FROM exam_attempts a
                   JOIN users u ON a.student_id = u.user_id
                   JOIN exams e ON a.exam_id = e.exam_id
                   WHERE a.exam_id = %s
                   ORDER BY a.start_time DESC""", (exam_id,))
    attempts = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template('dlms_monitor_exams.html', exam=exam, attempts=attempts)

if __name__ == '__main__':
    app.run(debug=True)
