# SymmetricDS Integration For Frappe v13

The aim of this project is to Integrate [SymmetricDS](https://github.com/JumpMind/symmetric-ds) into the [Frappe Framework](https://github.com/frappe/frappe). This allows the Frappe database to be replicated accross multiple servers, Not just on a "FULL Server" basis but eventualy on a "Per Company" Basis as well.

The end goal we would like to achieve is to be able to setup a Master Cloud Server that hosts multiple companies and have Branch Servers replicate ONLY That company`s data back to the Master Server creating a Hybrid Cloud Based Setup capable of Running Offline.

**PLEASE BE AWARE THAT THIS PROJECT IS STILL IN BETA. ALTHOUGH IT IS BEING USED IN PRODUCTION, THE ACTUAL INTEGRATION IS NOT COMPLETE AND YOU MIGHT NEED TO FIX REPLICATION ISSUES MANUALY THROUGH THE DATABASE ITSELF. That being said, Be familiar with the [SymmetricDS Documentation](https://www.symmetricds.org/doc/3.12/html/user-guide.html)**

ALSO UNTIL VIRTUAL DOCTYPES ARE PROPERLY WORKING FRAPPE v13 YOU NEED TO APPLY THE FOLLOWING FIXES MANUALY IN FRAPPE
https://github.com/frappe/frappe/issues/13321
https://github.com/frappe/frappe/pull/13319/commits/d54ecd42237d61857302db296324e37babd7b1d0
https://github.com/frappe/frappe/pull/13304/commits/baf4259596dadf8609103686a4dc3536da823434

## Current Features
1. Create and Link Engines to a Frappe Site
1. Basic Frappe Bench Commands to Setup Replication
1. Basic GUI for Managing Symmetric DS Based on Virtual Doctypes
1. Sending Bench Commands to a Node (Still in its Infancy)
1. Only Full Bidirectional Replication Supported at the moment

## Planned Features
1. Full Setup of Replication Through Frappe Instalation
    - Standardise Settings per Site (Engine Name, URL`s, etc)
    - Generate Engine Template on App Instalation
    - Create Tables on App Instalation
    - Fix Permisions on App Instalation
    - Create Reload Requests for only Modified Tables on any Schema Changes
    - Set all nodes to maintenance mode during any Schema Changes
1. Create Standard Channels and Triggers based on Frappe`s Structure (Esspecialy for ERPNext)
    - Triggers need to be created correctly on a per document basis to filter data PER Company. (Child Doctypes are currently a problem)
    - Create Initial Load Scripts to Only Load Specific Company`s Data on Registration or Reload
1. Allow Frappe Framework to know of Replication and monitor and make use of it
    - Integrate into Frappe the Current NodeID, whether or not its master or client, is replication service running or not
    - Integrate into SymmetricDS the means of allowing Triggers, Jobs, Monitors, Notifications, Data, etc to access the frappe framework
1. Implement File Syncronisation to Sync Site Files as well as Apps
    - Currently SymmetricDS File Sync is not implemented but is available.
    - Create Triggers for Syncing Files and Apps

### Pre-requisites
SymmetricDS uses Java 8 or higher so you will need to install jre 8 or above on Both client and server

On the frappe docker image you can do this by
```
sudo apt-get update
sudo apt-get install openjdk-11-jre
```

Versions do not need to match on all nodes as long as its there.

### Installation
Installing the App is pretty Simple on client and server
```
bench get-app symmetricds_integration https://github.com/Andriesvn/symmetricds_integration.git
```
Then add it to the site|s 
```
bench --site site_name install-app symmetricds_integration
```

### Master Server Setup
Setting things up on the master server is the hardest part.

First we need to create a engine properties file for SymmetricDS
```
bench --site site_name make-sds-config --engine-name engine_name --group-id group_id --external-id external_id --is-master
```
This will create a {engine_name}-{external_id}.properties file inside your sites main directory and symlink it to the servers engine directory.

It will use the database info (database name, username and password) contained inside your site_config file
It will also generate a deafult sync_url of http://localhost:31415/sync/{engine_name}-{external_id} for your server witch will need to be changed if you are not in development

Next we will need to greate all the sym tables for your engine
```
bench --site site_name create-sym-tables --engine-name engine_name
```
Then we need to fix the database user permisions as they need SUPER and PROCESS permisions
```
bench --site site_name grant-user-priv --db-root-user root --db-root-password password
```
You can add the --no-mariadb-socket option as needed

Your server is now runable and can be started either by service or directly in console.
From your bench directory you can run
```
sudo apps/symmetricds_integration/symmetric_server/bin/sym
```
To start it by console or
```
sudo apps/symmetricds_integration/symmetric_server/bin/sym_service install
sudo apps/symmetricds_integration/symmetric_server/bin/sym_service start
```
To start it by service

