# -*- coding: utf-8 -*-
# Copyright (c) 2019, me and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class InOut(Document):
	def after_insert(self):
		check = 'hello'
