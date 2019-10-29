# nephelaiio.plugins

[![Build Status](https://travis-ci.org/nephelaiio/ansible-plugins.svg?branch=master)](https://travis-ci.org/nephelaiio/ansible-role-plugins)
[![Ansible Galaxy](http://img.shields.io/badge/ansible--galaxy-nephelaiio.plugins-blue.svg)](https://galaxy.ansible.com/nephelaiio/plugins/)

An [ansible role](https://galaxy.ansible.com/nephelaiio/plugins) for custom plugins definitions


## Requirements

* [PyYaml](https://pyyaml.org) is required for `to_safe_yaml` filter execution

## Example Playbook

```
- hosts: servers
  roles:
     - role: nephelaiio.plugins
```

## Testing

Please ensure all libraries listed in the [requirements file](/requirements.txt) are currently installed and test using command `pytest`

## License

This project is licensed under the terms of the [MIT License](/LICENSE)
