-- add_spanish_input_source.applescript
-- This script opens System Settings -> Keyboard -> Input Sources to help you add Spanish layout.
-- Note: macOS doesn't expose a reliable automated way to add input sources without UI scripting permissions.

tell application "System Settings"
    activate
end tell

tell application "System Events"
    delay 0.5
    -- Open Spotlight search and type 'keyboard'
    keystroke space using {command down}
    delay 0.3
    keystroke "keyboard"
    delay 0.5
    keystroke return
end tell

display dialog "System Settings opened. Please add 'Spanish' under Input Sources -> + and enable 'Show input menu in menu bar' if desired." buttons {"OK"} default button "OK"
