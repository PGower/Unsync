"""Timetabler DOF9 import functions."""
import click
import petl

from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync

import json
import lxml
from lxml import objectify
import random


class objectJSONEncoder(json.JSONEncoder):
    """A specialized JSON encoder that can handle simple lxml objectify types.
        >>> from lxml import objectify
        >>> obj = objectify.fromstring("<Book><price>1.50</price><author>W. Shakespeare</author></Book>")       
        >>> objectJSONEncoder().encode(obj)
        '{"price": 1.5, "author": "W. Shakespeare"}'
      Found @ http://stackoverflow.com/questions/471946/how-to-convert-xml-to-json-in-python
    """

    def default(self, o):
        if isinstance(o, lxml.objectify.IntElement):
            return int(o)
        if isinstance(o, lxml.objectify.NumberElement) or isinstance(o, lxml.objectify.FloatElement):
            return float(o)
        if isinstance(o, lxml.objectify.ObjectifiedDataElement):
            return str(o)
        if hasattr(o, '__dict__'):
            #For objects with a __dict__, return the encoding of the __dict__
            return o.__dict__
        return json.JSONEncoder.default(self, o)


@unsync.command()
@click.option('--input-file', '-i', type=click.Path(exists=True, dir_okay=False, readable=True, resolve_path=True), help='Timetabler DOF9 file to extract data from.', required=True)
@click.option('--destination', '-d', required=True, help='The destination table that these courses will be stored in.')
@pass_data
def dof9_import_dates(data, input_file, destination):
    """Import the dates and definitions for the replacements that need to happen."""
    all_data = petl.wrap([[]])

    namespaces = {'x': 'http://www.timetabling.com.au/DOV9'}

    tree = lxml.etree.parse(open(input_file))  # Read Everything
    date_subtrees = tree.xpath('/x:DailyOrganiserData/x:Dates/x:Date', namespaces={'x': 'http://www.timetabling.com.au/DOV9'})
    for date_subtree in date_subtrees:
        cf_date = date_subtree.findtext('x:Date', namespaces=namespaces),
        cf_datestring = date_subtree.findtext('x:DateString', namespaces=namespaces),
        cf_day = date_subtree.findtext('x:Day', namespaces=namespaces)

        add_common_fields = lambda i, cf_date=cf_date, cf_datestring=cf_datestring, cf_day=cf_day: i.addfield('Date', cf_date).addfield('DateString', cf_datestring).addfield('Day', cf_day)  # noqa

        subtree_data = petl.MemorySource(lxml.etree.tostring(date_subtree))

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




        
        import pdb;pdb.set_trace()



    

    dof9_dates = petl.fromxml(input_file, '{http://www.timetabling.com.au/DOV9}Dates/{http://www.timetabling.com.au/DOV9}Date', {
                             'Date': '{http://www.timetabling.com.au/DOV9}Date',
                             'DateString': '{http://www.timetabling.com.au/DOV9}DateString',
                             'Day': '{http://www.timetabling.com.au/DOV9}Day',
                             'TeacherAbsenceID': '{http://www.timetabling.com.au/DOV9}TeacherAbsences/{http://www.timetabling.com.au/DOV9}TeacherAbsence/{http://www.timetabling.com.au/DOV9}TeacherAbsenceID',
                             'PeriodReplacements': '{http://www.timetabling.com.au/DOV9}PeriodReplacements',
                             'YardDutyReplacements': '{http://www.timetabling.com.au/DOV9}YardDutyReplacements',
                             'RoomEdits': '{http://www.timetabling.com.au/DOV9}RoomEdits',
                             'EmergencyTeacherAvailables': '{http://www.timetabling.com.au/DOV9}EmergencyTeacherAvailables',
                             'EmergencyTeacherYardDutyAvailables': '{http://www.timetabling.com.au/DOV9}EmergencyTeacherYardDutyAvailables',
                             'RoomReplacements': '{http://www.timetabling.com.au/DOV9}RoomReplacements',
                             'LessonCancellations': '{http://www.timetabling.com.au/DOV9}LessonCancellations',
                             'YardDutyCancellations': '{http://www.timetabling.com.au/DOV9}YardDutyCancellations',
                             'LoadAdjustments': '{http://www.timetabling.com.au/DOV9}LoadAdjustments',
                             'RoomAvailables': '{http://www.timetabling.com.au/DOV9}RoomAvailables',
                             'AttendanceChanges': '{http://www.timetabling.com.au/DOV9}AttendanceChanges'
                             })
    data.set(destination, dof9_dates)

command = dof9_import_dates
