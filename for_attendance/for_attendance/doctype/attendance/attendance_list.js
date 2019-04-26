frappe.listview_settings['Attendance'] = {
	add_fields: ["status", "attendance_date", "total_hours"],
	// get_indicator: function(doc) {
	// 	return [__(doc.status), doc.status=="Present" ? "green" : "darkgrey", "status,=," + doc.status];
	// }
	get_indicator: function (doc) {
		if (doc.status === "Present") {
			return [__("Present"), "green", "status,=," + doc.status];

		} else if (doc.status === "Absent"){
			return [__("Absent"), "red", "status,=," + doc.status];
		}
		else if (doc.status === "On Leave"){
			return [__("On Leave"), "blue", "status,=," + doc.status];
		}
	},
	
};
