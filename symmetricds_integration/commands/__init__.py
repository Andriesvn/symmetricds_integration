from __future__ import unicode_literals, absolute_import, print_function
import click
import frappe, os, sys, importlib, inspect, json
import frappe.utils
from frappe import _
from frappe.utils import cint
from frappe.commands import pass_context, get_site
from frappe.exceptions import SiteNotSpecifiedError


def call_command(cmd, context):
	return click.Context(cmd, obj=context).forward(cmd)

@click.command('create-sym-tables')
@click.option('--engine-name', help='Engine Name')
@pass_context
def create_sym_tables(context, engine_name):
    bin_dir = os.path.join(os.path.dirname(__file__),'..','..','symmetric_server','bin')
    print('bin Directory = ',bin_dir)
    frappe.commands.popen('{0}/symadmin --engine {1} create-sym-tables'.format(bin_dir, engine_name))


@click.command('uninstall-symmetric')
@click.option('--engine-name', help='Engine Name')
@pass_context
def uninstall_sym(context, engine_name):
    bin_dir = os.path.join(os.path.dirname(__file__),'..','..','symmetric_server','bin')
    print('bin Directory = ',bin_dir)
    frappe.commands.popen('{0}/symadmin --engine {1} uninstall'.format(bin_dir, engine_name))


@click.command('make-sds-config')
@click.option('--engine-name', help='Engine Name')
@click.option('--group-id', help='Node Group ID')
@click.option('--external-id', help='External id')
@click.option('--registration-url', help='Registration Url')
@click.option('--is-master', default=False, is_flag=True, help="Is Master")
@click.option('--secure', default=False, is_flag=True, help="Use HTTPS")
@pass_context
def make_sds_config(context, engine_name, group_id, external_id, registration_url,
    is_master=False,secure=False ):
    sites_path = os.path.join(frappe.utils.get_bench_path(), 'sites')
    site_path = context.sites[0]
    apps_path = os.path.join(frappe.utils.get_bench_path(), 'apps')
    properties_template = os.path.join(os.path.dirname(__file__),'templates','sync_template.properties')
    engine_dir = os.path.join(os.path.dirname(__file__),'..','..','symmetric_server','engines')
    bin_dir = os.path.join(os.path.dirname(__file__),'..','..','symmetric_server','bin')

    if not(os.path.exists(engine_dir)):
        os.mkdir(engine_dir)
	
    frappe.commands.popen('chmod +x {0}/*'.format(bin_dir, engine_name))

    print('site_path=', "{0}/{1}".format(sites_path, site_path))
    print('apps_path=',apps_path)
    configuration = frappe.get_site_config(sites_path=sites_path, site_path=site_path)
    print('Configuration=', configuration)
    if site_path:
        site_config = os.path.join(sites_path, site_path, "{0}.properties".format(engine_name))
        print('Config Path:',site_config)

    print('dirname:', properties_template)

    sync_url = "://localhost:31415/sync/{0}".format(engine_name)

    if (secure):
        sync_url = "https{0}".format(sync_url)
    else :
        sync_url = "http{0}".format(sync_url)
    
    with open(site_config, 'w') as target:
        with open(properties_template, 'r') as source:
            target.write(frappe.as_unicode(
                frappe.utils.cstr(source.read()).format(
                    engine_name=engine_name,
					driver='org.mariadb.jdbc.Driver' if configuration.db_type=="mariadb" else "",
					db_url="jdbc:{0}://{1}:3306/{2}".format(configuration.db_type, configuration.db_host, configuration.db_name),
					db_user=configuration.db_name,
					db_password=configuration.db_password,
					register_url=registration_url if not(is_master) else "",
                    sync_url=sync_url if is_master else "",
					group_id=group_id,
                    external_id= external_id,
                    http_enable=str(not(secure)).lower(),
                    https_enable=str(secure).lower())
                )
            )

    if os.path.exists(os.path.join(engine_dir,"{0}.properties".format(engine_name))):
        os.remove(os.path.join(engine_dir,"{0}.properties".format(engine_name)))
    os.symlink(site_config, os.path.join(engine_dir,"{0}.properties".format(engine_name)), False)

@click.command('grant-user-priv')
@click.option('--db-root-user', help='Database Root User')
@click.option('--db-root-password', help='Database Root Password')
@click.option('--no-mariadb-socket', is_flag=True, default=False, help='Set MariaDB host to % and use TCP/IP Socket instead of using the UNIX Socket')
@pass_context
def grant_user_priv(context, db_root_user, db_root_password, no_mariadb_socket=False):
    if not context.sites:
        raise SiteNotSpecifiedError

    sites_path = os.path.join(frappe.utils.get_bench_path(), 'sites')
    site_path = context.sites[0]

    frappe.init(site=site_path)

    configuration = frappe.get_site_config(sites_path=sites_path, site_path=site_path)

    db_type = frappe.conf.db_type if frappe.conf else configuration.db_type
    db_type = db_type or 'mariadb'
    frappe.flags.root_login = db_root_user
    frappe.flags.root_password = db_root_password
    db_name = configuration.db_name
    root_conn = get_root_connection(frappe.flags.root_login, frappe.flags.root_password)
    
    grant_all_privileges(root_conn,db_name,db_name)
    if no_mariadb_socket:
        grant_all_privileges(root_conn, db_name, db_name, host="%")
    
    flush_privileges(root_conn)
    root_conn.close()



def get_root_connection(root_login, root_password):
	import getpass
	if not frappe.local.flags.root_connection:
		if not root_login:
			root_login = 'root'

		if not root_password:
			root_password = frappe.conf.get("root_password") or None

		if not root_password:
			root_password = getpass.getpass("MySQL root password: ")

		frappe.local.flags.root_connection = frappe.database.get_db(user=root_login, password=root_password)

	return frappe.local.flags.root_connection

def grant_all_privileges(db_connection, target, user, host=None):
		if not host:
			host = get_current_host(db_connection)
		db_connection.sql("GRANT SUPER ON *.* TO '%s'@'%s';" % (user, host))
		db_connection.sql("GRANT PROCESS ON *.* TO '%s'@'%s' REQUIRE NONE WITH MAX_QUERIES_PER_HOUR 0 MAX_CONNECTIONS_PER_HOUR 0 MAX_UPDATES_PER_HOUR 0 MAX_USER_CONNECTIONS 0;" % (user, host))
		print("Super and Process granted to '%s'@'%s'" % (user, host))

def flush_privileges(db_connection):
		db_connection.sql("FLUSH PRIVILEGES")

def get_current_host(db_connection):
		return db_connection.sql("select user()")[0][0].split('@')[1]








commands = [
	make_sds_config,
    create_sym_tables,
    grant_user_priv
]
