frappe.provide('frappe.dashboards.chart_sources');

frappe.dashboards.chart_sources["Incomming Batch Timeline"] = {
	method: "symmetricds_integration.symmetricds_integration.dashboard_chart_source.incomming_batch_timeline.incomming_batch_timeline.get_data",
	filters: [
		{
			fieldname: "node_id",
			label: __("Node"),
			fieldtype: "Link",
			options: "Node",
			default: "ALL"
		}
	]
};