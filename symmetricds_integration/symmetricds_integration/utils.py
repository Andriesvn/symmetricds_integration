from __future__ import unicode_literals

import frappe, os
from frappe import throw, _
from frappe.utils import cint, now, getdate, cast_fieldtype, get_filter
from frappe.model.document import Document
import re

DOCTYPES_FOR_DOCTYPE = ('DocType', 'DocField', 'DocPerm', 'DocType Action', 'DocType Link')

def model_insert(model=None,doctype=None,table_name=None,name_field=None,primary_keys=[],
    has_creation=False,has_modified=False,has_modified_by=False):
    insert_item(table_name,name_field, model, has_creation,has_modified,has_modified_by)

def model_load_from_db(model=None,doctype=None,table_name=None,name_field=None,primary_keys=[],
    has_creation=False,has_modified=False,has_modified_by=False):
    if model.name !=doctype:
        items = get_value(table_name,name_field, model.name, has_creation,has_modified,has_modified_by,primary_keys)
        if len(items) > 0:
            super(Document, model).__init__(items[0])
    model.init_valid_columns()
    model._fix_numeric_types()


def model_db_update(model=None,doctype=None,table_name=None,name_field=None,primary_keys=None,has_creation=False,
    has_modified=False,has_modified_by=False):
    update_item(table_name,name_field, model,
    has_creation,has_modified,has_modified_by, primary_keys)

def model_get_list(model=None,doctype=None,table_name=None,name_field=None,primary_keys=[],
    has_creation=False,has_modified=False,has_modified_by=False,
    args=None):
    return get_table(table_name,name_field, doctype, args['fields'] if 'fields' in args else None, 
    args['filters'] if 'filters' in args else None, args['order_by'] if 'order_by' in args else None, 
    args['start'] if 'start' in args else args['limit_start'] if 'limit_start' in args else None, 
    args['page_length'] if 'page_length' in args else args['limit_page_length'] if 'limit_page_length' in args else None,
    has_creation,has_modified,has_modified_by, args['as_list'] if 'as_list' in args else False,
    args['or_filters'] if 'or_filters' in args else None, primary_keys)

def model_delete_from_table(model=None,doctype=None,table_name=None,name_field=None,primary_keys=[],has_creation=False,has_modified=False,has_modified_by=False,
    name=None, ignore_doctypes=None, doc=None):
    delete_from_table(table_name,name_field, doctype, name, ignore_doctypes, doc, primary_keys)

