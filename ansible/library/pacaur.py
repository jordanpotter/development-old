#!/usr/bin/env python

# The MIT License (MIT)
#
# Copyright (c) 2014 Austin Hyde
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

def pacaur_in_path(module):
  rc, stdout, stderr = module.run_command('which pacaur', check_rc=False)
  return rc == 0


def pacman_in_path(module):
  rc, stdout, stderr = module.run_command('which pacman', check_rc=False)
  return rc == 0


def package_installed(module, pkg):
  rc, stdout, stderr = module.run_command('pacman -Q %s' % pkg, check_rc=False)
  return rc == 0


def check_packages(module, pkgs, state):
  would_be_changed = []

  for pkg in packages:
    installed = package_installed(module, pkg)
    if (state == 'present' and not installed) or (state == 'absent' and installed):
      would_be_changed.append(pkg)

  word = 'installed'
  if state == 'absent':
    word = 'removed'

  if would_be_changed:
    module.exit_json(changed=True, msg='%s package(s) would be %s' % (len(would_be_changed), word))
  else:
    module.exit_json(changed=False, msg='all packages are already %s' % word)


def install_packages(module, pkgs):
  num_installed = 0

  cmd = 'pacaur --noconfirm --noedit -S %s'

  for pkg in pkgs:
    if package_installed(module, pkg):
      continue

    rc, stdout, stderr = module.run_command(cmd % pkg, check_rc=False)

    if rc != 0:
      module.fail_json(msg='failed to install package %s, because: %s' % (pkg,stderr))

    num_installed += 1

  if num_installed > 0:
    module.exit_json(changed=True, msg='installed %s package(s)' % num_installed)
  else:
    module.exit_json(changed=False, msg='all packages were already installed')


def remove_packages(module, pkgs, recurse):
  num_removed = 0

  arg = 'R'
  word = 'remove'
  if recurse:
    arg = 'Rs'
    word = 'recursively remove'

  cmd = 'pacman -%s --noconfirm %s'

  for pkg in pkgs:
    if not package_installed(module, pkg):
      continue

    rc, stdout, stderr = module.run_command(cmd % (arg, pkg), check_rc=False)

    if rc != 0:
      module.fail_json(msg='failed to %s package %s because: %s' % (word, pkg, stderr))

    num_removed += 1

  if num_removed > 0:
    module.exit_json(changed=True, msg='removed %s package(s)' % num_removed)
  else:
    module.exit_json(changed=False, msg='all packages were already removed')


def main():
  module = AnsibleModule(
    argument_spec = dict(
      name         = dict(required=True),
      state        = dict(default='present', choices=['present','absent']),
      recurse      = dict(default='no', choices=BOOLEANS, type='bool')
    ),
    supports_check_mode = True
  )

  if not pacaur_in_path(module):
    module.fail_json(msg="could not locate pacaur executable")

  if not pacman_in_path(module):
    module.fail_json(msg="could not locate pacman executable")

  p = module.params

  pkgs = p['name'].split(',')

  if module.check_mode:
    check_packages(module, pkgs, p['state'])

  if p['state'] == 'present':
    install_packages(module, pkgs)
  elif p['state'] == 'absent':
    remove_packages(module, pkgs, p['recurse'])


from ansible.module_utils.basic import *
main()
