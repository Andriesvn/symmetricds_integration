# Copyright (c) 2021, AvN Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from symmetricds_integration.symmetricds_integration.utils import model_insert, model_load_from_db, model_db_update, model_get_list, model_delete_from_table


doctype = 'DB Table'
table_name = 'information_schema`.`tables'
name_field = 'table_name'
primary_keys = ['table_name']
has_creation = False
has_modified = False
has_modified_by = False

class DBTable(Document):
	
	def db_insert(self):
		pass

	def load_from_db(self):
		model_load_from_db(self,doctype,table_name,name_field,primary_keys,has_creation,has_modified,has_modified_by)

	def db_update(self):
		pass

	def get_list(self, args):
		return model_get_list(self,doctype,table_name,name_field,primary_keys,has_creation,has_modified,has_modified_by, args)

	def delete_from_table(self, doctype, name, ignore_doctypes, doc):
		pass
