# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe

from frappe.utils import getdate, nowdate
from frappe import _
from frappe.website.website_generator import WebsiteGenerator
from erpnext.hr.utils import set_employee_name
from frappe.utils import cstr
from frappe.model.naming import make_autoname
import datetime
from bs4 import BeautifulSoup
import urllib2

class Attendance(WebsiteGenerator):
	def validate_duplicate_record(self):
		res = frappe.db.sql("""select name from `tabAttendance` where employee = %s and attendance_date = %s
			and name != %s and attendance_time = %s""",
			(self.employee, self.attendance_date, self.name, self.attendance_time))
		if res:
			frappe.throw(_("Attendance for employee {0} is already marked").format(self.employee))

		set_employee_name(self)

	# To set check out and check in of employee
	def validate_in_out(self):
		# first check if a record exists for current day of the same employee 
		# by default check in is set so the first record of user that day will be check in
		res = frappe.db.sql("""select name, in_out from `tabAttendance` where employee = %s and attendance_date = %s
			and name != %s """,
			(self.employee, self.attendance_date, self.name), as_dict=True)
		#if record exist then toggle what ever value it has
		if res:
			for d in res:
				if d.in_out == 'Check In':
					self.in_out = 'Check Out'
				elif d.in_out == 'Check Out':
					self.in_out = 'Check In'

	def check_leave_record(self):
		leave_record = frappe.db.sql("""select leave_type, half_day, half_day_date from `tabLeave Application`
			where employee = %s and %s between from_date and to_date and status = 'Approved'
			and docstatus = 1""", (self.employee, self.attendance_date), as_dict=True)
		if leave_record:
			for d in leave_record:
				if d.half_day_date == getdate(self.attendance_date):
					self.status = 'Half Day'
					frappe.msgprint(_("Employee {0} on Half day on {1}").format(self.employee, self.attendance_date))
				else:
					self.status = 'On Leave'
					self.leave_type = d.leave_type
					frappe.msgprint(_("Employee {0} is on Leave on {1}").format(self.employee, self.attendance_date))

		if self.status == "On Leave" and not leave_record:
			frappe.throw(_("No leave record found for employee {0} for {1}").format(self.employee, self.attendance_date))

	def validate_attendance_date(self):
		date_of_joining = frappe.db.get_value("Employee", self.employee, "date_of_joining")

		if getdate(self.attendance_date) > getdate(nowdate()):
			frappe.throw(_("Attendance can not be marked for future dates"))
		elif date_of_joining and getdate(self.attendance_date) < getdate(date_of_joining):
			frappe.throw(_("Attendance date can not be less than employee's joining date"))

	def validate_employee(self):
		emp = frappe.db.sql("select name from `tabEmployee` where name = %s",
		 	self.employee)
		if not emp:
			frappe.throw(_("Employee {0} is not active or does not exist").format(self.employee))

	def validate(self):
		from erpnext.controllers.status_updater import validate_status
		validate_status(self.status, ["Present", "Absent", "On Leave", "Half Day"])
		self.validate_attendance_date()
		self.validate_employee()
		self.validate_duplicate_record()
		self.check_leave_record()
		self.validate_in_out()

	def autoname(self):
		dt = frappe.get_meta("Attendance")
		if dt:
			key = dt.get("autoname")
        	self.name = make_autoname(key)

	def get_context(context):
		context.doc = frappe.get_doc(frappe.form_dict.doctype, frappe.form_dict.name)

		default_print_format = frappe.db.get_value('Property Setter', dict(property='default_print_format', doc_type=frappe.form_dict.doctype), "value")
		if default_print_format:
			context.print_format = default_print_format
		else:
			context.print_format = "Standard"
        
@frappe.whitelist()
def get_events(start, end, filters=None):
	events = []

	employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user})

	if not employee:
		return events

	from frappe.desk.reportview import get_filters_cond
	conditions = get_filters_cond("Attendance", filters, [])
	add_attendance(events, start, end, conditions=conditions)
	return events

def add_attendance(events, start, end, conditions=None):
	query = """select name, attendance_date, status
		from `tabAttendance` where
		attendance_date between %(from_date)s and %(to_date)s
		and docstatus < 2"""
	if conditions:
		query += conditions

	for d in frappe.db.sql(query, {"from_date":start, "to_date":end}, as_dict=True):
		e = {
			"name": d.name,
			"doctype": "Attendance",
			"date": d.attendance_date,
			"title": cstr(d.status),
			"docstatus": d.docstatus
		}
		if e not in events:
			events.append(e)

def get_list_context(context=None):
	context.update({
		"get_list": get_attendance_list,
	})

def get_attendance_list(doctype, txt, filters, limit_start, limit_page_length=20, order_by="modified"):
	default_date = datetime.date.today()
	time = frappe.form_dict.time
	if time:
		if time == "today":
			return frappe.db.sql('''select name, employee, employee_name, attendance_time, in_out from `tabAttendance` where attendance_date = %s
			''', default_date, as_dict=1)
		elif time == "weekly":
			default_date = datetime.date.today().isocalendar()[1]
			return frappe.db.sql('''select name, employee, employee_name, attendance_time, in_out from `tabAttendance` where WEEK(attendance_date, 1) = %s
			''', default_date, as_dict=1)
		elif time == "monthly":
			default_date = datetime.date.today().month
			return frappe.db.sql('''select name, employee, employee_name, attendance_time, in_out from `tabAttendance` where MONTH(attendance_date) = %s
			''', default_date, as_dict=1)
	else:
		return frappe.db.sql('''select name, employee, employee_name, attendance_time, in_out from `tabAttendance` where attendance_date = %s
		''', default_date, as_dict=1)

