
frappe.ready(function() {
	var next_start = {{ next_start or 0 }};
	var result_wrapper = $(".website-list .result");

	$(".btn-punch").on("click", function() {
		frappe.call({
			method: "for_attendance.for_attendance.doctype.attendance.attendance.add_punch", //dotted path to server method
			callback: function(r, rt) {
				if(r.message) {
					l = r.message.punching.length
					console.log(l);
					check = r.message.punching[l-1].punch_in_out;
					time = r.message.punching[l-1].punch_time;
					frappe.msgprint('Employee ' + name + ' ' + check + ' at ' + time);
				}
				else{
					$.ajax({
						url: "/api/resource/Attendance",
						dataType: 'text',
						type: 'POST',
						contentType: 'application/json',
						data: JSON.stringify({
							
						}
						),
						beforeSend: function (xhr) {
							xhr.setRequestHeader('X-Frappe-CSRF-Token', frappe.csrf_token);
						},
						success: function (data) {
							console.log(data);
							var string = JSON.parse(data);
							check = string.data.punching[0].punch_in_out;
							time = string.data.punching[0].punch_time;
							frappe.msgprint('Employee ' + name + ' ' + check + ' at ' + time);
							location.reload();
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
		});
		

	});

	$(".website-list .btn-more").on("click", function() {
		var btn = $(this);
		var data = $.extend(frappe.utils.get_query_params(), {
			doctype: "Attendance",
			txt: "{{ txt or '' }}",
			limit_start: next_start,
		});
		console.log('hgj');
        console.log(data);
		data.web_form_name = frappe.web_form_name;
		data.pathname = location.pathname;
		btn.prop("disabled", true);
		return $.ajax({
			url:"/api/method/for_attendance.templates.pages.attendances.get_attendance",
			data: data,
			statusCode: {
				200: function(data) {
					var data = data.message;
                    next_start = data.next_start;
                    console.log(data);
					$.each(data.result, function(i, d) {
						$(d).appendTo(result_wrapper);
					});
					toggle_more(data.show_more);
				}
			}
		}).always(function() {
			btn.prop("disabled", false);
		});
	});
	var toggle_more = function(show) {
		if (!show) {
			$(".website-list .more-block").addClass("hide");
		}
	};

	if($('.navbar-header .navbar-toggle:visible').length === 1)
	{
		$('.page-head h1').addClass('list-head').click(function(){
			window.history.back();
	 	});
	}
});
