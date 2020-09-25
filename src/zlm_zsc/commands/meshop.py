from zlm_zsc.base_commands import ZRoutine, ZLayerRoutine


class ExportMesh(ZRoutine):
    def definition(self, *args, **kwargs):
        return '''
        [RoutineDef, zem,
            // save
            [FileNameSetNext, #savePath]
            [IKeyPress, 13, [IPress, TOOL:Export:Export]]

        , savePath]
        '''


class ImportMesh(ZRoutine):

    def definition(self, *args, **kwargs):
        return '''[RoutineDef, zim, 
            [VarSet, dllPath, ""]
            [MemReadString, zlmMFileUtilPath, dllPath]

            [VarSet, subtoolName, [IGetTitle,Tool:ItemInfo]]
            [FileNameSetNext, #importPath]
            [IKeyPress, 13, [IPress, Tool:Import:Import]]

            [FileExecute, #dllPath, RenameSetNext, [StrExtract, #subtoolName, 0, ([StrLength, #subtoolName] - 2)]]
            [IPress, "Tool:SubTool:Rename"]

        , importPath]
        '''


class GetNumPoint(ZRoutine):
    def definition(self, *args, **kwargs):
        return '''
        [RoutineDef, zgnp,
            [VarSet,InfoStr, [IGetInfo, "Tool:Current Tool"]]
            [Loop, 2,
                [VarSet, offset, [StrFind,"=", InfoStr]]
                [VarSet, InfoStr, [StrExtract, InfoStr, offset + 1, 256]]
            ]
            [VarSet,offset, [StrFind, [StrFromAsc, 10], InfoStr]] //find line break
            [VarSet,InfoStr, [StrExtract, InfoStr, 0, offset-1]]
            [VarSet,pCount, InfoStr]
        , pCount]
        '''


class SetSubDivForVertex(ZRoutine):
    def __init__(self, *args, **kwargs):
        ZRoutine.__init__(self, ('GetNumPoint', ), *args, **kwargs)

    def definition(self, *args, **kwargs):
        return '''
        [RoutineDef, zssdv,
            // start at subdiv 1 than advance the subvision till the vertex count 
            // equal the requested vertex count
            [VarSet, found, 0]
            [VarSet, pCount, 0]
            [Loop, [IGetMax, "Tool:Geometry:SDiv"],
                [ISet,"Tool:Geometry:SDiv", #subdiv + 1, 0]
                [RoutineCall, zgnp, pCount]
                [If, pCount == vCount,
                    [VarSet, found, 1]
                    [LoopExit]
                ]
            , subdiv]
        , vCount, found]
        '''


class UpdateMesh(ZRoutine):
    def __init__(self, *args, **kwargs):
        ZRoutine.__init__(self, ('SetSubDivForVertex', ), *args, **kwargs)

    def definition(self, *args, **kwargs):
        return '''
        [RoutineDef, zim,
            [VarSet, found, 0]
            [RoutineCall, zssdv, vCount, found]

            [VarSet, dllPath, ""]
            [MemReadString, zlmMFileUtilPath, dllPath]

            [If, found,
                [VarSet, subtoolName, [IGetTitle,Tool:ItemInfo]]
                [FileNameSetNext, #filepath]
                [IKeyPress, 13, [IPress, Tool:Import:Import]]

                [FileExecute, #dllPath, RenameSetNext, [StrExtract, #subtoolName, 0, ([StrLength, #subtoolName] - 2)]]
                [IPress, "Tool:SubTool:Rename"]
            , /* else */
                [NoteBar, [StrMerge, "Skipping import - Couldn't find subdivision with ", #vCount, "points."]]
            ]

            [If, deleteAfter,
                [FileExecute, #dllPath, FileDelete, #filepath]
            ]

        , filepath, vCount, deleteAfter]
        '''
