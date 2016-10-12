#!/usr/bin/env bash

echo "Converting forms"
pyuic4 -o ./ui_quickmotor.py ./ui_quickmotor.ui
pyuic4 -o ./ui_scanwindow.py ./ui_scanwindow.ui
pyuic4 -o ./ui_hideable.py ./ui_hideable.ui
pyuic4 -o ./ui_profiledialog.py ./ui_profiledialog.ui
pyuic4 -o ./ui_trend_holder.py ./ui_trend_holder.ui
pyuic4 -o ./ui_list_channel_widget.py ./ui_list_channel_widget.ui
pyuic4 -o ./ui_window.py ./ui_window.ui
pyuic4 -o ./ui_list.py ./ui_list.ui

echo "Converting resources"
pyrcc4 -o resource_hider_rc.py resource_hider.qrc