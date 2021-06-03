------------------------------------------------------------------------------
-- Clear and load SymmetricDS Configuration
------------------------------------------------------------------------------

delete from sym_trigger_router;
delete from sym_trigger
delete from sym_file_trigger_router;
delete from sym_file_trigger;
delete from sym_router;
delete from sym_channel where channel_id in (SELECT LOWER(REPLACE(module_name,' ', '_')) FROM `tabModule Def`);
delete from sym_node_group_link;
delete from sym_node_group;
delete from sym_node_host;
delete from sym_node_identity;
delete from sym_node_security;
delete from sym_node;


------------------------------------------------------------------------------
-- Channels
------------------------------------------------------------------------------

-- Channel channels for tables related to ERPNExt Modules
insert into sym_channel 
(channel_id, processing_order, max_batch_size, enabled, description)
SELECT LOWER(REPLACE(module_name,' ', '_')), ((ROW_NUMBER() OVER (ORDER BY creation)) * 10) + 500000, 100000, 1, module_name FROM `tabModule Def`;

------------------------------------------------------------------------------
-- Node Groups
------------------------------------------------------------------------------

insert into sym_node_group (node_group_id) values ('master');
insert into sym_node_group (node_group_id) values ('backup');

------------------------------------------------------------------------------
-- Node Group Links
------------------------------------------------------------------------------

-- Master sends changes to DR when DR pulls from Master
insert into sym_node_group_link (source_node_group_id, target_node_group_id, data_event_action) values ('master', 'backup', 'W');

-- DR sends changes to Master when DR pushes to Master
insert into sym_node_group_link (source_node_group_id, target_node_group_id, data_event_action) values ('backup', 'master', 'P');

------------------------------------------------------------------------------
-- Triggers
------------------------------------------------------------------------------

-- Triggers for tables on channels
insert into sym_trigger 
(trigger_id,source_table_name,channel_id,last_update_time,create_time)
SELECT CONCAT(LOWER(REPLACE(dt.module,' ', '_')),'_', LOWER(REPLACE(dt.name,' ', '_'))) AS trigger_id, S.table_name as source_table_name
    , LOWER(REPLACE(dt.module,' ', '_')) AS channel_id
    ,current_timestamp,current_timestamp
FROM `tabDocType` as dt
left outer join information_schema.tables as S on (S.table_name = CONCAT('tab', dt.name))
WHERE S.table_name IS NOT NULL and dt.name not in ("Error Log","Error Snapshot","Scheduled Job Log","Scheduled Job Type");

insert into sym_trigger 
(trigger_id,source_table_name,channel_id,last_update_time,create_time)
values ('core_not_listed','tabSeries,__UserSettings','core',current_timestamp,current_timestamp);

insert into sym_trigger 
(trigger_id,source_table_name,channel_id,last_update_time,create_time,`sync_on_insert_condition`, `sync_on_delete_condition`)
values ('core_singles','tabSingles','core',current_timestamp,current_timestamp,
"$(curTriggerValue).doctype NOT IN ('System Settings') and $(curTriggerValue).field NOT IN ('scheduler_last_event','enable_scheduler')",
"$(curTriggerValue).doctype NOT IN ('System Settings') and $(curTriggerValue).field NOT IN ('scheduler_last_event','enable_scheduler')"
 );

UPDATE sym_trigger SET
    excluded_column_names = "api_key, api_secret"
WHERE trigger_id = "core_user";


------------------------------------------------------------------------------
-- Routers
------------------------------------------------------------------------------

-- Default router sends all data from master to dr 
insert into sym_router 
(router_id,source_node_group_id,target_node_group_id,router_type,create_time,last_update_time)
values('master_2_backup', 'master', 'backup', 'default',current_timestamp, current_timestamp);

-- Default router sends all data from dr to master
insert into sym_router 
(router_id,source_node_group_id,target_node_group_id,router_type,create_time,last_update_time)
values('backup_2_master', 'backup', 'master', 'default',current_timestamp, current_timestamp);

------------------------------------------------------------------------------
-- Trigger Routers
------------------------------------------------------------------------------

-- Send all master data to all backups
insert into sym_trigger_router 
(trigger_id,router_id,initial_load_order,last_update_time,create_time)
SELECT st.trigger_id, 'master_2_backup', sc.processing_order * 100 ,current_timestamp, current_timestamp FROM `sym_trigger` as st
left outer join sym_channel as sc on (st.channel_id = sc.channel_id);

-- Send all backup data to master
insert into sym_trigger_router 
(trigger_id,router_id,initial_load_order,last_update_time,create_time)
SELECT st.trigger_id, 'backup_2_master', sc.processing_order * 100 ,current_timestamp, current_timestamp FROM `sym_trigger` as st
left outer join sym_channel as sc on (st.channel_id = sc.channel_id);