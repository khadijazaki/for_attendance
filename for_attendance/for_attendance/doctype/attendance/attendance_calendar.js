// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
frappe.views.calendar["Attendance"] = {
	field_map: {
		"start": "date",
		"end": "date",
		"id": "name",
		"status": "status"
	},

	get_events_method: "erpnext.hr.doctype.attendance.attendance.get_events",
	onload: function() {
		// $(".fc-left").append("<p>Some appended text.</p>");
		alert('hello');
	}
};