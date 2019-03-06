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
		$.ajax({
			url: "/api/resource/Attendance",
			dataType: 'text',
			type: 'POST',
			contentType: 'application/json',
			data: JSON.stringify({
				employee: name
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

				fetch('/api/resource/Attendance?fields=["in_out","attendance_time","name"]&filters=[["employee","=","' + name + '"],["attendance_date","=","' + moment().format('YYYY-MM-DD') + '"]]').then(response => {
					return response.json();
				}).then(function (myJson) {
					var a = JSON.stringify(myJson);
					var string = JSON.parse(a);
					values = string.data;
					var tableData = '<table class="table"><thead><tr><th>Time</th><th>IN OUT</th></tr></thead>';
					$.each(values, function (index, data) {
						route_to = '/attendance/' + data.name;
						tableData += '<tbody><tr><td><a href=' + route_to + '>' + moment(data.attendance_time).format('MMMM Do YYYY, h:mm:ss a') + '</a></td><td>' + data.in_out + '</td></tr>';
					});
					tableData += '</tbody></table>';
					$('.show-table').html(tableData);
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

})