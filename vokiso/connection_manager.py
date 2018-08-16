from time import sleep

import ipgetter
from py2p import mesh
from threading import Event, Thread, Lock


class DirectConnection:
    def __init__(self):
        import miniupnpc

        print('Finding router ip...')
        upnp = miniupnpc.UPnP()
        upnp.discoverdelay = 10
        upnp.discover()
        upnp.selectigd()

        local_host = upnp.lanaddr
        external_host = ipgetter.myip()

        local_port = 4455
        external_port = 43210

        while True:
            upnp.addportmapping(external_port, 'TCP', local_host, local_port, 'Vokiso', '')
            try:
                self.sock = mesh.MeshSocket(
                    local_host, local_port, out_addr=(external_host, external_port)
                )
            except OSError:
                local_port += 1
                external_port += 1
                continue
            print('Listening on {}:{}...'.format(local_host, local_port))
            print('Also listening on {}:{}...'.format(external_host, external_port))
            break

        self.connected_event = Event()
        self.sock.once('connect')(lambda sock: self.connected_event.set())
        self.send_lock = Lock()

    def connect(self, ip, port):
        self.sock.connect(ip, port)
        self.wait()

    def wait(self):
        self.connected_event.wait()
        sleep(0.5)
        assert self.sock.routing_table

    def start(self, on_message):
        Thread(target=self._process_messages, daemon=True, args=[on_message]).start()

    def send(self, message):
        with self.send_lock:
            self.sock.send(message)

    def _process_messages(self, on_message):
        while True:
            msg = self.sock.recv()
            if not msg:
                sleep(0.1)
                continue
            on_message(msg.packets[-1])