Although it can now run, No replication is actualy configured yet. You can read up on how its done using the [SymmetricDS Documentation](https://www.symmetricds.org/doc/3.12/html/user-guide.html).

To Setup a Full Server to Server Bidirectional Replication (NO Sub Filtering yet), you can excecute the SQL statement found under the [symmetricds_integration/symmetric_server/samples/insert_sample.sql](https://github.com/Andriesvn/symmetricds_integration/blob/644d775cbb22ae06e50cad9948383018bfcc1764/symmetric_server/samples/insert_sample.sql) inside your Master server`s Site Database while Symmerticds is NOT running.

Remember to replace the Node group Names "master" and "backup" with those you wish to use for your master and client.
This will create all channels, triggers, links and 2 node groups needed for full bidirectional replication based on your modules and doctypes currently in the database.
```
apps/symmetricds_integration/symmetric_server/bin/dbimport --engine engine_name apps/symmetricds_integration/symmetric_server/samples/insert_sample.sql
```

This will be implemented to be created on setup in future


### Client Server Setup

Starting from a clean setup, install all apps that are installed on the server, (Same versions) including the symmetricds_integration app.

Create a new site and install all apps on it. the server sitename and client site name does NOT need to match.

Then create the engine properties file for SymmetricDS for a client setup
```
bench --site site_name make-sds-config --engine-name engine_name --group-id group_id --external-id external_id --registration-url [the sync url as shown in your servers properties file]
```
Remember to use the Sync URL as its shown in your servers properties file and the group_id you chose for the client.

Then we need to fix the database user permisions as they need SUPER and PROCESS permisions
```
bench --site site_name grant-user-priv --db-root-user root --db-root-password password
```
**VERY IMPORTANT THING TO REMEMBER HOWEVER... the scheduler must remain disabled on the client at all times!**
```
bench config set-common-config -c pause_scheduler 1
bench config set-common-config -c disable_scheduler 1
bench set-config -g pause_scheduler 1
bench set-config -g disable_scheduler 1
bench --site all set-config pause_scheduler 1
```
Sometimes Pausing it alone does not work... Might look like overkill but its the only way i found of making sure it stays off!

You do NOT need to start the site or do the initial setup on the client.

Your now ready to sync. All you do now is start the SymmetricDS server either in console or by service.
By default, auto registration and auto reload are enabled on the server so once sync is started the client will auto register and the server will automatically schedule a reload for the newly created node. This will clear the current database and download the structure and data from the server.

No files fill be sync unfortunately and you can expect Uploaded files in Frappe not to be either. 

You will need to unfortunately Rsync all of the files manualy at this point.


### Migrating or applying Changes
Unfortunately Changing the schema is not that easy with replication enabled. Although SymmetricDS Syncs database schema changes, It needs to be informed of them first.

Best way i have found to apply changes to replicating nodes is as follows.

First of all put ALL your nodes into Maintenance Mode to prevent any further changes to data.
```
bench set-maintenance-mode on
```
Once all of them are in maintenance-mode you can kill the SymmetricDS on the Server. Depending on how you ran it Ctrl + C in console or as a service:
```
apps/symmetricds_integration/symmetric_server/bin/sym_service stop 
```
Then apply your changes on the server as usual example 
```
bench update
```
Also apply all changes to the app files on all the clients (only file changes. Dont run migrations)
```
bench update --pull
```
Here comes the tricky part for now. Once schema changes happen on the server, SymmetricDS will try to pic them up on startup, however, this is not garenteed to work. So If you know what schema changes occured you can schedule them for reload manualy for nodes witch works best.

First we tell SymmetricDS to try to see if it can pic it up. 
```
sudo apps/symmetricds_integration/symmetric_server/bin/symadmin sync-triggers
```
Next, if we know what changed we can tell it to send specific tables that changed to the clients
```
sudo apps/symmetricds_integration/symmetric_server/bin/symadmin send-schema --node-group your_clients_nodegroup_id the_table_that_changed
```
or you can send a specific SQL over
```
sudo apps/symmetricds_integration/symmetric_server/bin/symadmin send-sql --node-group your_clients_nodegroup_id the_table_that_changed "alter table the_table_that_changed add newcolumn varchar(100)"
```
Once its done you can start the SymmetricDS server once more and hopefully all clients are synced correctly. IF NOT you will need to force a reload on them which means deleting the entire database and redownloading it FOR EACH CLIENT:
```
sudo apps/symmetricds_integration/symmetric_server/bin/symadmin reload-node your_node_id
```
Once its done you can get all of them out of maintenance mode
```
bench set-maintenance-mode off
```
### Sending Bench commands to clients
To make this process a bit easyer, You are able to send Bench commands to nodes in the Node Doctype Form. For now its per node but busy working on making it per node group.

Sending a bench command from the interface to a specific node sends it via sync so sync must still be running.
when sending it from the interface just include everything after the bench command. Example if you intend on sending:
```
bench set-maintenance-mode off
```
The command should be entered as
```
set-maintenance-mode off
```
It will be run as sudo on the client as SymmetricDS needs sudo permisions. Result on client
```
sudo bench set-maintenance-mode off
```
Output will be logged on the client`s symmetricds log.

#### License

GPLv3
