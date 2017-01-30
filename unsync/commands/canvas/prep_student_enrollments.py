"""Prepare student enrollments"""
import click
import petl
from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync


@unsync.command()
@click.option('--ptf9-enrollments', required=True, help='Table where student ptf9 enrollment data is stored.')
@click.option('--ptf9-students', required=True, help='Table where student ptf9 data is stored.')
@click.option('--destination', '-d', required=True, help='Table to store modified enrollment data in.')
@pass_data
def prep_student_enrollments(data, ptf9_enrollments, ptf9_students, destination):
    enrollments = data.get(ptf9_enrollments)
    students = data.get(ptf9_students)

    enrollments = enrollments.cut('ClassCode', 'StudentID').rename('ClassCode', 'course_id')
    students = students.cut('Code', 'StudentID').rename('Code', 'user_id')
    enrollments = petl.leftjoin(enrollments, students, lkey='StudentID', rkey='StudentID')
    enrollments = (enrollments
                   .cut('user_id', 'course_id')
                   .addfield('role', 'student')
                   .convert('user_id', lambda v: 'c{}'.format(v))
                   .select(lambda rec: rec.course_id is not None and rec.user_id is not None))

    data.set(destination, enrollments)

command = prep_student_enrollments
