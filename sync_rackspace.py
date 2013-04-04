from ConfigParser import SafeConfigParser
import requests
import json
import pprint

# set up parser for configuration file
parser = SafeConfigParser()
parser.read('connect.cfg')
print parser.get('rackspace', 'username')

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

# will need pass the token in for each request using the X-Auth-Token header
headers = {'X-Auth-Token':token}
r = requests.get(url, headers=headers)
print r.text




