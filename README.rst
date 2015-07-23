===================
Text-based-switcher
===================

Text-based window switcher for Unity

The visual switcher is very poor at providing context. E.g. the browser window
thumbnails are too small to tell apart. 

This switcher shows a list of window titles and allows you to choose one
by typing first character(s) of the sought window. Press return to bring the
window to the front.

All credit goes to the original author, Jacob Vlijm. Thanks!
See http://askubuntu.com/a/648800/20835

Usage
=====

The script needs ``wmctrl`` and ``xprop``. On Ubuntu:

.. code:: console

    $ sudo apt-get install wmctrl x11-utils

Install from PyPI:

.. code:: console

    $ sudo pip install text_based_switcher

Test-run it:

.. code:: console

    $ list_windows --workspace
    $ list_windows --application
    $ list_windows --window

If it works, add one or more of the preferred commands to one or more shortcut
keys: choose:
_System Settings_ > _Keyboard_ > _Shortcuts_ > _Custom Shortcuts_.

Click the "+" and add the command.

If you do a local install (``--user`` option), Compiz won't get the right
Python path.
You can fix this by hacking ``sys.path`` in the installed script.

TODO
====

- Add wmctrl or ruamel.emwh as dependency
- Add xprop as dependency
- Don't call commands, use Python libraries
- Write some tests


Developer notes
===============

Please use a virtualenv to maintain this package, but I should not need to say that.

Grab the source from the SCM repository:

.. code:: console

  $ python setup.py develop
  $ pip install text-based-switcher[dev]

If you install 

Run the tests (there are no tests yet!):

.. code:: console

  $ python setup.py test
  $ python run_tests.py


Links
=====

Project home page

  https://github.com/jean/text-based-switcher

Source code

  https://github.com/jean/text-based-switcher

Issue tracker

  https://github.com/jean/text-based-switcher/issues
