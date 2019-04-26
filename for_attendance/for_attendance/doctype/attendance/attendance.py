# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe

from frappe.utils import getdate, nowdate, now, time_diff_in_hours
from frappe import _
from frappe.website.website_generator import WebsiteGenerator
from erpnext.hr.utils import set_employee_name
from frappe.utils import cstr
from frappe.model.naming import make_autoname
from datetime import datetime, date
from bs4 import BeautifulSoup
import urllib2

class Attendance(WebsiteGenerator):
	def validate_duplicate_record(self):
		res = frappe.db.sql("""select name from `tabAttendance` where employee = %s and attendance_date = %s
			and name != %s""",
			(self.employee, self.attendance_date, self.name))
		if res:
			frappe.throw(_("Attendance for employee {0} is already marked").format(self.employee))

		set_employee_name(self)

	def before_insert(self, ignore_permissions=True):
		if len(self.punching) == 0 and self.status == 'Present':
			row = self.append('punching', {
			'punch_in_out': 'Punch In',
			'punch_time': frappe.utils.now()
			})

	# # To set check out and check in of employee
	def validate_in_out(self):
		lenof = len(self.punching)
		if lenof > 1:
			# for i in range(2, lenof):
			# 	self.punching[i].idx = i + 1 
			for i in self.punching:
				if i.idx % 2 == 0:
					i.punch_in_out = 'Punch Out'
				else:
					i.punch_in_out = 'Punch In'
			# else:
			# 	if self.punching[lenof-2].punch_in_out == 'Punch In':
			# 		self.punching[lenof-1].punch_in_out = 'Punch Out'
			# 	elif self.punching[lenof-2].punch_in_out == 'Punch Out':
			# 		self.punching[lenof-1].punch_in_out = 'Punch In'

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
			
	def validate_total_hours(self):
		lenof = len(self.punching)
		if lenof >= 1:
			punch_in = [i.punch_time for i in self.punching if i.punch_in_out == 'Punch In']
			punch_out = [i.punch_time for i in self.punching if i.punch_in_out == 'Punch Out']
			if len(punch_in) != len(punch_out):
				punch_in.pop()
			differences = [time_diff_in_hours(y,x) for x, y in zip(punch_in, punch_out)]
			self.total_hours = round(sum(differences), 2)
		else:
			self.total_hours = 0

	def validate_total_in_week_month(self):
		import datetime
		if isinstance(self.attendance_date, datetime.date):
			check_date = self.attendance_date
		else:
			from datetime import datetime, date
			check_date = datetime.strptime(self.attendance_date, '%Y-%m-%d').date()
		a_time_w = frappe.db.sql('''select round(sum(total_hours), 2) from `tabAttendance` where WEEK(attendance_date, 1) = %s''', check_date.isocalendar()[1], as_list=1)
		self.total_in_week = a_time_w[0][0]
		a_time_m = frappe.db.sql('''select round(sum(total_hours), 2) from `tabAttendance` where MONTH(attendance_date) = %s''', check_date.month, as_list=1)
		self.total_in_month = a_time_m[0][0]


	def validate(self):
		from erpnext.controllers.status_updater import validate_status
		validate_status(self.status, ["Present", "Absent", "On Leave", "Half Day"])
		self.validate_attendance_date()
		self.validate_employee()
		self.validate_duplicate_record()
		self.check_leave_record()
		self.validate_in_out()
		self.validate_total_hours()
		self.validate_total_in_week_month()

	def autoname(self):
		dt = frappe.get_meta("Attendance")
		if dt:
			key = dt.get("autoname")
        	self.name = make_autoname(key)

	def get_context(context):
		# context.doc = frappe.get_doc(frappe.form_dict.doctype, frappe.form_dict.name)

		context.print_format = "Standard"

	
	def set_indicator(self):
		"""Set indicator for portal"""
		if self.status == 'Present':
			self.indicator_color = "green"
			self.indicator_title = _("Present")

		elif self.status == 'Absent':
			self.indicator_color = "red"
			self.indicator_title = _("Absent")

		elif self.status == 'Present':
			self.indicator_color = "blue"
			self.indicator_title = _("On Leave")
        
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

@frappe.whitelist()
def add_punch():
	emp = frappe.get_list('Employee', filters={'user_id': frappe.session.user}, fields=['name'])
	if not emp:
		frappe.throw(_("You are not an employee"))
	res = frappe.get_list('Attendance', filters={'employee': emp[0].name, 'attendance_date': now()})
	if res:
		res = frappe.get_doc('Attendance', res[0].name)
		if res.status != 'Present':
			frappe.throw(_("Not allowed as attendance is not marked Present"))
			return res
		res.append('punching', {
			'punch_in_out': 'Punch In',
			'punch_time': frappe.utils.now()
		})
		res.save(ignore_permissions=True)
		return res