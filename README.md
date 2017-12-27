SublimeLinter-annotations
=========================

[![Build Status](https://travis-ci.org/SublimeLinter/SublimeLinter-annotations.svg?branch=master)](https://travis-ci.org/SublimeLinter/SublimeLinter-annotations)

This linter plugin for [SublimeLinter](http://sublimelinter.readthedocs.org) highlights annotations in comments such as FIXME, NOTE, TODO, @todo, XXX, and README. It will be used with all files.

## Installation
SublimeLinter 3 must be installed in order to use this plugin. 

Please use [Package Control](https://packagecontrol.io) to install the linter plugin.

## Settings
- SublimeLinter settings: http://sublimelinter.readthedocs.org/en/latest/settings.html
- Linter settings: http://sublimelinter.readthedocs.org/en/latest/linter_settings.html

Additional SublimeLinter-annotations settings:

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
