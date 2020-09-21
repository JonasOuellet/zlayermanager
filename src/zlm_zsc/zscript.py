import zlm_settings

_CURRENT_ZSCRIPT = None

_COMMANDS = {}


class ZScript(object):
    def __init__(self, output_file=None, show_actions=False, freeze=True):
        if output_file is None:
            output_file = zlm_settings.SCRIPT_PATH

        self.file_path = output_file

        self.show_actions = show_actions
        self.freeze = freeze

        self.command_execution = []
        self.command_type = set()

    def add(self, command, *args, **kwargs):
        self.command_execution.append((command, args, kwargs))
        name = command.__class__.__name__
        if name not in self.command_type:
            self.command_type.add(name)

    def start(self):
        global _CURRENT_ZSCRIPT
        _CURRENT_ZSCRIPT = self

    def end(self):
        global _CURRENT_ZSCRIPT
        _CURRENT_ZSCRIPT = None

        self.write_to_file(self.file_path)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.end()

    def write_to_file(self, file):
        with open(file, mode='w') as f:
            self.write_code(f)

    def _write_dep(self, cmd_name, defined, fp):
        cmd = _COMMANDS[cmd_name]
        for dep_cmd_name in cmd.dependencies:
            self._write_dep(dep_cmd_name, defined, fp)

        if cmd._definition and cmd_name not in defined:
            fp.write(cmd._definition)
            fp.write('\n')

        defined.add(cmd_name)

    def write_code(self, fp):
        # write command definition if needed
        definined_cmd = set()
        for cmd_name in self.command_type:
            self._write_dep(cmd_name, definined_cmd, fp)

        if not self.show_actions:
            fp.write('[IShowActions,0]\n')
        if self.freeze:
            fp.write('[IFreeze,\n')

        for cmd, args, kwargs in self.command_execution:
            fp.write(cmd.get_code(*args, **kwargs))
            fp.write('\n')

        if self.freeze:
            fp.write(']')

    def get_code(self):
        pass


def _on_cmd_called(self, *args, **kwargs):
    if _CURRENT_ZSCRIPT:
        _CURRENT_ZSCRIPT.add(self, *args, **kwargs)
    return self


def register_command(command_class, *args, **kwargs):
    name = command_class.__name__
    if name in _COMMANDS:
        raise ValueError('A command class with name "{}" already exists.'.format(command_class))

    # replace call method so we register the cmd each time it is called.
    command_class.__call__ = _on_cmd_called

    inst = command_class(*args, **kwargs)
    _COMMANDS[name] = inst
    return inst


def get_cmd(name):
    if name not in _COMMANDS:
        raise KeyError('Invalid command name "{}"'.format(name))

    com = _COMMANDS[name]
    return com


def call_cmd(name, init_args, init_dict, args, kwargs):
    com = get_cmd(*init_args, **init_dict)
    com(*args, **kwargs)

    return com
