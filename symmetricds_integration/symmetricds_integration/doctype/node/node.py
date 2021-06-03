# Copyright (c) 2021, AvN Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from symmetricds_integration.symmetricds_integration.utils import model_insert, model_load_from_db, model_db_update, model_get_list, model_delete_from_table
from symmetricds_integration.symmetricds_integration.utils import send_command, send_bench_command

doctype = 'Node'
table_name = 'sym_node'
name_field = 'node_id'
primary_keys = ['node_id']
has_creation = False
has_modified = False
has_modified_by = False

class Node(Document):
	
	def db_insert(self):
		pass

	def load_from_db(self):
		model_load_from_db(self,doctype,table_name,name_field,primary_keys,has_creation,has_modified,has_modified_by)


	def db_update(self):
		model_db_update(self,doctype,table_name,name_field,primary_keys,has_creation,has_modified,has_modified_by)
	
	def get_list(self, args):
		return model_get_list(self,doctype,table_name,name_field,primary_keys,has_creation,has_modified,has_modified_by, args)
	
	def delete_from_table(self, doctype, name, ignore_doctypes, doc):
		pass

	@frappe.whitelist()
	def send_command(self, type, expression):
		send_command([self.node_id],expression, type)
	
	@frappe.whitelist()
	def send_bench_command(self, command):
		send_bench_command([self.node_id], command)
