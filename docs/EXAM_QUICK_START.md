# 🚀 Timed Exams System - Quick Start Guide

## What's New?

Your Distance Learn platform now has a complete **timed exam system with camera monitoring**. Students take multiple-choice exams with a countdown timer, and lecturers can monitor attempts in real-time.

---

## ⚡ Quick Setup

### 1. Update Database

Run this SQL to add the exam tables:

```bash
mysql -u root -p dlms_db < dlms_database.sql

```sql
**Note**: Update the password in `dlms_app.py` line 15 if your MySQL root password is different.

### 2. Start Flask App
```bash
cd "c:\Users\OPARAH\Documents\Claude 1"
python dlms_app.py
```text
App will be available at: `http://localhost:5000`

### 3. Login Credentials (for testing)

```text
Lecturer: lecturer@dlms.com / password123
Student:  student@dlms.com / password123
Admin:    admin@dlms.com / password123
```

---

## 📋 How to Use

### For Lecturers: Creating an Exam

1. **Login** as lecturer
2. **Go to**: My Courses → Select a course → **Exams** button
3. **Click**: "+ Create Exam"
4. **Fill in**:
   - Exam title (e.g., "Final Exam")
   - Description (optional)
   - Duration in minutes (e.g., 60)
   - Total points available
5. **Submit** - Exam created!
6. **Click**: "Manage Questions" button
7. **Add Questions**:
   - Type your question
   - Enter 4 options (A, B, C, D)
   - Select the correct answer from dropdown
   - Enter points for this question
   - Click "Add Question"
8. **Repeat** for all questions
9. **Click**: Back to course to see your exam listed

### For Lecturers: Monitoring Exams

1. **Go to**: My Courses → Select course → Exams
2. **Find** your exam
3. **Click**: "Monitor" button
4. **See**:
   - All student attempts
   - Status (in progress / completed)
   - Scores (for completed)
   - Camera status (✓ Active / ✗ Off)
5. **View Results** by clicking exam name for completed attempts

---

### For Students: Taking an Exam

1. **Login** as student
2. **Go to**: My Courses → Select course → **Exams** button
3. **See** all exams in this course
4. **Click**: "Take Exam" button
5. **Read** the exam requirements page
6. **Click**: Start Exam
7. **IMPORTANT**: Click "Enable Camera" 🎥
   - Browser will ask for camera permission
   - Grant permission
   - Camera feed will appear
8. **Answer** the questions:
   - Click the radio button for your answer
   - Answers auto-save
9. **Watch** the timer countdown
10. **Click** "Submit Exam" when done
11. **See** your score immediately
12. **Review** your answers to see correct vs your choices

---

## 🎥 Camera Feature

### Why Camera?

- Proctoring: Ensures exam integrity
- Required: Exam cannot be submitted without camera enabled

### How It Works

1. Student clicks "Enable Camera"
2. Browser requests permission (user clicks "Allow")
3. Camera feed displays in video element
4. Button changes to "✓ Camera Active"
5. Submit button becomes enabled
6. Student takes exam with camera recording

### If Camera Not Available

- Browser shows error message
- Submit button stays disabled
- Student cannot complete exam

**Note**: Camera feed is displayed to student only. Server-side recording can be added as an enhancement.

---

## ⏱️ Timer System

### How Timer Works

- **Display**: Countdown in MM:SS format at top of exam
- **Behavior**: Updates every 1 second
- **Auto-Submit**: When timer hits 0:00, exam auto-submits automatically
- **Warning**: Timer text turns red at 60 seconds remaining
- **Prevention**: Students cannot extend time or pause

### Timer Example

```text
Duration: 60 minutes
Timer displays: 59:47, 59:46, 59:45, ... 0:02, 0:01 → AUTO-SUBMIT
```

---

## 🎯 Auto-Grading System

### How Scoring Works

1. Each question has a **correct_answer** (A/B/C/D)
2. Each question has **points** value
3. **On submission**:
   - System compares student's answer to correct_answer
   - If match → Award points
   - If no match → Award 0 points
4. **Total Score** = Sum of all points earned

### Example

```text
Question 1: Correct answer is B, student answered B → +1 point
Question 2: Correct answer is A, student answered C → 0 points
Question 3: Correct answer is D, student answered D → 2 points
Total: 3 points out of 5
```

---

## 📊 Results Page

Students see:

- ✅ Final score and percentage
- ✅ Question-by-question breakdown:
  - Their answer (highlighted)
  - Correct answer
  - Green border = correct
  - Red border = incorrect
- ✅ Time submitted
- ✅ Back to dashboard button

---

## 🔧 Configuration

### Exam Settings

