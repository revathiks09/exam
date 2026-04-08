# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Courses(models.Model):
    dept = models.ForeignKey('Departments', models.DO_NOTHING, blank=True, null=True)
    course_name = models.CharField(max_length=150, blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'courses'


class Departments(models.Model):
    dept_name = models.CharField(max_length=100, blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'departments'


class ExamSchedule(models.Model):
    subject = models.ForeignKey('Subjects', models.DO_NOTHING, blank=True, null=True)
    exam_date = models.DateField(blank=True, null=True)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'exam_schedule'


class HallTickets(models.Model):
    student = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    semester = models.ForeignKey('Semesters', models.DO_NOTHING, blank=True, null=True)
    issued_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'hall_tickets'


class LoginSessions(models.Model):
    user = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    login_time = models.DateTimeField()
    logout_time = models.DateTimeField(blank=True, null=True)
    ip_address = models.CharField(max_length=50, blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'login_sessions'


class Marks(models.Model):
    student = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    subject = models.ForeignKey('Subjects', models.DO_NOTHING, blank=True, null=True)
    evaluator = models.ForeignKey('Users', models.DO_NOTHING, related_name='marks_evaluator_set', blank=True, null=True)
    internal_marks = models.FloatField(blank=True, null=True)
    external_marks = models.FloatField(blank=True, null=True)
    marks_obtained = models.FloatField(blank=True, null=True)
    moderated_marks = models.FloatField(blank=True, null=True)
    status = models.CharField(max_length=9, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'marks'


class QuestionPapers(models.Model):
    subject = models.ForeignKey('Subjects', models.DO_NOTHING, blank=True, null=True)
    faculty = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    semester = models.ForeignKey('Semesters', models.DO_NOTHING, blank=True, null=True)
    paper_title = models.CharField(max_length=200, blank=True, null=True)
    file_path = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=9, blank=True, null=True)
    submitted_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'question_papers'


class ResultAnalytics(models.Model):
    subject = models.ForeignKey('Subjects', models.DO_NOTHING, blank=True, null=True)
    pass_percentage = models.FloatField(blank=True, null=True)
    average_marks = models.FloatField(blank=True, null=True)
    grade_distribution = models.TextField(blank=True, null=True)
    generated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'result_analytics'


class Results(models.Model):
    student = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    semester = models.ForeignKey('Semesters', models.DO_NOTHING, blank=True, null=True)
    total_marks = models.FloatField(blank=True, null=True)
    grade = models.CharField(max_length=5, blank=True, null=True)
    result_status = models.CharField(max_length=4, blank=True, null=True)
    published_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'results'


class RevaluationRequests(models.Model):
    student = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    subject = models.ForeignKey('Subjects', models.DO_NOTHING, blank=True, null=True)
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=11, blank=True, null=True)
    requested_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'revaluation_requests'


class SeatingArrangement(models.Model):
    student = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    subject = models.ForeignKey('Subjects', models.DO_NOTHING, blank=True, null=True)
    hall_no = models.CharField(max_length=50, blank=True, null=True)
    seat_no = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'seating_arrangement'


class Semesters(models.Model):
    course = models.ForeignKey(Courses, models.DO_NOTHING, blank=True, null=True)
    semester_no = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'semesters'


class Subjects(models.Model):
    semester = models.ForeignKey(Semesters, models.DO_NOTHING, blank=True, null=True)
    subject_name = models.CharField(max_length=150, blank=True, null=True)
    faculty = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'subjects'


class Students(models.Model):
    user = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    regno = models.CharField(max_length=50, blank=True, null=True)
    dept = models.ForeignKey(Departments, models.DO_NOTHING, blank=True, null=True)
    course = models.ForeignKey(Courses, models.DO_NOTHING, blank=True, null=True)
    semester = models.ForeignKey(Semesters, models.DO_NOTHING, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'students'


class SystemLogs(models.Model):
    user = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    action = models.TextField(blank=True, null=True)
    log_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'system_logs'


class Users(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(unique=True, max_length=150, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=15, blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'users'
