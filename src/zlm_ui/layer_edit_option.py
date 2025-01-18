import zlm_settings

option_name = 'layer_edit'
ask_before_delete = 'ask_before_delete'
allow_bellow_zero = 'allow_bellow_zero'

# make duplicate way slower
move_dup_layer_down = 'move_dup_layer_down'

default_options = {
    ask_before_delete: True,
    move_dup_layer_down: False,
    allow_bellow_zero: False
}

options = zlm_settings.ZlmSettings.instance().get(option_name, default_options)


def should_ask_before_delete():
    return options.get(ask_before_delete, default_options[ask_before_delete])


def should_move_dup_down():
    return options.get(move_dup_layer_down, default_options[move_dup_layer_down])


def should_go_bellow_zero() -> bool:
    return options.get(allow_bellow_zero, default_options[allow_bellow_zero])
