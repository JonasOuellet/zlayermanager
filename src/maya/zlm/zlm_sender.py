from multiprocessing.connection import Listener, Client

from zlm.zlm_settings import ZlmSettings


def send_command(cmd_name, settings=None, *args):
    if settings is None:
        settings = ZlmSettings()

    cmd_args = [cmd_name]
    cmd_args.extend(args)

    client = Client(('localhost', settings.communication_port), authkey='secret')
    client.send(cmd_args)
    client.close()
