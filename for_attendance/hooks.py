# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version
from frappe import _

app_name = "for_attendance"
app_title = "For Attendance"
app_publisher = "me"
app_description = "A seperate app for attendance"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "me@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/for_attendance/css/for_attendance.css"
# app_include_js = "/assets/for_attendance/js/for_attendance.js"

# include js, css files in header of web template
# web_include_css = "/assets/for_attendance/css/for_attendance.css"
# web_include_js = "/assets/for_attendance/js/for_attendance.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}


website_generators = ["Attendance"]

website_route_rules = [
	{"from_route": "/attendance", "to_route": "Attendance"},
	{"from_route": "/attendance/<path:name>", "to_route": "attendance_detail",
		"defaults": {
			"doctype": "Attendance",
			"parents": [{"label": _("check"), "route": "attendance"}]
		}
  }
]

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "for_attendance.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "for_attendance.install.before_install"
# after_install = "for_attendance.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "for_attendance.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"for_attendance.tasks.all"
# 	],
# 	"daily": [
# 		"for_attendance.tasks.daily"
# 	],
# 	"hourly": [
# 		"for_attendance.tasks.hourly"
# 	],
# 	"weekly": [
# 		"for_attendance.tasks.weekly"
# 	]
# 	"monthly": [
# 		"for_attendance.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "for_attendance.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "for_attendance.event.get_events"
# }

