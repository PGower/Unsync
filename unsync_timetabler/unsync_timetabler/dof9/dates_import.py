"""Timetabler DOF9 import functions."""
import unsync
import petl

import lxml


@unsync.command()
@unsync.option('--input-file', '-i', type=unsync.Path(exists=True, dir_okay=False, readable=True, resolve_path=True), help='Timetabler DOF9 file to extract data from.', required=True)
@unsync.option('--teacher-absences-destination', help="The destination table that all teacher_absences data will be saved to.")
@unsync.option('--period-replacements-destination', help="The destination table that all period_replacements data will be saved to.")
@unsync.option('--emergency-teacher-availables-destination', help="The destination table that all emergency_teacher_availables data will be saved to.")
@unsync.option('--emergency-teacher-yard-duty-available-destination', help="The destination table that all emergency_teacher_yard_duty_available data will be saved to.")
@unsync.option('--yard-duty-replacements-destination', help="The destination table that all yard_duty_replacements data will be saved to.")
@unsync.option('--room-replacements-destination', help="The destination table that all room_replacements data will be saved to.")
@unsync.option('--room-edits-destination', help="The destination table that all room_edits data will be saved to.")
@unsync.option('--lesson-cancellations-destination', help="The destination table that all lesson_cancellations data will be saved to.")
@unsync.option('--yard-duty-cancellations-destination', help="The destination table that all yard_duty_cancellations data will be saved to.")
@unsync.option('--load-adjustments-destination', help="The destination table that all load_adjustments data will be saved to.")
@unsync.option('--room-availables-destination', help="The destination table that all room_availables data will be saved to.")
@unsync.option('--attendence-changes-destination', help="The destination table that all attendence_changes data will be saved to.")
def dof9_import_dates(data, input_file,
                      teacher_absences_destination,
                      period_replacements_destination,
                      emergency_teacher_availables_destination,
                      emergency_teacher_yard_duty_available_destination,
                      yard_duty_replacements_destination,
                      room_replacements_destination,
                      room_edits_destination,
                      lesson_cancellations_destination,
                      yard_duty_cancellations_destination,
                      load_adjustments_destination,
                      room_availables_destination,
                      attendence_changes_destination):
    """Import the dates and definitions for the replacements that need to happen."""
    namespaces = {'x': 'http://www.timetabling.com.au/DOV9'}

    all_teacher_absences = petl.wrap([[]])
    all_period_replacements = petl.wrap([[]])
    all_emergency_teacher_availables = petl.wrap([[]])
    all_emergency_teacher_yard_duty_available = petl.wrap([[]])
    all_yard_duty_replacements = petl.wrap([[]])
    all_room_replacements = petl.wrap([[]])
    all_room_edits = petl.wrap([[]])
    all_lesson_cancellations = petl.wrap([[]])
    all_yard_duty_cancellations = petl.wrap([[]])
    all_load_adjustments = petl.wrap([[]])
    all_room_availables = petl.wrap([[]])
    all_attendence_changes = petl.wrap([[]])

    tree = lxml.etree.parse(open(input_file))  # Read Everything
    date_subtrees = tree.xpath('/x:DailyOrganiserData/x:Dates/x:Date', namespaces={'x': 'http://www.timetabling.com.au/DOV9'})
    for date_subtree in date_subtrees:
        cf_date = date_subtree.findtext('x:Date', namespaces=namespaces)
        cf_datestring = date_subtree.findtext('x:DateString', namespaces=namespaces)
        cf_day = date_subtree.findtext('x:Day', namespaces=namespaces)

        add_common_fields = lambda i, cf_date=cf_date, cf_datestring=cf_datestring, cf_day=cf_day: i.addfield('Date', cf_date).addfield('DateString', cf_datestring).addfield('Day', cf_day)  # noqa

        subtree_data = petl.MemorySource(lxml.etree.tostring(date_subtree))

        if teacher_absences_destination is not None:
            teacher_absences = petl.fromxml(subtree_data, '{http://www.timetabling.com.au/DOV9}TeacherAbsences/{http://www.timetabling.com.au/DOV9}TeacherAbsence',
                                            {
                                                'TeacherAbsenceID': '{http://www.timetabling.com.au/DOV9}TeacherAbsenceID',
                                                'TeacherCode': '{http://www.timetabling.com.au/DOV9}TeacherCode',
                                                'SessionNo': '{http://www.timetabling.com.au/DOV9}SessionNo',
                                                'Precedes': '{http://www.timetabling.com.au/DOV9}Precedes',
                                                'IsYardDuty': '{http://www.timetabling.com.au/DOV9}IsYardDuty',
                                                'PeriodCode': '{http://www.timetabling.com.au/DOV9}PeriodCode',
                                                'TeacherAbsenceReasonID': '{http://www.timetabling.com.au/DOV9}TeacherAbsenceID',
                                                'Counted': '{http://www.timetabling.com.au/DOV9}Counted',
                                                'Load': '{http://www.timetabling.com.au/DOV9}Load',
                                                'ArchiveTimetableReference': '{http://www.timetabling.com.au/DOV9}ArchiveTimetableReference',
                                                'ArchiveErrorType': '{http://www.timetabling.com.au/DOV9}ArchiveErrorType'
                                            })
            teacher_absences = add_common_fields(teacher_absences)
            all_teacher_absences = all_teacher_absences.cat(teacher_absences)

        if period_replacements_destination is not None:
            period_replacements = petl.fromxml(subtree_data, '{http://www.timetabling.com.au/DOV9}PeriodReplacements/{http://www.timetabling.com.au/DOV9}PeriodReplacement',
                                           {
                                            'PeriodReplacementID': '{http://www.timetabling.com.au/DOV9}PeriodReplacementID',
                                            'RollClassCode': '{http://www.timetabling.com.au/DOV9}RollClassCode',
                                            'ClassCode': '{http://www.timetabling.com.au/DOV9}ClassCode',
                                            'ClassGroupRowID': '{http://www.timetabling.com.au/DOV9}ClassGroupRowID',
                                            'PeriodCode': '{http://www.timetabling.com.au/DOV9}PeriodCode',
                                            'PeriodNo': '{http://www.timetabling.com.au/DOV9}PeriodNo',
                                            'ReplacementTeacherCode': '{http://www.timetabling.com.au/DOV9}ReplacementTeacherCode',
                                            'Load': '{http://www.timetabling.com.au/DOV9}Load',
                                            'Count': '{http://www.timetabling.com.au/DOV9}Count',
                                            'InLieu': '{http://www.timetabling.com.au/DOV9}InLieu',
                                            'Notes': '{http://www.timetabling.com.au/DOV9}Notes',
                                            'Index': '{http://www.timetabling.com.au/DOV9}Index',
                                            'NotRequired': '{http://www.timetabling.com.au/DOV9}NotRequired',
                                            'DuplicateReplacementID': '{http://www.timetabling.com.au/DOV9}DuplicateReplacementID',
                                            'ReferenceTeacherCode': '{http://www.timetabling.com.au/DOV9}ReferenceTeacherCode',
                                            'IsComposites': '{http://www.timetabling.com.au/DOV9}IsComposites',
                                            'ArchiveTimetableReference': '{http://www.timetabling.com.au/DOV9}ArchiveTimetableReference',
                                            'ArchiveErrorType': '{http://www.timetabling.com.au/DOV9}ArchiveErrorType'
                                           })
            period_replacements = add_common_fields(period_replacements)
            all_period_replacements = all_period_replacements.cat(period_replacements)

        if yard_duty_replacements_destination is not None:
            yard_duty_replacements = petl.fromxml(subtree_data, '{http://www.timetabling.com.au/DOV9}YardDutyReplacements/{http://www.timetabling.com.au/DOV9}YardDutyReplacement',
                                                  {
                                                    'YardDutyReplacementID': '{http://www.timetabling.com.au/DOV9}YardDutyReplacementID',
                                                    'YardDutyCode': '{http://www.timetabling.com.au/DOV9}YardDutyCode',
                                                    'PeriodCode': '{http://www.timetabling.com.au/DOV9}PeriodCode',
                                                    'PeriodNo': '{http://www.timetabling.com.au/DOV9}PeriodNo',
                                                    'Precedes': '{http://www.timetabling.com.au/DOV9}Precedes',
                                                    'SessionNo': '{http://www.timetabling.com.au/DOV9}SessionNo',
                                                    'ReplacementTeacherCode': '{http://www.timetabling.com.au/DOV9}ReplacementTeacherCode',
                                                    'Load': '{http://www.timetabling.com.au/DOV9}Load',
                                                    'Count': '{http://www.timetabling.com.au/DOV9}Count',
                                                    'InLieu': '{http://www.timetabling.com.au/DOV9}InLieu',
                                                    'Notes': '{http://www.timetabling.com.au/DOV9}Notes',
                                                    'Index': '{http://www.timetabling.com.au/DOV9}Index',
                                                    'NotRequired': '{http://www.timetabling.com.au/DOV9}NotRequired',
                                                    'ActivityCode': '{http://www.timetabling.com.au/DOV9}ActivityCode',
                                                    'ReferenceTeacherCode': '{http://www.timetabling.com.au/DOV9}ReferenceTeacherCode',
                                                    'DuplicateReplacementID': '{http://www.timetabling.com.au/DOV9}DuplicateReplacementID',
                                                    'ArchiveTimetableReference': '{http://www.timetabling.com.au/DOV9}ArchiveTimetableReference',
                                                    'ArchiveErrorType': '{http://www.timetabling.com.au/DOV9}ArchiveErrorType'
                                                  })
            yard_duty_replacements = add_common_fields(yard_duty_replacements)
            all_yard_duty_replacements = all_yard_duty_replacements.cat(yard_duty_replacements)

        if room_edits_destination is not None:
            room_edits = petl.fromxml(subtree_data, '{http://www.timetabling.com.au/DOV9}RoomEdits/{http://www.timetabling.com.au/DOV9}RoomEdit',
                                      {
                                        'ClassCode': '{http://www.timetabling.com.au/DOV9}ClassCode',
                                        'ClassGroupRowID': '{http://www.timetabling.com.au/DOV9}ClassGroupRowID',
                                        'RollClassCode': '{http://www.timetabling.com.au/DOV9}RollClassCode',
                                        'PeriodCode': '{http://www.timetabling.com.au/DOV9}PeriodCode',
                                        'ReplacementRoomCode': '{http://www.timetabling.com.au/DOV9}ReplacementRoomCode',
                                        'ArchiveTimetableReference': '{http://www.timetabling.com.au/DOV9}ArchiveTimetableReference',
                                        'ArchiveErrorType': '{http://www.timetabling.com.au/DOV9}ArchiveErrorType'

                                      })
            room_edits = add_common_fields(room_edits)
            all_room_edits = all_room_edits.cat(room_edits)

    if teacher_absences_destination is not None:
        data.set(teacher_absences_destination, all_teacher_absences)
    if period_replacements_destination is not None:
        data.set(period_replacements_destination, all_period_replacements)
    if yard_duty_replacements_destination is not None:
        data.set(yard_duty_replacements_destination, all_yard_duty_replacements)
    if room_edits_destination is not None:
        data.set(room_edits_destination, all_room_edits)

dof9_import_dates.display_name = 'import_dates'
