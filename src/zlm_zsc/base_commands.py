from zlm_core import ZlmLayer


class ZCommand(object):

    def __init__(self, *args, **kwargs):
        self._definition = None
        defin = self.definition(*args, **kwargs)
        if defin is not None:
            defin = self.parse_definition(defin)
        self._definition = defin

    def definition(self, *args, **kwargs):
        return None

    def parse_definition(self, zscript):
        """Do some cleanup on the zscript definition text.
        return (str) the definition of this zscript code.
        """
        return zscript

    def get_code(self, *args, **kwargs):
        return self.call(*args, **kwargs)

    def call(self, *args, **kwargs):
        """Return a string that represent the the zscript execution
        for this command.

        Raises:
            NotImplementedError: Must be implemented in child classes.
        """
        raise NotImplementedError

    def get(self):
        return self.call(self.args, self.kwargs)

    def get_zcode(self, arg):
        if isinstance(arg, ZCommand):
            return arg.get()

        if isinstance(arg, str):
            text = '"{}"'.format(arg)
            return text

        return str(arg)


class ZRoutine(ZCommand):
    def __init__(self, *args, **kwargs):
        self.command_name = ""

        ZCommand.__init__(self, *args, **kwargs)

    def parse_definition(self, zscript):
        out = ""
        name_set = False

        idx = 0
        while idx < len(zscript):
            c = zscript[idx]

            if not name_set and c == ',':
                s = idx + 1
                e = zscript.find(',', s)
                self.command_name = zscript[s:e].strip()
                idx = e
                name_set = True
                out += ',' + self.command_name + ','
            elif c == '"':
                # find next '""
                s = idx + 1
                e = zscript.find('"', s)
                out += zscript[idx:e+1]
                idx = e
            elif c == '/':
                c1 = zscript[idx + 1]
                if c1 == '/':
                    # line comment
                    idx = zscript.find('\n', idx + 1)
                if c1 == '*':
                    # multi line comment
                    idx = zscript.find('*/', idx + 1) + 1

            elif c not in (' ', '\n', '\t'):
                out += c

            idx += 1

        return out

    def call(self, *args, **kwargs):
        out = '[RoutineCall,{}'.format(self.command_name)
        for arg in args:
            out += ',' + self.get_zcode(arg)
        out += ']'
        return out

    def definition(self):
        raise NotImplementedError("ZRoutine must have a definition.")


class ZLayerRoutine(ZRoutine):

    def __init__(self, *args, **kwargs):
        ZRoutine.__init__(self, *args, **kwargs)

    def call(self, *args, **kwargs):
        if len(args):
            if isinstance(args[0], ZlmLayer):
                newargs = self.get_args_from_layer(args[0])
                newargs.extend(args[1:])
                return ZRoutine.call(self, *newargs, **kwargs)

        return ZRoutine.call(self, *args, **kwargs)

    def get_args_from_layer(self, layer):
        raise NotImplementedError
