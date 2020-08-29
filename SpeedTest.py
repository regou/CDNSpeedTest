import time
import requests
from forcediphttpsadapter.adapters import ForcedIPHTTPSAdapter

requests.packages.urllib3.disable_warnings()


class SpeedTest:
    def __init__(self, ip):
        self.testIp = ip
        self.speed = 0
        self.testTime = 10
        self.bootTime = 2.5  # 到满速度的时间可能要2秒

    connect_timeout = 3

    url = {
        'protocol': "https:",
        'host': "apple.freecdn.workers.dev",
        'path': "/105/media/us/iphone-11-pro/2019/3bd902e4-0752-4ac1-95f8-6225c32aec6d/films/product/iphone-11-pro"
                "-product-tpl-cc-us-2019_1280x720h.mp4"
    }

    def start(self):
        return

    def init(self):
        with requests.Session() as session:
            session = requests.Session()
            prefix = f"{self.url['protocol']}//{self.url['host']}"
            session.mount(prefix=prefix, adapter=ForcedIPHTTPSAdapter(dest_ip=self.testIp))

            def real_start():
                return session.get(
                    f"{prefix}{self.url['path']}",
                    headers={'Host': self.url['host']},
                    verify=False, stream=True,
                    timeout=(3, self.testTime + self.bootTime + 5)
                )

            setattr(self, 'start', real_start)

    def test(self):
        r = self.start()
        end_time = time.time() + self.testTime + self.bootTime
        final_size = 0
        block_size = 1024  # 1k
        n_chunk = 1
        # file_size = int(r.headers.get('Content-Length', None))
        # file_size = 70000
        # num_bars = np.ceil(file_size / (n_chunk * block_size))
        # bar = progressbar.ProgressBar(maxval=num_bars).start()
        for i, chunk in enumerate(r.iter_content(chunk_size=n_chunk * block_size)):
            if time.time() <= end_time:
                final_size = i
                # bar.update(i + 1)
            else:
                final_size = i
                break

        # bar.finish();
        self.speed = (final_size / 1024) / self.testTime  # xM/s

    def result2string(self):
        return f"{self.speed}Mb/s"