def get_table(table_name, name_field=None,
doctype=None, fields=None, filters=None, order_by=None, start=None, page_length=None
,has_creation=False, has_modified=False, has_modified_by=False, as_list=False, or_filters=None, primary_keys=[]):
    select = "select * from `{0}`".format(table_name)
    orderby = ""
    conditions = None 
    limit_start = None 
    limit_page_length = None
    values = {}
    fixedname_field = get_fixed_name_field(table_name, name_field,primary_keys)

    print('fields:',fields)

    if page_length: 
        limit_page_length = cint(page_length) if page_length else None
        limit_start = 0 if (start == None) else cint(start)

    limit = add_limit(limit_page_length,limit_start)
    if (order_by != None):
        order_by = order_by.replace("`tab{0}`".format(doctype),"`{0}`".format(table_name))
        order_by = re.sub("`{0}`.`name`|`name`|`{0}`.`idx`|`idx`|`{0}`.idx".format(table_name),fixedname_field, order_by)
        if (has_creation):
            order_by = order_by.replace("`creation`","`create_time`")
        else:
            order_by = order_by.replace("`{0}`.`creation`".format(table_name),"null")
        if (has_modified):
            order_by = order_by.replace("`modified`","`last_update_time`")
        else:
            order_by = order_by.replace("`{0}`.`modified`".format(table_name),"null")
        if (has_modified_by):
            order_by = order_by.replace("`modified_by`","`last_update_by`")
        else:
             order_by = order_by.replace("`{0}`.`modified_by`".format(table_name),"null")
        order_by = re.sub("`{0}`.`owner`|`owner`|`{0}`.`_user_tags`|`_user_tags`|`{0}`.`_comments`|`_comments`|`{0}`.`_assign`|`_assign`|`{0}`.`_liked_by`|`_liked_by`|`{0}`.`parent`|`parent`|`{0}`.`parenttype`|`parenttype`|`{0}`.`parentfield`|`parentfield`".format(table_name),
            "null",order_by)
        order_by = re.sub("`{0}`.`docstatus`|`docstatus`".format(table_name),"0",order_by)
        orderby = "ORDER BY {0}".format(order_by)

    if filters != None:
        if isinstance(filters, dict):
            filters = [filters]
        conditions, values = get_conditions(filters, name_field, doctype, " and ", table_name, primary_keys)
    
    if or_filters != None:
        if isinstance(or_filters, dict):
            or_filters = [or_filters]
        or_conditions, or_values = get_conditions(or_filters, name_field, doctype, " or ", table_name, primary_keys)
        values.update(or_values)
        conditions = "{0} {1}".format(conditions,or_conditions)
    
    conditions = conditions.strip()

    if conditions == "":
        conditions = None

    fixed_fields = []
    if (fields != None and len(fields) > 0):
        if isinstance(fields, str):
            fields = [fields]
        for field in fields:
            fixed_field = field.replace("`tab{0}`".format(doctype),"`{0}`".format(table_name))
            fixed_field = re.sub("`{0}`.`name`|`name`|`{0}`.`idx`|`idx`".format(table_name),fixedname_field, fixed_field)
            fixed_field = re.sub("`{0}`.`owner`|`owner`|`{0}`.`_user_tags`|`_user_tags`|`{0}`.`_comments`|`_comments`|`{0}`.`_assign`|`_assign`|`{0}`.`_liked_by`|`_liked_by`|`{0}`.`parent`|`parent`|`{0}`.`parenttype`|`parenttype`|`{0}`.`parentfield`|`parentfield`".format(table_name),
            "null",fixed_field)
            fixed_field = re.sub("`{0}`.`docstatus`|`docstatus`".format(table_name),"0",fixed_field)
            
            if (has_creation):
                fixed_field = fixed_field.replace("`creation`","create_time")
            if (has_modified):
                fixed_field = fixed_field.replace("`modified`","last_update_time")
            if (has_modified_by):
                fixed_field = fixed_field.replace("`modified_by`","last_update_by")


            if field == "`tab{0}`.`name`".format(doctype) or field == "name":
                fixed_field = "{0} as `name`".format(fixedname_field)
            if field == "`tab{0}`.`idx`".format(doctype)  or field == "idx":
                fixed_field = "{0} as `idx`".format(fixedname_field)

            if field == "`tab{0}`.`owner`".format(doctype) or field == "owner":
                fixed_field = "null as `owner`".format(table_name)
            if field == "`tab{0}`.`_user_tags`".format(doctype) or field == "_user_tags":
                fixed_field = "null as `_user_tags`".format(table_name)
            if field == "`tab{0}`.`_comments`".format(doctype) or field == "_comments":
                fixed_field = "null as `_comments`".format(table_name)
            if field == "`tab{0}`.`_assign`".format(doctype) or field == "_assign":
                fixed_field = "null as `_assign`".format(table_name)
            if field == "`tab{0}`.`_liked_by`".format(doctype) or field == "_liked_by":
                fixed_field = "null as `_liked_by`".format(table_name)
            if field == "`tab{0}`.`parent`".format(doctype) or field == "parent":
                fixed_field = "null as `parent`".format(table_name)
            if field == "`tab{0}`.`parenttype`".format(doctype) or field == "parenttype":
                fixed_field = "null as `parenttype`".format(table_name)
            if field == "`tab{0}`.`parentfield`".format(doctype) or field == "parentfield":
                fixed_field = "null as `parentfield`".format(table_name)
            if field == "`tab{0}`.`docstatus`".format(doctype) or field == "docstatus":
                fixed_field = "0 as `docstatus`".format(table_name)

            if field == "`tab{0}`.`creation`".format(doctype) or field == "creation":
                if has_creation :
                    fixed_field = "`{0}`.`create_time` as `creation`".format(table_name)
                else: 
                    fixed_field = "null as `creation`"

            if field == "`tab{0}`.`modified`".format(doctype) or field == "modified":
                if has_modified :
                    fixed_field = "`{0}`.`last_update_time` as `modified`".format(table_name)
                else: 
                    fixed_field = "null as `modified`"

            if field == "`tab{0}`.`modified_by`".format(doctype) or field == "modified_by":
                if has_modified_by :
                    fixed_field = "`{0}`.`last_update_by` as `modified_by`".format(table_name)
                else: 
                    fixed_field = "null as `modified_by`"

            fixed_fields.append(fixed_field)
    else:
        fixed_fields =  ["{0} as `name`".format(fixedname_field)]

    select = """select {0}
    from `{1}`""".format(", ".join(fixed_fields), table_name)

    select_statment= """{0}
        {1} 
        {2} 
        {3}
        {4}""".format(select,"where" if conditions else "", conditions if conditions else "", orderby, limit)
    items = frappe.db.sql(select_statment, values,
        as_list= as_list, 
        as_dict= not(as_list))
    
    return items

