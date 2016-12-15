"""Common junk for CanvasUnsync. Will need to be tied at some stage."""
# from __future__ import absolute_import
import click
import petl
from lib.canvas_api import CanvasAPIError
import arrow


# def apply_attr_map(t, attr_map):
#     for a_map in attr_map:
#         src = a_map[0]
#         dest = a_map[1]
#         t = t.addfield(dest, lambda rec, src=src: rec[src])
#     return t


# def apply_attr_fill(t, attr_fill):
#     for a_fill_map in attr_fill:
#         name = a_fill_map[0]
#         value = a_fill_map[1]
#         t = t.addfield(name, value)
#     return t


# def generic_import_actions(t, attr_map, attr_fill, delete_import_fields):
#     t = apply_attr_map(t, attr_map)
#     t = apply_attr_fill(t, attr_fill)
#     if delete_import_fields is True:
#         t = t.cut(*[a[1] for a in attr_map] + [a[0] for a in attr_fill])
#     return t


# def validate_source(ctx, param, value):
#     # how do I get the UnsyncData object from the context?
#     pass


def extract_api_data(response, header, empty_value=None):
    if response['response'].status_code == 200:
        t = [header]
        for i in response['data']:
            t.append([i.get(j, empty_value) for j in header])
        return petl.wrap(t)
    else:
        click.secho('Looks like something went wrong: {} {}.'.format(response['response'].status_code, response['response'].reason), err=True, fg='red')
        raise CanvasAPIError(response['response'])


def select_term_id(target_date, kind, terms, date_format='YYYY-MM-DDTHH:mm:ss'):
    """Return the sis_term_id from the passed terms table where the kind matches the term and the target_date falls within the target date."""
    if issubclass(type(target_date), basestring):
        target_date = arrow.get(target_date, date_format)

    term_lookup = terms.cut('term_id', 'start', 'end')
    term_lookup = term_lookup.listoftuples()[1:]
    term_lookup = dict([(i[0], {'start': arrow.get(i[1], date_format), 'end': arrow.get(i[2], date_format)}) for i in term_lookup])

    for term_id, span in term_lookup.items():
        if kind.lower() in term_id.lower():
            if span['start'] <= target_date and target_date <= span['end']:
                return term_id
    return None
