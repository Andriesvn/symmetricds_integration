// Copyright (c) 2021, AvN Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Node', {
	onload: function(frm) {


	},
	refresh: function (frm) {
		frm.page.clear_primary_action();
			frm.add_custom_button(__("Send Bench Command"),
				function () {
					frm.events.send_command(frm);
				}
			).toggleClass('btn-primary');
	},

	send_command: function (frm) {
		const dialog = new frappe.ui.Dialog({
			title: __('Send Node Bench Command'),
			fields: [
				{
					label: __('Command'),
					fieldname: 'command',
					fieldtype: 'Data',
					reqd: 1,
				},
			],
			primary_action: async function({ command }) {
				// filter balance details for empty rows
				const method = "send_bench_command";
				const res = await frappe.call({ 
					doc: frm.doc, 
					method, 
					args: { command }, 
					freeze:true 
				});
				dialog.hide();
			},
			primary_action_label: __('Submit')
		});
		dialog.show();
	},
});