def get_conditions(filters, name_field, doctype, sep = " and ", table_name= None, primary_keys=[]):
    from frappe.boot import get_additional_filters_from_hooks
    additional_filters_config = get_additional_filters_from_hooks()
    conditions = []
    values = {}
    fixedname_field = get_fixed_name_field(table_name, name_field,primary_keys)

    for filter in filters:
       f = get_filter(doctype, filter, additional_filters_config)
       if not(f.fieldname in ['name','idx']):
           conditions.append("`{0}` {1} %({2})s".format(f.fieldname,f.operator,f.fieldname))
           values[f.fieldname] = f.value
       else:
           conditions.append("{0} {1} %({2})s".format(fixedname_field,f.operator,name_field))
           values[name_field] = f.value
    return sep.join(conditions), values

def get_fixed_name_field(table_name, name_field,primary_keys=[]):
    fixedname_field = "`{0}`.`{1}`".format(table_name, name_field)
    fixed_primary_keys=[]
    if len(primary_keys) > 1:
        for key in primary_keys:
            fixed_primary_keys.append("`{0}`.`{1}`".format(table_name, key))
        fixedname_field = "CONCAT_WS('::',{0})".format(",".join(fixed_primary_keys))
    return fixedname_field

def get_fixed_primary_keys(table_name, primary_keys=[]):
    fixed_primary_keys=[]
    for key in primary_keys:
        fixed_primary_keys.append("`{0}`.`{1}`").format(table_name, key)
    
    return fixed_primary_keys

def get_value(table_name, name_field=None, key=None, has_creation=False, has_modified=False, has_modified_by=False, primary_keys=[]):
    
    fixedname_field = get_fixed_name_field(table_name, name_field, primary_keys)
    
    fixed_fields = [
        "`{0}`.*".format(table_name), 
        "{0} as `name`".format(fixedname_field),
        "{0} as `idx`".format(fixedname_field),
        ]
    if (has_creation):
        fixed_fields.append("`{0}`.`create_time` as `creation`".format(table_name))
    if (has_modified):
        fixed_fields.append("`{0}`.`last_update_time` as `modified`".format(table_name))
    if (has_modified_by):
        fixed_fields.append("`{0}`.`last_update_by` as `modified_by`".format(table_name))

    values = {'name': key} 
    select = """select {0}
        from `{1}`
        WHERE {2} = %({3})s""".format(", ".join(fixed_fields), table_name, fixedname_field, "name")
    return frappe.db.sql(select, values, as_dict=1)


def add_limit(limit_page_length, limit_start):
		if limit_page_length:
			return 'limit %s offset %s' % (limit_page_length, limit_start)
		else:
			return ''

def insert_item(table_name, name_field, item, has_creation=False, has_modified=False, has_modified_by=False):
    """INSERT the document (with valid columns) in the database."""
  
    if not item.creation:
        item.creation = item.modified = now()
        item.created_by = item.modified_by = frappe.session.user


    # if doctype is "DocType", don't insert null values as we don't know who is valid yet
    d = item.get_valid_dict(convert_dates_to_str=True, ignore_nulls = item.doctype in DOCTYPES_FOR_DOCTYPE)
    values = list(d.values())
    columns = []
    new_values = []
    i = 0
    for col in list(d):
        if not(col in ['name', 'idx','owner','_user_tags'
            ,'_comments','_assign','_liked_by','parent','parenttype','parentfield','docstatus'
            ,'creation','modified','modified_by']):
            columns.append(col)
            new_values.append(values[i])
        if col == 'creation' and has_creation:
            columns.append('create_time')
            new_values.append(values[i])
        if col == 'modified' and has_modified:
            columns.append('last_update_time')
            new_values.append(values[i])
        if col == 'modified_by' and has_modified_by:
            columns.append('last_update_by')
            new_values.append(values[i])
        i= i + 1
        
    insert_sql = """INSERT INTO `{tablename}` ({columns})
                VALUES ({values})""".format(
                tablename = table_name,
                columns = ", ".join(["`"+c+"`" for c in columns]),
                values = ", ".join(["%s"] * len(columns))
            )
    try:
        frappe.db.sql(insert_sql, new_values)
    except Exception as e:
        if frappe.db.is_primary_key_violation(e):
            if item.meta.autoname=="hash":
                # hash collision? try again
                frappe.flags.retry_count = (frappe.flags.retry_count or 0) + 1
                if frappe.flags.retry_count > 5 and not frappe.flags.in_test:
                    raise
                item.name = None
                item.db_insert()
                return

            frappe.msgprint(_("{0} {1} already exists").format(item.doctype, frappe.bold(item.name)), title=_("Duplicate Name"), indicator="red")
            raise frappe.DuplicateEntryError(item.doctype, item.name, e)

        elif frappe.db.is_unique_key_violation(e):
            # unique constraint
            item.show_unique_validation_message(e)
        else:
            raise     
    item.set("__islocal", False)

