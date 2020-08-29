import random, time
from pathlib import Path
from ipaddress import IPv6Network, IPv6Address
from SpeedTest import SpeedTest
from progressbar import ProgressBar
import pydash as _
import csv
import config_with_yaml

config = config_with_yaml.load(Path("config.yml"))
seed_num = config.getPropertyWithDefault('number_of_random_ips', 10)
speed_tests = []

from_txt_path = Path(config.getPropertyWithDefault('ip_ranges_file', './ipv6.txt'))
SpeedTest.connect_timeout = config.getPropertyWithDefault('connect_timeout', 1)
SpeedTest.url['protocol'] = config.getPropertyWithDefault('test_url.protocol', 'https:')
SpeedTest.url['host'] = config.getProperty('test_url.host')
SpeedTest.url['path'] = config.getProperty('test_url.path')

with open(from_txt_path, 'r') as f:
    subnets = _.map_(f.readlines(), lambda l: l.strip())

networks = _.map_(subnets, lambda subnet: IPv6Network(subnet))

# seed_num = min(seed_num, len(networks))

for x in range(seed_num):
    network = _.sample(networks)
    if network.max_prefixlen - network.prefixlen == 0:
        ip = IPv6Address(network.network_address)
    else:
        ip = IPv6Address(network.network_address + random.getrandbits(network.max_prefixlen - network.prefixlen))

    st = SpeedTest(str(ip))
    st.init()
    speed_tests.append(st)

bar = ProgressBar(max_value=len(speed_tests))
columns = ['ip', 'When', 'Speed(Mb/s)']

data = []
def run_with_progress(st, index):
    global df
    bar.update(index)
    try:
        st.test()
    except Exception:
        pass
    data.append([st.testIp, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(st.startTime)), st.speed])
    time.sleep(0.005)


_.for_each(speed_tests, run_with_progress)


has_header = False
try:
    with open('result.csv', mode='r', newline='') as csvfile:
        if csv.Sniffer().has_header(csvfile.read(1024)):
            has_header = True
except Exception:
    pass

with open('result.csv', 'a', newline='') as csvfile:
    fieldnames = columns
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    if not has_header:
        writer.writeheader()

    _.for_each(data, lambda row: writer.writerow({
        fieldnames[0]: row[0],
        fieldnames[1]: row[1],
        fieldnames[2]: row[2]
    }))

