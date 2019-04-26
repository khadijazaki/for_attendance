# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

import frappe, os, copy, json, re
from frappe import _

from frappe.modules import get_doc_path
from frappe.utils import cint, strip_html
from six import string_types

no_cache = 1
no_sitemap = 1

def get_context(context):
	"""Build context for print"""
	if not ((frappe.form_dict.doctype and frappe.form_dict.name) or frappe.form_dict.doc):
		return {
			"body": """<h1>Error</h1>
				<p>Parameters doctype and name required</p>
				<pre>%s</pre>""" % repr(frappe.form_dict)
		}

	if frappe.form_dict.doc:
		doc = frappe.form_dict.doc
	else:
		doc = frappe.get_doc(frappe.form_dict.doctype, frappe.form_dict.name)

	meta = frappe.get_meta(doc.doctype)
	if hasattr(doc, "set_indicator"):
		doc.set_indicator()
	for i in doc.punching:
			i.punch_time = (i.punch_time).strftime('%I:%M %p')


	return {
		"doc":doc,
		"name": doc.get(meta.title_field) if meta.title_field else doc.name,
		"employee":doc.employee,
		"employee_name":doc.employee_name,
		"a_date":doc.attendance_date,
		"punching":doc.punching,
		"status":doc.status,
		"total_hours": doc.total_hours,
		"total_in_week": doc.total_in_week,
		"total_in_month": doc.total_in_month,
	}