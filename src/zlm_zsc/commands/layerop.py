from zlm_zsc.base_commands import ZRoutine, ZLayerRoutine


class DeactivateRecord(ZRoutine):

    def definition(self, *args, **kwargs):
        return '''
        [RoutineDef, zdr,
            [VarSet, curLayerName, [IGetTitle, "Tool:Layers:Layer Intensity"]]
            // frame current layer
            [If, [IsEnabled, Tool:Layers:SelectDown],
                [IPress, Tool:Layers:SelectDown]
            , /* else */
                [ISet, "Tool:Layers:Layers Scrollbar", 0, 0]
            ]
            [If, [IsEnabled, Tool:Layers:SelectUp],
                [IPress, Tool:Layers:SelectUp]
                [IPress, Tool:Layers:SelectDown]
            ]

            [VarSet, curLayerPath, [StrMerge, "Tool:Layers:", #curLayerName]]
            [VarSet, mode, [IModGet, curLayerPath]]

            [If, #mode == 1,
                // deactivate Recording
                [VarSet, wid, [IWidth,curLayerPath]]
                [IClick, curLayerPath, wid-10, 5]
            ]
        ]
        '''


class SetLayerMode(ZLayerRoutine):

    def definition(self, *args, **kwargs):
        return '''
        [RoutineDef, zslm,
            [ISet, "Tool:Layers:Layers Scrollbar", 0, index]
            [VarSet, layerPath, [StrMerge, "Tool:Layers:", #layerName]]

            [If, mode == 2,
                [ISet, layerPath, intensity]
            ]

            [VarSet, curMode, [IModGet, layerPath]]

            [If, curMode != mode,
                [VarSet, wid, [IWidth, layerPath]]
                [If, mode == 1,
                    [IClick, layerPath, wid-20, 5]
                ,
                    [If, curMode == 1,
                        [IClick, layerPath, wid-10, 5]
                    ]
                    [IClick, layerPath, wid-5, 5]
                ]
            ]
        , layerName, index, mode, intensity]
        '''

    def get_args_from_layer(self, layer):
        return [
            layer.name,
            layer.zbrush_index(),
            layer.mode,
            layer.intensity
        ]


class SetIntensity(ZLayerRoutine):

    def definition(self, *args, **kwargs):
        return '''
        [RoutineDef, zi,
            [ISet, "Tool:Layers:Layers Scrollbar", 0, index]
            [ISet, [StrMerge, "Tool:Layers:", #layerName], intensity]
        , layerName, index, intensity]
        '''

    def get_args_from_layer(self, layer):
        return [
            layer.name,
            layer.zbrush_index(),
            layer.intensity
        ]


class ExportLayer(ZLayerRoutine):

    def definition(self, *args, **kwargs):
        return '''
        [RoutineDef, zel,
            [ISet, "Tool:Layers:Layers Scrollbar", 0, index]
            [VarSet, layerPath, [StrMerge, "Tool:Layers:", #layerName]]

            // Activate
            [VarSet, wid, [IWidth, layerPath]]
            [ISet, layerPath, 1.0]

            [If, [IModGet, layerPath] == 0,
                [IClick, layerPath, wid-5, 5]
            ]

            // save
            [FileNameSetNext, #savePath]
            [IKeyPress, 13, [IPress, TOOL:Export:Export]]

            // Deactivate
            [IClick, layerPath, wid-5, 5]

        , layerName, index, savePath]
        '''

    def get_args_from_layer(self, layer):
        return [
            layer.name,
            layer.zbrush_index()
        ]


class CreateLayer(ZLayerRoutine):
    def definition(self, *args, **kwargs):
        return '''
        [RoutineDef, zcl,
            [VarSet, dllPath, ""]
            [MemReadString, zlmMFileUtilPath, dllPath]

            [IPress, "Tool:Layers:New"]
            [FileExecute, #dllPath, RenameSetNext, #layerName]
            [IPress, "Tool:Layers:Rename"]

            // Deactivate record layer
            [VarSet, layerPath, [StrMerge, "Tool:Layers:", #layerName]]
            [VarSet, wid, [IWidth, layerPath]]
            [IClick, layerPath, wid-10, 5]
        , layerName]
        '''

    def get_args_from_layer(self, layer):
        return [
            layer.name
        ]
