import requests
from sc_settings import user, passw, ip
from pprint import pprint

# Use this to debug
# import pdb; pdb.set_trace()

# Ignore the InsecureRequestWarning message:
requests.packages.urllib3.disable_warnings()



base_url = 'https://' + ip + ':9569/srm/'
login_form = base_url + 'j_security_check'

rest_root = base_url + 'REST/api/v1/'
rest_storage_systems = rest_root + 'StorageSystems/'
rest_volumes = rest_root + 'Volumes/'


class RestModule(object):
    """
    Rest Api utils module
    """

    def __init__(self, user, password):
        # user and password to connect to Spectrum Control
        self.username = (user, password)

        # Session open to Spectrum Control
        self.session = requests.Session()

        # Skip the SSL certificate (CA) verification
        self.session.verify = False

        # First login to Spectrum Control for authentication
        self.session.post(login_form, data={'j_username': user, 'j_password': password}, )

    def get_storage_systems(self):
        """ GET all the Storage Systems monitored by Spectrum Control"""

        request = self.session.get(rest_storage_systems)
        if request.status_code != 200:
            print('Unable to open: {}, status code: {}'.format(rest_storage_systems, request.status_code))
            exit(1)

        content_type = request.headers.get('content-type')
        if content_type != 'application/json':
            print('Unsupported Content-Type: {}. We want JSON'.format(content_type))
            exit(1)

        return request.json()

    def show_storage_system(self, storage_name):
        """ GET a specific Storage Systems info from Spectrum Control"""

        request = self.session.get(rest_storage_systems)

        if request.status_code != 200:
            print('Unable to open: {}, status code: {}'.format(rest_storage_systems, request.status_code))
            exit(1)

        content_type = request.headers.get('content-type')
        if content_type != 'application/json':
            print('Unsupported Content-Type: {}. We want JSON'.format(content_type))
            exit(1)

        stoarage_systems = request.json()
        for sys in stoarage_systems:
            if sys['Name'] == storage_name:
                return sys

    def get_storage_system_volumes(self, storage_name):
        """ GET all the Volumes which belongs to a Storage Systems """

        request = self.session.get(rest_storage_systems)
        if request.status_code != 200:
            print('Unable to open: {}, status code: {}'.format(rest_storage_systems, request.status_code))
            exit(1)

        content_type = request.headers.get('content-type')
        if content_type != 'application/json':
            print('Unsupported Content-Type: {}. We want JSON'.format(content_type))
            exit(1)

        stoarage_systems = request.json()
        for sys in stoarage_systems:
            if sys['Name'] == storage_name:
                id = sys['id']

        rest_volumes = rest_storage_systems + id + '/Volumes/'
        request = self.session.get(rest_volumes)
        if request.status_code != 200:
            print('Unable to open: {}, status code: {}'.format(rest_volumes, request.status_code))
            exit(1)

        content_type = request.headers.get('content-type')
        if content_type != 'application/json':
            print('Unsupported Content-Type: {}. We want JSON'.format(content_type))
            exit(1)

        return request.json()

    def get_volumes(self):
        """ GET all the Volumes monitored by Spectrum Control"""

        request = self.session.get(rest_volumes)
        if request.status_code != 200:
            print('Unable to open: {}, status code: {}'.format(rest_storage_systems, request.status_code))
            exit(1)

        content_type = request.headers.get('content-type')
        if content_type != 'application/json':
            print('Unsupported Content-Type: {}. We want JSON'.format(content_type))
            exit(1)

        return request.json()

    def show_volume_uid(self, uid):
        """ GET one or more volumes wich meet a criteria from Spectrum Control"""

        request = self.session.get(rest_volumes)

        if request.status_code != 200:
            print('Unable to open: {}, status code: {}'.format(rest_volumes, request.status_code))
            exit(1)

        content_type = request.headers.get('content-type')
        if content_type != 'application/json':
            print('Unsupported Content-Type: {}. We want JSON'.format(content_type))
            exit(1)

        volumes = request.json()
        for vol in volumes:
            if vol['Volume Unique ID'].lower() == uid.lower():
                return vol

    def show_volume_name(self, name):
        """ GET one or more volumes wich meet a criteria from Spectrum Control"""

        request = self.session.get(rest_volumes)

        if request.status_code != 200:
            print('Unable to open: {}, status code: {}'.format(rest_volumes, request.status_code))
            exit(1)

        content_type = request.headers.get('content-type')
        if content_type != 'application/json':
            print('Unsupported Content-Type: {}. We want JSON'.format(content_type))
            exit(1)

        volumes = request.json()
        for vol in volumes:
            if vol['Name'].lower() == name.lower():
                return vol



# usage
connection = RestModule(user, passw)
# storage_name = input('Storage name: ')
# stoarage_system = connection.show_storage_system(storage_name)
# volumes = connection.get_storage_system_volumes(storage_name)
# pprint(stoarage_system)
# pprint(volumes)

# uid = input('Volume UID: ')
# volume = connection.show_volume_uid(uid)
# pprint(volume)

name = input('Volume UID: ')
volume = connection.show_volume_name(name)
pprint(volume)


