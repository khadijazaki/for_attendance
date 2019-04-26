// Copyright (c) 2019, me and contributors
// For license information, please see license.txt


frappe.ui.form.on('Punch Request', {
	on_load: function(frm){
		frm.trigger("make_dashboard");
	},

	refresh: function(frm){
		frm.trigger("make_dashboard");
	},
    
	make_dashboard: function(frm) {
		var punch_details = [];
		var ids = [];
		if (frm.doc.employee && frm.doc.punch_time) {

			frappe.call({
				method: "for_attendance.for_attendance.doctype.punch_request.punch_request.get_punch_details",
				async: false,
				args: {
					employee: frm.doc.employee,
					date: frm.doc.punch_time
				},
				callback: function(r) {
					if (r.message) {
						punch_details = r.message;
						for (var i = 0; i < punch_details['punching'].length; i++) {
							ids.push(punch_details['punching'][i].idx);
						  }
						frm.set_df_property('punch_id', 'options', ids );
						frm.refresh_field('punch_id');
					}
				}
			});
			$("div").remove(".form-dashboard-section");
			let section = frm.dashboard.add_section(
				frappe.render_template('punch_request_dashboard', {
					times: punch_details['punching'],
					date: moment(frm.doc.punch_time).format('DD-MMM-YYYY'),
					status: punch_details['status']
				})
			);



			frm.dashboard.show();
		}
	},

	punch_time: function(frm) {
		frm.trigger("make_dashboard");
	},
});
