from __future__ import unicode_literals

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cstr

def get_context(context):
	if not 'Attendance Manager' in frappe.get_roles(frappe.session.user):
		frappe.throw(_("You are not allowed to access this page"), frappe.PermissionError)

# @frappe.whitelist()
# def check_exist(employee):
# 	res = frappe.db.sql("""select name from `tabAttendance` where employee = %s and attendance_date = %s""",
# 			(employee, frappe.utils.nowdate()), as_dict=True)
# 	if res:
# 		return res

@frappe.whitelist()
def check_exist(employee):
	res = frappe.db.sql("""select name from `tabAttendance` where employee = %s and attendance_date = %s""",
			(employee, frappe.utils.nowdate()), as_dict=True)
	if res:
		c = frappe.db.sql("""select name from `tabIn Out` where parent = %s """,
			(res[0].name), as_dict=True)
		return c, res[0].name