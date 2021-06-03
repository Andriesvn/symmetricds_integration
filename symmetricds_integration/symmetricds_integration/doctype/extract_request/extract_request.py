# Copyright (c) 2021, AvN Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from symmetricds_integration.symmetricds_integration.utils import model_insert, model_load_from_db, model_db_update, model_get_list, fix_int_name

doctype = 'Extract Request'
table_name = 'sym_extract_request'
name_field = 'request_id'
primary_keys = ['request_id']
has_creation = True
has_modified = True
has_modified_by = False

class ExtractRequest(Document):
	
	def db_insert(self):
		pass

	def load_from_db(self):
		model_load_from_db(self,doctype,table_name,name_field,primary_keys,has_creation,has_modified,has_modified_by)


	def db_update(self):
		model_db_update(self,doctype,table_name,name_field,primary_keys,has_creation,has_modified,has_modified_by)
	
	def get_list(self, args):
		items = model_get_list(self,doctype,table_name,name_field,primary_keys,has_creation,has_modified,has_modified_by, args)
		return list(map(fix_int_name,items))
	
	def delete_from_table(self, doctype, name, ignore_doctypes, doc):
		pass
