SublimeLinter-annotations
=========================

[![Build Status](https://travis-ci.org/SublimeLinter/SublimeLinter-annotations.svg?branch=master)](https://travis-ci.org/SublimeLinter/SublimeLinter-annotations)

This linter plugin for [SublimeLinter](https://github.com/SublimeLinter/SublimeLinter) highlights annotations in comments such as FIXME, NOTE, TODO, @todo, XXX, and README.
It will be used with all files.

## Installation
SublimeLinter must be installed in order to use this plugin.

Please use [Package Control](https://packagecontrol.io) to install the linter plugin.

## Settings
- SublimeLinter settings: http://sublimelinter.com/en/latest/settings.html
- Linter settings: http://sublimelinter.com/en/latest/linter_settings.html

Additional SublimeLinter-annotations settings:

|Setting|Description|
|:------|:----------|
|`warnings`|Comma-delimited list of words that will be highlighted as warnings.|
|`errors`|Comma-delimited list of words that will be highlighted as errors.|
|`infos`|Comma-delimited list of words that will be highlighted as infos.|
|`selector_` (*advanced*)| A scope selector for regions that the word lists will be searched in.|

Matching is case-sensitive and matches whole words.

For example:

```json
"linters": {
    "annotations": {
        "infos": ["NOTA BENE", "FYI"],
        "warnings": ["FOO", "BAR"],
        "errors": ["WHAT?", "OMG!"]
    }
}
```
