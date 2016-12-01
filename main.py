import click

from plugins.ptf9 import ptf9_course_import, ptf9_student_import, ptf9_staff_import, ptf9_student_enrollment_import, ptf9_staff_enrollment_import
from plugins.csv import csv_import, csv_export, full_csv_export
from plugins.print_to_screen import print_to_screen
from plugins.ldap import ldap_import

from plugins.common import pass_data


@click.group(chain=True)
@pass_data
def cli(data):
    pass

cli.add_command(ptf9_course_import)
cli.add_command(ptf9_student_import)
cli.add_command(ptf9_staff_import)
cli.add_command(ptf9_student_enrollment_import)
cli.add_command(ptf9_staff_enrollment_import)
cli.add_command(csv_import)
cli.add_command(csv_export)
cli.add_command(full_csv_export)
cli.add_command(ldap_import)
cli.add_command(print_to_screen)


if __name__ == '__main__':
    cli()
