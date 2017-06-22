"""Timetabler PTF9 import functions."""
import unsync
import petl


@unsync.command()
@unsync.option('--input-file', '-i', type=unsync.Path(exists=True, dir_okay=False, readable=True, resolve_path=True), help='Timetabler PTF9 file to extract data from.', required=True)
@unsync.option('--destination', '-d', required=True, help='The destination table that these courses will be stored in.')
def period_import(data, input_file, destination):
    """Import courses from a Timetabler PTF9 export file."""
    new_periods = petl.fromxml(input_file, '{http://www.timetabling.com.au/TDV9}Periods/{http://www.timetabling.com.au/TDV9}Period', {
                             'PeriodID': '{http://www.timetabling.com.au/TDV9}PeriodID',
                             'DayID': '{http://www.timetabling.com.au/TDV9}DayID',
                             'Code': '{http://www.timetabling.com.au/TDV9}Code',
                             'Name': '{http://www.timetabling.com.au/TDV9}Name',
                             'Doubles': '{http://www.timetabling.com.au/TDV9}Doubles',
                             'Triples': '{http://www.timetabling.com.au/TDV9}Triples',
                             'Quadruples': '{http://www.timetabling.com.au/TDV9}Quadruples',
                             'SiteMove': '{http://www.timetabling.com.au/TDV9}SiteMove',
                             'Load': '{http://www.timetabling.com.au/TDV9}Load',
                             'Index': '{http://www.timetabling.com.au/TDV9}Index',
                             'Number': '{http://www.timetabling.com.au/TDV9}Number',
                             'StartTime': '{http://www.timetabling.com.au/TDV9}StartTime',
                             'FinishTime': '{http://www.timetabling.com.au/TDV9}FinishTime',
                             })
    data.set(destination, new_periods)

command = period_import

# default=[('Code', 'course_id'), ('Name', 'long_name'), ('Code', 'short_name'), ('ClassID', 'ptf9_id')]
