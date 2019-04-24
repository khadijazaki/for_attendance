# -*- coding: utf-8 -*-
# Copyright (c) 2019, me and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import getdate, add_days, add_years, cstr
from frappe import _
from datetime import datetime

class PunchRequest(Document):
	def validate_att(self):
		att = frappe.get_list('Attendance', filters={'employee': self.employee, 'attendance_date': getdate(self.punch_time)})
		if not att:
			self.add_att()
		else:
			self.update_attendance(att[0].name)

	def add_att(self):
		new_att = frappe.get_doc({"doctype":"Attendance", "employee":self.employee})
		new_att.append('punching', {
			'punch_in_out': self.punch_type,
			'punch_time': self.punch_time
			})
		new_att.insert()

	def update_attendance(self, name):
		new_att = frappe.get_doc('Attendance', name)
		if self.punch_id:
			in_out = frappe.get_list('In Out', filters=[['parent', '=',  name], ['idx', '=', self.punch_id]])
			up = frappe.get_doc('In Out', in_out[0])
			up.punch_time = self.punch_time
			up.punch_in_out = self.punch_type
			up.save()
		else:
			in_out = frappe.get_list('In Out', filters=[['parent', '=',  name], ['punch_time', '<=', self.punch_time]])
			idxs = len(in_out)
			new_att.append('punching', {
				'idx': idxs,
				'punch_in_out': self.punch_type,
				'punch_time': self.punch_time
				})
			for i in range(idxs+1, len(new_att.punching)):
		 		new_att.punching[i - 1].idx = i + 1
			new_att.punching[len(new_att.punching)-1].idx = idxs+1
			new_att.save()
		new_att.save()

	def validate(self):
		punching = get_punch_details(self.employee, self.punch_time)
		x = [x.idx for x in punching]
		if self.update_value:
			if not self.punch_id:
				frappe.throw(_("Must Enter Punch ID to update record"))

	def on_submit(self):
		if self.status == "Open":
			frappe.throw(_("Only Punch Requests with status 'Approved' and 'Rejected' can be submitted"))

		self.validate_att()


@frappe.whitelist()
def get_punch_details(employee, date):
	res = frappe.get_list('Attendance', filters={'employee': employee, 'attendance_date': getdate(date)})
	if res:
		res = frappe.get_doc('Attendance', res[0].name)
		for i in res.punching:
			i.punch_time = (i.punch_time).strftime('%I:%M %p')
		return res.punching