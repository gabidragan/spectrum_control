import requests
from sc_settings import user, passw, ip
from pprint import pprint
import arrow

# Use this to debug
# import pdb; pdb.set_trace()

# Ignore the InsecureRequestWarning message:
requests.packages.urllib3.disable_warnings()


def one_week_ago():
    return arrow.utcnow().shift(weeks=-1).format('X')


def one_day_ago():
    return arrow.utcnow().shift(days=-1).format('X')


def one_hour_ago():
    return arrow.utcnow().shift(hours=-1).format('X')


base_url = 'https://' + ip + ':9569/srm/'
login_form = base_url + 'j_security_check'

rest_root = base_url + 'REST/api/v1/'
rest_storage_systems = rest_root + 'StorageSystems/'
rest_volumes = rest_root + 'Volumes/'
rest_pools = rest_root + 'Pools/'


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

    def request(self, url):
        """ Start a session on Spectrum Control and check the return code and JSON format"""

        request = self.session.get(url)
        if request.status_code != 200:
            print('Unable to open: {}, status code: {}'.format(url, request.status_code))
            exit(1)

        content_type = request.headers.get('content-type')
        if content_type != 'application/json':
            print('Unsupported Content-Type: {}. We want JSON'.format(content_type))
            exit(1)

        return request.json()

    def get_storage_systems(self):
        """ GET all the Storage Systems monitored by Spectrum Control"""

        data = self.request(rest_storage_systems)
        return data

    def show_storage_system(self, storage_name):
        """ GET a specific Storage Systems info from Spectrum Control"""

        stoarage_systems = self.request(rest_storage_systems)
        for sys in stoarage_systems:
            if sys['Name'] == storage_name:
                return sys

    def get_storage_system_id(self, storage_name):
        """ GET the storage system ID which belongs to a Storage Systems """

        # Get the id of the Storage System
        storage_systems = self.request(rest_storage_systems)
        for sys in storage_systems:
            if sys['Name'] == storage_name:
                return sys['id']

    def get_storage_system_volumes(self, id):

        # Build URL in /StorageSystems/<id>/Volumes format
        rest_volumes_storage = rest_storage_systems \
                       + id \
                       + '/Volumes/'
        print(rest_volumes_storage)

        vols = self.request(rest_volumes_storage)
        pprint(vols)
        return vols

    def get_volumes(self):
        """ GET all the Volumes monitored by Spectrum Control"""

        data = self.request(rest_volumes)
        return data

    def show_volume_by_uid(self, uid):
        """ GET the volume with specific UID from Spectrum Control"""

        volumes = self.request(rest_volumes)
        for vol in volumes:
            if vol['Volume Unique ID'].lower() == uid.lower():
                return vol

    def show_volume_by_name(self, name):
        """ GET the fist volume with specific name from Spectrum Control"""

        volumes = self.request(rest_volumes)
        for vol in volumes:
            if vol['Name'] == name:
                return vol

    def show_pool_by_name(self, name):
        """ GET the first pool with specific name from Spectrum Control"""

        pools = self.request(rest_pools)
        for pool in pools:
            if pool['Name'] == name:
                return pool

    def show_volume_performance(self,
                                storage_system,
                                volume_name,
                                granularity="daily",
                                period=one_hour_ago):
        """ GET the Read and Write IOs of a volume from Spectrum Control"""

        # Build URL in the following format:
        # /StorageSystems/<Storage_ID>/Volumes/Performance?
        #                                      &metrics=<metric_ids>
        #                                      &granularity=(sample | hourly | daily | monthly)
        #                                      &startTime=<start_time>
        rest_volume_performance = rest_storage_systems \
                                  + storage_system \
                                  + '/Volumes/Performance?metrics=803,806&granularity=' \
                                  + granularity \
                                  + '&startTime=' \
                                  + period() \
                                  + str('000')

        performance = self.request(rest_volume_performance)
        output = []
        for perf in performance[1:]:
            if f'{volume_name}<br /> ' in perf['deviceName']:
                output.append(perf)
        return output

    def get_perf(self):
        url = "https://212.113.90.56:9569/srm/REST/api/v1/StorageSystems/2031697/Volumes/Performance?metrics=806&startTime=1543930708000&metrics=sample"
        return self.request(url)


def check_activity(performance):
    """ Check if a volume performance shows any activity """

    activity = "Inactive"
    for perf in performance:
        if perf['maxValue'] > 0:
            activity = "Active"
    return activity


def print_volume(volume):
    """ Print out summary of a volume"""

    print(f'{volume["Name"]} '
          f'{volume["I/O Group"]} '
          f'{volume["Pool"]} '
          f'{volume["Capacity"]}GiB '
          f'{volume["Volume Unique ID"]} '
           )
    return None


def show_vdisk_activity(name):
    """
    This function is checking if a volume has activity in the past hour.
    The function returns "Active" or "Inactive"
    """

    connection = RestModule(user, passw)
    volume = connection.show_volume_by_name(name)
    print_volume(volume)
    stg_sys = connection.show_storage_system(volume['Storage System'])
    performance = connection.show_volume_performance(stg_sys['id'], volume['Name'], 'sample')
    return check_activity(performance)


### Usage:

# uid = input('Volume UID: ')
# volume = connection.show_volume_uid(uid)
# pprint(volume)

#########################################

# name = input('Volume Name: ')
# volume = connection.show_volume_name(name)
# print(f'The volume {volume['Name']} belongs to {volume['Storage System']}.')
# pprint(volume)
#
# stg_sys = connection.show_storage_system(volume['Storage System'])
# print('Storage-ul {} are ID=ul {}.'.format(volume['Storage System'], stg_sys['id']))
# performance = connection.show_volume_performance(stg_sys['id'], volume['Name'], 'sample')
#
# pprint(performance)
#

#########################################

# name = input('Volume Name: ')
# print(show_vdisk_activity(name))


