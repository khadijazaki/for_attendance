# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

import frappe, os, copy, json, re
from frappe import _

from frappe.modules import get_doc_path
from frappe.utils import cint, strip_html
from six import string_types
import datetime

no_cache = 1
no_sitemap = 1

def get_context(context):
    doctype = "Attendance"
    context.update({
        "doctype": doctype,
        })
    return get_attendance()

@frappe.whitelist(allow_guest=True)
def get_attendance(limit_start=0, limit=3):
    limit_start = cint(limit_start)
    user = frappe.session.user
    row_template = 'for_attendance/doctype/attendance/templates/attendance_row.html'
    result = []
    doctype = 'Attendance'
    meta = frappe.get_meta(doctype)
    all_fields = frappe.get_meta(doctype).fields
    list_view_fields = [df for df in all_fields if df.in_list_view][:4]
    time = frappe.form_dict.time
    default_date = datetime.date.today()
    if 'Employee' and not 'Administrator' in frappe.get_roles(user):
        attendances = frappe.db.sql('''select name from `tabAttendance` where attendance_date = %s
                and employee IN (select name from `tabEmployee` where user_id = %s)
                order by modified desc limit %s, %s''', (default_date, user, limit_start, limit+1), as_dict=1)
        if time and time == 'weekly':
            attendances = frappe.db.sql('''select name from `tabAttendance` where WEEK(attendance_date, 1) = %s
                and employee IN (select name from `tabEmployee` where user_id = %s)
                order by modified desc limit %s, %s''', (default_date.isocalendar()[1], user, limit_start, limit+1), as_dict=1)
        if time and time == 'monthly':
            attendances = frappe.db.sql('''select name from `tabAttendance` where MONTH(attendance_date) = %s
                and employee IN (select name from `tabEmployee` where user_id = %s)
                order by modified desc limit %s, %s''', (default_date.month, user, limit_start, limit+1), as_dict=1)
    else:
        attendances = frappe.db.sql('''select name from `tabAttendance` where attendance_date = %s
                order by modified desc limit %s, %s ''', (default_date, limit_start, limit+1), as_dict=1)
        if time and time == 'weekly':
            attendances = frappe.db.sql('''select name from `tabAttendance` where WEEK(attendance_date, 1) = %s
                order by modified desc limit %s, %s''', (default_date.isocalendar()[1], limit_start, limit+1), as_dict=1)
        if time and time == 'monthly':
            attendances = frappe.db.sql('''select name from `tabAttendance` where MONTH(attendance_date) = %s
                order by modified desc limit %s, %s''', (default_date.month, limit_start, limit+1), as_dict=1)
    show_more = len(attendances) > limit
    if show_more:
        attendances = attendances[:-1]
    for a in attendances:
        doc = frappe.get_doc(doctype, a)
        new_context = frappe._dict(doc=doc, meta=meta, list_view_fields=list_view_fields)
        rendered_row = frappe.render_template(row_template, new_context)
        result.append(rendered_row)
    return {
        "list_view_fields":list_view_fields,
        "result":result,
        "show_more": show_more,
        "next_start": limit_start + limit,
        }

# Not removing follwoing for syntax purpose
# but the above function is better approach I think
# @frappe.whitelist()
# def get_attendance(limit_start=0, limit=5):
#     limit_start = cint(limit_start)
#     row_template = 'for_attendance/doctype/attendance/templates/attendance_row.html'
#     result = []
#     doctype = 'Attendance'
#     meta = frappe.get_meta(doctype)
#     all_fields = frappe.get_meta(doctype).fields
#     list_view_fields = [df for df in all_fields if df.in_list_view][:4]
#     time = frappe.form_dict.time
#     attendances = frappe.get_all(doctype, filters={'attendance_date': datetime.date.today()}, start=limit_start, page_length=limit+1)
#     if time and time != 'today':
#         attendances = frappe.get_all(doctype, start=limit_start, page_length=limit+1)
#     show_more = len(attendances) > limit
#     if show_more:
#         attendances = attendances[:-1]
#     for a in attendances:
#         doc = frappe.get_doc(doctype, a.name)
#         if time:
#             if time == 'today':
#                 checker = True
#             elif time == 'monthly':
#                 checker = bool((doc.attendance_date).month == datetime.date.today().month)
#             elif time == 'weekly':
#                 checker = bool((doc.attendance_date).strftime("%V") == datetime.date.today().strftime("%V"))
#             if checker:
#                 new_context = frappe._dict(doc=doc, meta=meta, list_view_fields=list_view_fields)
#                 rendered_row = frappe.render_template(row_template, new_context)
#                 result.append(rendered_row)
#         else:
#             new_context = frappe._dict(doc=doc, meta=meta, list_view_fields=list_view_fields)
#             rendered_row = frappe.render_template(row_template, new_context)
#             result.append(rendered_row)

#     return {
#         "attendances": attendances,
#         "list_view_fields":list_view_fields,
#         "result":result,
#         "show_more": show_more,
#         "next_start": limit_start + limit,
#         }