import requests
import json
import sys
import shutil
from ConfigParser import SafeConfigParser

# set up parser for configuration file
parser = SafeConfigParser()
parser.read('connect.cfg')

# authenticate to get access to Rackspace Cloud Services
# issue authentication request to Rackspace Cloud Identity Services
# to get token, for US account: https://identity.api.rackspacecloud.com/v2.0/tokens
# version 2.0 points to version of Cloud Auth API
# will return a token and a service catalog of services avail to this token
# token expires after 24 hours so generate it once a day
# see here for First Gen Cloud Server Auth doc:
# -> http://docs.rackspace.com/servers/api/v1.0/cs-devguide/content/auth.html
# and here for NextGen:
# -> http://docs.rackspace.com/servers/api/v2/cs-gettingstarted/content/section_gs_auth.html
url = 'https://identity.api.rackspacecloud.com/v2.0/tokens'
account_info = {'username':parser.get('rackspace', 'username'),
                'apiKey':parser.get('rackspace', 'api_key')}
payload = {"auth":{"RAX-KSKEY:apiKeyCredentials":account_info}}
headers = {'content-type': 'application/json'}
r = requests.post(url, data=json.dumps(payload), headers=headers)

# get the data: parse authentication response to get token and
# account number = tenant ID
result = r.json()
token = result['access']['token']['id']
account_id = result['access']['token']['tenant']['id']
print "token: {0}".format(token)
print "tenant_id: {0}".format(account_id)

# build the url to get list of servers
if parser.get('rackspace', 'api_version') == '1':
    url = 'https://servers.api.rackspacecloud.com/v1.0/{0}/servers/detail'.format(account_id)
elif parser.get('rackspace', 'api_version') == '2':
    url = 'https://dfw.servers.api.rackspacecloud.com/v2/{0}/servers/detail'.format(account_id)
else:
    print "Please specify if script should use Rackspace API version 1 or version 2 in config file."
    sys.exit()

# will need pass the token in for each request using the X-Auth-Token header
headers = {'X-Auth-Token':token}
r = requests.get(url, headers=headers)

# get the list of servers
result = r.json()
active_servers = {}

servers = result['servers']
print "servers are: {0}".format(servers)
for server in servers:
    server_name = server['name']
    print "server name: {0}".format(server_name)
    server_public_ip = server['addresses']['public']
    print "server public ip: {0}".format(server_public_ip)
    active_servers[server_name] = server_public_ip

print "active servers: {0}".format(active_servers)

# update local /etc/hosts file
# make working copy of /etc/hosts file
shutil.copy2('test_file', 'working_file')

# open copy of /etc/hosts for processing
with open('working_file', 'rb') as f:
    # generate working hosts file
    with open('updated_file', 'wb') as g:
        for line in f:
            if '# user-defined' in line:
                server_ip_address, server_domain_name, comment = line.split(' ', 2)

                # use server / domain name + latest ip address from rackspace
                if server_domain_name in active_servers:
                    #print "server domain name: {0}".format(server_domain_name)
                    for s_ip_address in active_servers[server_domain_name]:
                        g.write('{0} {1} # user-defined \n'.format(server_ip_address,
                            server_domain_name))
                        print "updated: {0}".format(server_domain_name)
                    del active_servers[server_domain_name]
            else:
                # other entries in hosts file, pass through un-molested
                g.write(line)

        # write new servers to working hosts file
        for server_domain_name, server_ip_addresses in active_servers.items():
            for server_ip_address in server_ip_addresses:
                g.write('{0} {1} # user-defined \n'.format(server_ip_address, server_domain_name))

# move updated hosts file into place
# shutil.copy2('updated_file', '/etc/hosts')



