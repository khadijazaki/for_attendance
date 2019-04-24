frappe.ready(function () {
	$(".padding").before('<div class="show-table"></div>');
	$(".btn-form-submit").hide();
	var timer = setTimeout(() => {
		var timer = false;

		$('input[data-fieldname="employee"]').on("keyup change", function () {
			if (timer !== false) {
				clearInterval(timer);
			}
			timer = setTimeout(() => {
				submitAttendance();
			}, 1000)
		});
	}, 500);


	function submitAttendance() {
		name = $('input[data-fieldname="employee"]').val();
		console.log(name);
		frappe.call({
			method: "for_attendance.for_attendance.web_form.add_attendance.add_attendance.check_exist", //dotted path to server method
			args: {
                'employee': name
            },
			callback: function(r, rt) {
				if(r.message) {
					frappe.call({
						method: "frappe.client.get",
						args: {
							doctype: "Attendance",
							name: "ATT-2019-00015",
						},
						callback(r) {
							if(r.message) {
								var task = r.message;
								console.log(task);
								frappe.model.set_value("Attendance", 'ATT-2019-00015', "route", 'hello');
								task.save();
							}
						}
					});
					a = frappe.get_doc("Attendance", "ATT-2019-00015");
					console.log(a);
					frappe.model.set_value("Attendance", 'ATT-2019-00015', "route", 'hello')
				//    att = r.message[1];
				//    idx_l = r.message[0].length;
				//    console.log(att + idx_l);
				//    $.ajax({
				// 	url: "/api/resource/Attendance/" + att ,
				// 	dataType: 'text',
				// 	type: 'PUT',
				// 	contentType: 'application/json',
				// 	data: JSON.stringify({
				// 		punching: [{'punch_in_out':'Punch In', 'punch_time': '12:05:00','idx': idx_l +1}]
				// 	}
				// 	),
				// 	beforeSend: function (xhr) {
				// 		xhr.setRequestHeader('X-Frappe-CSRF-Token', frappe.csrf_token);
				// 	},
				// 	success: function (data) {
				// 		console.log(data);
				// 	},
				// 	error: function (error) {
				// 		var string = error.responseText;
				// 		var json_object = JSON.parse(string);
				// 		var msg_object = JSON.parse(json_object._server_messages);
				// 		var msg = JSON.parse(msg_object[0]);
				// 		frappe.msgprint(msg.message);
				// 	}
				// });

				}
				else {
					$.ajax({
						url: "/api/resource/Attendance",
						dataType: 'text',
						type: 'POST',
						contentType: 'application/json',
						data: JSON.stringify({
							employee: name,
							in_out: [{'punch_in_out':'Punch In'}]
						}
						),
						beforeSend: function (xhr) {
							xhr.setRequestHeader('X-Frappe-CSRF-Token', frappe.csrf_token);
						},
						success: function (data) {
							var string = JSON.parse(data);
							check = string.data.in_out;
							time = string.data.attendance_time;
							// frappe.msgprint('Employee ' + name + ' ' + check + ' at ' + time);
							fetch('/api/resource/Employee?fields=["employee_name"]&filters=[["employee","=","' + name + '"]]').then(response => {
								return response.json();
							}).then(function (myJson) {
								var a = JSON.stringify(myJson);
								var string = JSON.parse(a);
								ename = string.data[0].employee_name;
								$('input[data-fieldname="employee_name"]').val(ename);
							});
						},
						error: function (error) {
							var string = error.responseText;
							var json_object = JSON.parse(string);
							var msg_object = JSON.parse(json_object._server_messages);
							var msg = JSON.parse(msg_object[0]);
							frappe.msgprint(msg.message);
						}
					});

				}
			}
		})
	}

})