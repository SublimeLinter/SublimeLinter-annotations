SublimeLinter-annotations
=========================

[![Build Status](https://travis-ci.org/SublimeLinter/SublimeLinter-annotations.svg?branch=master)](https://travis-ci.org/SublimeLinter/SublimeLinter-annotations)

This linter plugin for [SublimeLinter](http://sublimelinter.readthedocs.org) highlights annotations in comments such as FIXME, NOTE, TODO, XXX and README. It will be used with all files.

## Installation
SublimeLinter 3 must be installed in order to use this plugin. If SublimeLinter 3 is not installed, please follow the instructions [here](http://sublimelinter.readthedocs.org/en/latest/installation.html).

### Plugin installation
Please use [Package Control](https://sublime.wbond.net/installation) to install the linter plugin. This will ensure that the plugin will be updated when new versions are available. If you want to install from source so you can modify the source code, you probably know what you are doing so we won’t cover that here.

To install via Package Control, do the following:

1. Within Sublime Text, bring up the [Command Palette](http://docs.sublimetext.info/en/sublime-text-3/extensibility/command_palette.html) and type `install`. Among the commands you should see `Package Control: Install Package`. If that command is not highlighted, use the keyboard or mouse to select it. There will be a pause of a few seconds while Package Control fetches the list of available plugins.

1. When the plugin list appears, type `annotations`. Among the entries you should see `SublimeLinter-annotations`. If that entry is not highlighted, use the keyboard or mouse to select it.

## Settings
For general information on how SublimeLinter works with settings, please see [Settings](http://sublimelinter.readthedocs.org/en/latest/settings.html). For information on generic linter settings, please see [Linter Settings](http://sublimelinter.readthedocs.org/en/latest/linter_settings.html).

In addition to the standard SublimeLinter settings, SublimeLinter-annotations provides its own settings.

|Setting|Description|
|:------|:----------|
|warnings|Comma-delimited list of words that will be highlighted as warnings.|
|errors|Comma-delimited list of words that will be highlighted as errors.|

You may provide a string with multiple words separated by commas or a list of strings. Matching is case-sensitive and matches whole words.

For example:

```json
"linters": {
    "annotations": {
        "warnings": "[FOO], BAR",
        "errors": ["WHAT?", "OMG!"]
    }
}
```

## Contributing
If you would like to contribute enhancements or fixes, please do the following:

1. Fork the plugin repository.
1. Hack on a separate topic branch created from the latest `master`.
1. Commit and push the topic branch.
1. Make a pull request.
1. Be patient.  ;-)

Please note that modications should follow these coding guidelines:

- Indent is 4 spaces.
- Code should pass flake8 and pep257 linters.
- Vertical whitespace helps readability, don’t be afraid to use it.
- Please use descriptive variable names, no abbrevations unless they are very well known.

Thank you for helping out!
