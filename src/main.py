import random,time
from pathlib import Path
from ipaddress import IPv6Network, IPv6Address
from src.SpeedTest import SpeedTest
from progressbar import ProgressBar
from pandas import DataFrame
import pydash as _
import config_with_yaml
config = config_with_yaml.load("config.yml")
seed_num = config.getPropertyWithDefault('seed_num', 10)
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
columns=['ip', 'Speed(Mb/s)']
df = DataFrame([], columns=columns)


def run_with_progress(st, index):
    global df
    bar.update(index)
    try:
        st.test()
    except Exception:
        pass
    df = df.append(
        DataFrame([[st.testIp, st.speed]], columns=columns),
        ignore_index=True
    )
    time.sleep(0.005)


_.for_each(speed_tests, run_with_progress)

df.to_csv('./result_v6.csv', index_label='index', encoding='utf-8')
