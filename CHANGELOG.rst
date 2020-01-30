Changelog
=========


1.1.3 (2020-01-30)
------------------

Fix
~~~
- Fix foreign key filters when pagination is enabled (#28) [Tadek
  Teleżyński]


1.1.2 (2020-01-08)
------------------
- Improvements for has_link (#27) [Bartłomiej Biernacki]

  * Display link even if it's not a ForeignKey but the object has get_absolute_url method

  * Support smart list without details link


1.1.1 (2019-12-18)
------------------

Fix
~~~
- Fix for model_field for column sometimes being none (#26) [Bartłomiej
  Biernacki]


1.1.0 (2019-12-17)
------------------

New
~~~
- Add changelog. [Tadek Teleżyński]

Fix
~~~
- Fix handling querysets which returns dicts (#25) [Bartłomiej
  Biernacki]

  * Fix handling querysets which returns dicts
- Fix local env setup. [Tadek Teleżyński]

Other
~~~~~
- Foreign keys links (#24) [Bartłomiej Biernacki]

  * Automatically add links to foreign key object if they define 'get_absolute_url'

  * Fixed black
- Generate changelog during git-release. [Tadek Teleżyński]


1.0.35 (2019-10-07)
-------------------

Fix
~~~
- Fix regression: unhashable type. [Tadek Teleżyński]


1.0.34 (2019-10-07)
-------------------

Fix
~~~
- Fix lack of default empty dict in preserve query params. [Tadek
  Teleżyński]


1.0.33 (2019-10-03)
-------------------

Fix
~~~
- Fix string unpacking. [Tadek Teleżyński]


1.0.32 (2019-09-30)
-------------------

Fix
~~~
- Fix formatting and typos in readme. [Tadek Teleżyński]
- Fixes callable field bug. [Tadek Teleżyński]

  The conditional statement in `get_value` was backwards.

Other
~~~~~
- Clear pagination when selecting new filter. [Tadek Teleżyński]
- Enable running a smart list example locally. [Tadek Teleżyński]

  This commit gives an out-of-the-box browser example of
  smart lists usage. It adds:
  - management command to create initial data
  - django view which utilizes different smart lists features
  - necessary templates, project files etc.
  - appropriate README section


1.0.31 (2019-09-09)
-------------------

Fix
~~~
- Fix filters with pagination. [Michal Simonienko]


1.0.30 (2019-07-29)
-------------------
- In list_display getter renturn copy of a list. [Michal Simonienko]


1.0.29 (2019-07-29)
-------------------

New
~~~
- Add getter for list_display. [Michal Simonienko]

  Add getter for list_display.
  Add missing imports for type checking.


1.0.28 (2019-07-26)
-------------------

New
~~~
- Add black and reformat code. [Michal Simonienko]

  from now on project follows black style guide

Fix
~~~
- Fix ordering. [Michal Simonienko]
- Fix travis exclude. [bartek-biernacki]
- Fix tests. [bartek-biernacki]

Other
~~~~~
- .gitignore and Travis config. [bartek-biernacki]
- Update README. [Michal Simonienko]


1.0.26 (2019-07-17)
-------------------

New
~~~
- Add render_column_template helper. [Michal Simonienko]
- Add custom rendered custom element. [Michal Simonienko]

  From now on you can pass in list_displays also two element iterables in
  which first element is a callble that returns html and second element is
  a label for that column.

Fix
~~~
- Fix XSS vulnerability in render_function. [Michal Simonienko]

Other
~~~~~
- Make render_function more versatile. [Michal Simonienko]


1.0.25 (2019-07-12)
-------------------

New
~~~
- Add labels for columns. [Michal Simonienko]

  From now on in list_display you can pass string or tuple of two
  strings. First string in a tuple is the field name and second is a label
  (the name for column).


1.0.24 (2019-07-09)
-------------------

New
~~~
- Added Makefile for easy releasing. [Ales Kocjancic]

Fix
~~~
- Fix default arguments logic for smart_list templatetag. [Michal
  Simonienko]

Other
~~~~~
- Removed md description since it fails on pypi. [Ales Kocjancic]


1.0.23 (2019-06-13)
-------------------

New
~~~
- Add django 2 compatibility. [Krzysztof Bujniewicz]

Other
~~~~~
- Moved version into package. [Ales Kocjancic]


1.0.22 (2018-09-30)
-------------------
- Make sure it works wiht both classes and str. [Kristian Øllegaard]
- Bugfix. [Kristian Øllegaard]


1.0.20 (2018-09-30)
-------------------
- Bugfix and more tests. [Kristian Øllegaard]


10.0.19 (2018-09-30)
--------------------
- Support for custom filters, like the ones found in Django admin.
  [Kristian Øllegaard]
- Prettier labels (which are also translated already by Django)
  [Kristian Øllegaard]
- Custom classes and grid sizes and fixed tests. [Kristian Øllegaard]
- Update README.md. [Kristian Øllegaard]


1.0.17 (2017-04-28)
-------------------

Fix
~~~
- Fixed test to use q GET parameter. [Mikkel Clausen]
- Fixed typo in comment. [Mikkel Clausen]

Other
~~~~~
- Refactored internals and made choices on filters bold. [Kristian
  Øllegaard]
- Support .values() querysets. [Kristian Øllegaard]
- Removed unused method. [Mikkel Clausen]
- Smart_lists: fixed code style. [Mikkel Clausen]
- Smart_lists/helpers: fix for getTitle. [Mikkel Clausen]
- Smart_lists/helpers: use _meta in getTitle. [Mikkel Clausen]
- Renamed search GET parameter to q instead of search. [Mikkel Clausen]
- Cleanup nameing of search_query_value and list_search. [Mikkel
  Clausen]
- Implemented django-admin like search including test. [Mikkel Clausen]
- More tests. [Kristian Øllegaard]


10.0.13 (2017-03-14)
--------------------

Fix
~~~
- Fixed readme to use smart_list as template tag instead of smart_lists.
  [Mikkel Clausen]

Other
~~~~~
- Smart_lists/templatetag/smart_list.py: fixed name collision. [Mikkel
  Clausen]


10.0.12 (2017-03-12)
--------------------
- Filters !!! [Kristian Øllegaard]


10.0.11 (2017-03-12)
--------------------
- Ordering on custom list_display functions and short_description.
  [Kristian Øllegaard]


1.0.10 (2017-03-12)
-------------------
- Easy multiple sorting and better templates. [Kristian Øllegaard]
- Redid ordering so it supports multiple columns and uses the same
  syntax as django admin. [Kristian Øllegaard]


1.0.8 (2017-03-12)
------------------

Fix
~~~
- Fixed this packaging mess. [Kristian Øllegaard]

Other
~~~~~
- Wrong import. [Kristian Øllegaard]
- Packaging is hard .. :-) [Kristian Øllegaard]
- 1.0.1. [Kristian Øllegaard]
- Packaging. [Kristian Øllegaard]
- Setup.py. [Kristian Øllegaard]
- Update README.md. [Kristian Øllegaard]
- Update README.md. [Kristian Øllegaard]
- Update README.md. [Kristian Øllegaard]
- Initial commit / MVP. [Kristian Øllegaard]
- Initial commit. [Kristian Øllegaard]


