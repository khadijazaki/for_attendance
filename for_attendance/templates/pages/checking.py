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
	all_fields = frappe.get_meta(doc.doctype).fields


	return {
		"doc":doc,
		"name": doc.get(meta.title_field) if meta.title_field else doc.name,
		"all_fields":all_fields
	}