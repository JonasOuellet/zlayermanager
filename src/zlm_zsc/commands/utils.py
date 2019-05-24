from zlm_zsc.base_commands import ZCommand


class SubdivStore(ZCommand):
    def call(self, *args, **kwargs):
        return '[VarSet,subLevel,[IGet,"Tool:Geometry:SDiv"]]'

    def get(self):
        return '#subLevel'


class SubdivSet(ZCommand):
    def __init__(self, *args, **kwargs):
        ZCommand.__init__(self, *args, **kwargs)

    def call(self, *args, **kwargs):
        if not args:
            text = '0'
        else:
            text = self.get_zcode(args[0])

        return '[ISet,"Tool:Geometry:SDiv",{},0]'.format(text)

    def get(self):
        return '[IGet,"Tool:Geometry:SDiv"]'


class SubdivRestore(ZCommand):
    def call(self, *args, **kwargs):
        return '[ISet,"Tool:Geometry:SDiv",#subLevel,0]'


class SubdivMax(ZCommand):
    def call(self, *args, **kwargs):
        return '[ISet,"Tool:Geometry:SDiv",[IGetMax,"Tool:Geometry:SDiv"],0]'

    def get(self):
        return '[IGetMax,"Tool:Geometry:SDiv"]'


class Quote(ZCommand):
    zscript = '[VarSet,qte,[StrFromAsc,34]]'

    def call(self, *args, **kwargs):
        return self.zscript

    def get(self):
        return '#qte'

    # def definition(self, *args, **kwargs):
    #     return self.zscript