- **Duration**: Set per exam (minutes)
- **Total Points**: Set per exam
- **Question Points**: Set per question
- **Auto-Grade**: Automatic, instant feedback

### Database

- Tables: exams, exam_questions, exam_attempts, exam_answers
- Auto indexes on course_id, student_id for performance

### Styling

- Uses Distance Learn color scheme (dark slate, sky blue, emerald)
- Responsive design (works on desktop, tablet, mobile)
- Professional gradient backgrounds

---

## 🧪 Testing Checklist

### Test 1: Create Exam

- [ ] Lecturer can create exam
- [ ] Can add questions with A/B/C/D options
- [ ] Can set points and duration
- [ ] Exam appears in course

### Test 2: Take Exam

- [ ] Student sees exam in course
- [ ] Can click "Take Exam"
- [ ] Questions load properly
- [ ] Can enable camera without errors

### Test 3: Timer & Submission

- [ ] Timer counts down from duration
- [ ] Answers save automatically
- [ ] Submit button works
- [ ] Redirects to results

### Test 4: Grading

- [ ] Score displayed correctly
- [ ] Percentage calculated right
- [ ] Answer review shows correct answers
- [ ] Points match question values

### Test 5: Monitoring

- [ ] Lecturer sees exam attempts in monitor
- [ ] Status shows correctly
- [ ] Score displays for completed exams
- [ ] Can view results from monitor

---

## 📁 File Structure

```text
   Distance Learn/
   ├── dlms_app.py                      ← Main Flask app (contains exam routes)
   ├── dlms_database.sql                ← Database schema (exam tables included)
   ├── dlms_requirements.txt
   ├── static/
   │   └── css/
   │       └── dlms_css.css             ← Professional styling
   └── templates/
      ├── dlms_exam_attempt.html       ← ⭐ MAIN EXAM PAGE (with timer & camera)
      ├── dlms_exam_results.html       ← Results & answer review
      ├── dlms_monitor_exams.html      ← Lecturer dashboard
      ├── dlms_take_exam.html          ← Pre-exam confirmation
      ├── dlms_course_exams.html       ← Exam listing page
      ├── dlms_add_exam_questions.html ← Question builder
      ├── dlms_create_exam.html        ← Exam creation form
      ├── dlms_student_courses.html    ← Updated with Exams button
      ├── dlms_lecturer_courses.html   ← Updated with Exams button
      └── ... (other templates)
```

---

## 🎓 Features Summary

| Feature | Status | Details |
|---------|--------|---------|

| Exam Creation | ✅ | Lecturers can create exams |
| Question Builder | ✅ | Add multiple-choice (A/B/C/D) questions |
| Timer | ✅ | Countdown with auto-submit at 0 |
| Camera | ✅ | WebRTC integration, required for submission |
| Auto-Grading | ✅ | Instant scoring on submit |
| Results Page | ✅ | Answer review with correct vs student answers |
| Monitoring | ✅ | Real-time lecturer dashboard |
| Integration | ✅ | "Exams" button on course pages |

---

## 🚨 Important Notes

1. **Camera Required**: Students MUST enable camera to submit exam
2. **No Pause**: Timer cannot be paused, exam auto-submits when time ends
3. **Auto-Save**: Answers are auto-saved, no manual save needed
4. **No Editing**: After submission, answers cannot be changed
5. **Instant Grade**: Score appears immediately on results page
6. **MySQL**: Make sure MySQL is running before starting Flask app

---

## 🐛 Troubleshooting

### Camera Not Working?

- Check browser permissions
- Make sure webcam is not in use by another app
- Try a different browser
- Camera support: Chrome, Firefox, Safari (not IE)

### Timer Not Showing?

- Check browser JavaScript console (F12)
- Refresh page
- Check that attempt_id is being passed correctly

### Exam Not Saving Answers?

- Check network connection
- Look at browser console for errors
- Verify Flask app is running
- Check that database connection is working

### Submit Button Disabled?

- This is expected until camera is enabled
- Click "Enable Camera" button first
- Grant browser permission when prompted

---

## 📞 Support

If you encounter issues:

1. **Check Console**: Press F12 → Console tab for JavaScript errors
2. **Check Terminal**: Look at Flask app output for errors
3. **Check Database**: Verify MySQL is running and connected
4. **Check Files**: Verify all template files exist in templates/ folder

---

## 🎉 You're All Set

Your timed exam system is ready to use. Start by:

1. ✅ Run Flask app: `python dlms_app.py`
2. ✅ Login as lecturer
3. ✅ Create your first exam
4. ✅ Add questions
5. ✅ Have a student take it
6. ✅ View results

**Happy testing!** 🚀
