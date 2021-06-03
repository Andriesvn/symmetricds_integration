# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe, json
from frappe import _
from frappe.utils.dashboard import cache_source
from frappe.utils import add_to_date, date_diff, getdate, nowdate, get_last_day, formatdate, get_link_to_form
from frappe.utils.dateutils import get_from_date_from_timespan, get_period_ending
from erpnext.loan_management.report.applicant_wise_loan_security_exposure.applicant_wise_loan_security_exposure \
	 import get_loan_security_details
from six import iteritems

@frappe.whitelist()
@cache_source
def get_data(chart_name = None, chart = None, no_cache = None, filters = None, from_date = None,
	to_date = None, timespan = None, time_interval = None, heatmap_year = None):
	if chart_name:
		chart = frappe.get_doc('Dashboard Chart', chart_name)
	else:
		chart = frappe._dict(frappe.parse_json(chart))

	timespan = chart.timespan

	if chart.timespan == 'Select Date Range':
		from_date = chart.from_date
		to_date = chart.to_date
    
	timegrain = chart.time_interval


	filters = frappe.parse_json(filters) or frappe.parse_json(chart.filters_json)
	node_id = filters.get("node_id")


	if not to_date:
		to_date = nowdate()
	if not from_date:
		if timegrain in ('Monthly', 'Quarterly','Weekly','Daily'):
			from_date = get_from_date_from_timespan(to_date, timespan)

	# fetch dates to plot
	dates = get_dates_from_timegrain(from_date, to_date, timegrain)

	entries = get_incomming_batch_entries(node_id,from_date,to_date)

	result = build_result(dates,entries)

	return {
		'labels': [formatdate(r[0].strftime('%Y-%m-%d')) for r in result],
		'datasets': [{
			'name': 'Recieved',
			'chartType': 'line',
			'values': [r[1] for r in result]
		},
		{
			'name': 'Sent',
			'chartType': 'line',
			'values': [r[2] for r in result]
		},
		{
			'name': 'Successfully Processed',
			'chartType': 'line',
			'values': [r[3] for r in result]
		},
		{
			'name': 'Error',
			'chartType': 'line',
			'values': [r[4] for r in result]
		}
        ]
	}

def build_result(dates, entries):
	result = [[getdate(date), 0.0, 0.0, 0.0, 0.0] for date in dates]
    # start with the first date
	date_index = 0
	for entry in entries:
		# entry date is after the current pointer, so move the pointer forward
		while getdate(entry.create_time) > result[date_index][0]:
			date_index += 1
		if entry.type == 'incoming':
			result[date_index][1] += 1
		if entry.type == 'outgoing':
			result[date_index][2] += 1
		if entry.status == 'OK':
			result[date_index][3] += 1
		if entry.status == 'ER':
			result[date_index][4] += 1
	
	return result

def get_incomming_batch_entries(node_id,from_date, to_date):
    to_date = add_to_date(to_date, days=1)
    conditions = ''
    if not(node_id.lower() == 'all'):
        conditions = "AND node_id = '{0}'".format(node_id)
    select_sql = """
		SELECT 'incoming' as `type`, batch_id , node_id, create_time, status
		FROM `sym_incoming_batch`
		WHERE create_time >= '{0}'
		AND create_time <= '{1}'
        {2}
        UNION ALL
        SELECT 'outgoing' as `type`, batch_id, node_id, create_time, status
		FROM `sym_outgoing_batch`
		WHERE create_time >= '{0}'
		AND create_time <= '{1}'
        {2}
        ORDER BY create_time
	""".format(from_date,to_date,conditions)
    return frappe.db.sql(select_sql, {}, as_dict=1)


def get_dates_from_timegrain(from_date, to_date, timegrain):
	days = months = years = 0
	if "Daily" == timegrain:
		days = 1
	elif "Weekly" == timegrain:
		days = 7
	elif "Monthly" == timegrain:
		months = 1
	elif "Quarterly" == timegrain:
		months = 3

	dates = [get_period_ending(from_date, timegrain)]
	while getdate(dates[-1]) < getdate(to_date):
		date = get_period_ending(add_to_date(dates[-1], years=years, months=months, days=days), timegrain)
		dates.append(date)
	return dates