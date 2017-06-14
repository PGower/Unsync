"""Prepare staff enrollments"""
import click
import petl
from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync


@unsync.command()
@click.option('--ptf9-enrollments', required=True, help='Table where staff ptf9 enrollment data is stored.')
@click.option('--ptf9-staff', required=True, help='Table where staff ptf9 data is stored.')
@click.option('--ptf9-courses', required=True, help='Table where ptf9 courses data is stored. This expects raw course data, not processed.')
@click.option('--destination', '-d', required=True, help='Table to store modified enrollment data in.')
@click.option('--teacher-id-map', required=True, help='Table that contains mappings from Timetabler IDs to canvas user IDs. Expects two columns tt_id and user_id.')
@pass_data
def prep_staff_enrollments(data, ptf9_enrollments, ptf9_staff, ptf9_courses, destination, teacher_id_map):
    enrollments = data.get(ptf9_enrollments)
    staff = data.get(ptf9_staff)
    courses = data.get(ptf9_courses)
    id_map = data.get(teacher_id_map)

    enrollments = enrollments.cut('ClassID', 'TeacherID').distinct()
    courses = courses.cut('Code', 'ClassID').rename('Code', 'ClassCode')
    staff = staff.cut('Code', 'TeacherID').rename('Code', 'TeacherCode')

    enrollments = petl.leftjoin(enrollments, courses, key='ClassID')
    enrollments = petl.leftjoin(enrollments, staff, key='TeacherID')
    # Just ignore any data without a TeacherID or TeacherCode, it wont work and we wont miss anything by ignoring it.
    enrollments = petl.select(enrollments, lambda rec: rec['TeacherID'] is not None and rec['TeacherCode'] is not None)
    enrollments = petl.lookupjoin(enrollments, id_map, lkey='TeacherCode', rkey='tt_id')
    enrollments = (enrollments
                   .addfield('role', 'teacher')
                   .rename('ClassCode', 'course_id')
                   .cut('course_id', 'user_id', 'role')
                   .select(lambda rec: rec.course_id is not None and rec.user_id is not None))

    data.set(destination, enrollments)

command = prep_staff_enrollments
