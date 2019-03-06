from __future__ import unicode_literals

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cstr

def get_context(context):
	if not 'Attendance Manager' in frappe.get_roles(frappe.session.user):
		frappe.throw(_("You are not allowed to access this page"), frappe.PermissionError)