def update_item(table_name, name_field, item, has_creation=False, has_modified=False, has_modified_by=False, primary_keys=[]):
    """Update the document (with valid columns) in the database."""

    if item.get("__islocal") or not item.name:
        db_insert(table_name, name_field, item, has_creation, has_modified, has_modified_by)
        return

    d = item.get_valid_dict(convert_dates_to_str=True, ignore_nulls = item.doctype in DOCTYPES_FOR_DOCTYPE)

    # don't update name, as case might've been changed
    name = d[name_field]
    fixedname_field = get_fixed_name_field(table_name, name_field,primary_keys)
    
    values = list(d.values())
    columns = []
    ignored_columns = ['name', 'idx','owner','_user_tags'
            ,'_comments','_assign','_liked_by','parent','parenttype','parentfield','docstatus'
            ,'creation','modified','modified_by', name_field]
    ignored_columns = ignored_columns + primary_keys
    new_values = []
    i = 0
    for col in list(d):
        if not(col in ignored_columns):
            columns.append(col)
            new_values.append(values[i])
        if col == 'creation' and has_creation:
            columns.append('create_time')
            new_values.append(values[i])
        if col == 'modified' and has_modified:
            columns.append('last_update_time')
            new_values.append(values[i])
        if col == 'modified_by' and has_modified_by:
            columns.append('last_update_by')
            new_values.append(values[i])
        i= i + 1

    update_sql = """UPDATE `{tablename}`
            SET {values} WHERE {name_field}=%s""".format(
                tablename = table_name,
                values = ", ".join(["`"+c+"`=%s" for c in columns]),
                name_field = fixedname_field
            )
    try:
        frappe.db.sql(update_sql, new_values + [name])
    except Exception as e:
        if frappe.db.is_unique_key_violation(e):
            item.show_unique_validation_message(e)
        else:
            raise


def delete_from_table(table_name,name_field, doctype, name, ignore_doctypes, doc, primary_keys=[]):
    """Delete the document from the database."""
    fixedname_field = get_fixed_name_field(table_name, name_field,primary_keys)
    delete_sql="delete from `{0}` where {1}=%s".format(table_name, fixedname_field)
    frappe.db.sql(delete_sql, name)

def fix_int_name(iterable):
	iterable.name = '{0}'.format(iterable.name)
	return iterable

def send_command(nodes,expression,type='B'):
    insert_sql = """insert into sym_data (node_list, table_name, event_type, row_data, trigger_hist_id, channel_id, create_time)
                select '{nodes}', source_table_name, %s, %s, trigger_hist_id, 'config', current_timestamp
                from sym_trigger_hist where source_table_name = 'sym_node' and inactive_time is null""".format(
                nodes = ", ".join(nodes)
            )
    expression = expression.replace('"','\\"')
    expression = '"{0}"'.format(expression)
    try:
        frappe.db.sql(insert_sql, [type,expression])
    except Exception as e:
        raise
    
def send_bench_command(nodes,command):
    bench_template = os.path.join(os.path.dirname(__file__),'..','commands','templates','bench_command.bsh')
    template = load_template(bench_template)
    template = template.replace("{bench_command}",command)
    send_command(nodes,template,type='B')

def load_template(template_path):
    target=""
    with open(template_path, 'r') as source:
            target = target + frappe.as_unicode(
                frappe.utils.cstr(source.read())
            )
    return target
