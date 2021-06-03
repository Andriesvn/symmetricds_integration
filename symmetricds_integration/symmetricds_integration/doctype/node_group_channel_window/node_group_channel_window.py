# Copyright (c) 2021, AvN Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from symmetricds_integration.symmetricds_integration.utils import model_insert, model_load_from_db, model_db_update, model_get_list, model_delete_from_table

doctype = 'Node Group Channel Window'
table_name = 'sym_node_group_channel_wnd'
name_field = 'channel_id'
primary_keys = ['node_group_id','channel_id','start_time','end_time']
has_creation = False
has_modified = False
has_modified_by = False

class NodeGroupChannelWindow(Document):
	
	def db_insert(self):
		model_insert(self,doctype,table_name,name_field,primary_keys,
    		has_creation,has_modified,has_modified_by)

	def load_from_db(self):
		model_load_from_db(self,doctype,table_name,name_field,primary_keys,has_creation,has_modified,has_modified_by)

	def db_update(self):
		model_db_update(self,doctype,table_name,name_field,primary_keys,has_creation,has_modified,has_modified_by)
	
	def get_list(self, args):
		return model_get_list(self,doctype,table_name,name_field,primary_keys,has_creation,has_modified,has_modified_by, args)
	
	def delete_from_table(self, doctype, name, ignore_doctypes, doc):
		model_delete_from_table(self,doctype,table_name,name_field,primary_keys,has_creation,has_modified,has_modified_by, name, ignore_doctypes, doc)
	 	

