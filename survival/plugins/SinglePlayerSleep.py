# -*- coding: utf-8 -*-
import sys
import time
import re
import os
import ruamel.yaml as yaml
#sys.path.append('/usr/local/python3/lib/python3.9/site-packages')
import hjson

from mcdreforged.api.rtext import *
from mcdreforged.api.command import *
from mcdreforged.api.decorator import new_thread
from mcdreforged.plugin.server_interface import ServerInterface
#from ConfigAPI import Config

PLUGIN_METADATA = {
    'id': 'single_player_sleep',
    'version': '0.0.1',
    'name': 'SinglePlayerSleep',
    'description': 'Allowed single sleep in server to skip night',
    'author': 'Charlie_NI',
    'dependencies': {
        'minecraft_data_api': '*',
        'config_api': '*'
    }
}
DEFAULT_CONFIG = {
    'skip_wait_time': 0,
    'wait_before_skip': 3,
    'waiting_for_skip': '§e{0} §c is sleeping, skipping the night after §e{1} §cs, click this message to cancel it',
    'already_sleeping': '§c There is already player sleeping',
    'no_one_sleeping': '§c No player is sleeping',
    'not_fall_asleep': '§c You haven\'t fell into sleep deeply',
    'skip_abort': '§a SKIPPING NIGHT CANCELED',
    'is_daytime': '§c It\'s DAYTIME now'
}

class Config:
    def __init__(self, plugin_name: str, default: dict,
                 config_name: str = None):
        self.default = default
        self.dir = os.path.join('config', plugin_name)
        if not os.path.isdir(self.dir):
            os.mkdir(self.dir)
        config_name = plugin_name if config_name is None else config_name
        self.path = os.path.join(self.dir, f'{config_name}.yml')
        self.data = None
        self._check()

    def _check(self):
        self._read()
        save_flag = False
        for key, value in self.default.items():
            if key not in self.data.keys():
                self.data[key] = value
                save_flag = True
        if save_flag:
            self._save()

    def _read(self):
        if os.path.isfile(self.path):
            with open(self.path) as f:
                self.data = yaml.safe_load(f)
        else:
            self.data = self.default
            self._save()

    def _save(self):
        with open(self.path, 'w') as f:
            yaml.dump(self.data, f)

    def __getitem__(self, key):
        if key not in self.data.keys():
            raise ValueError(key + ' is not in configuration')
        else:
            return self.data[key]

    def get(self, key):
        if key not in self.data.keys():
            raise ValueError(key + ' is not in configuration')
        else:
            return self.data[key]

    def set(self, key, value):
        """set configuration item"""
        if key not in self.default.keys():
            raise ValueError(key + ' has not registered')
        else:
            self.data[key] = value
            self._save()

    def reload(self):
        """reload config from file"""
        self._check()

    def reset_default(self):
        """reset all configuration to default"""
        self.data = self.default
        self._save()

    def get_default(self, key):
        """get default configuration item"""
        if key not in self.data.keys():
            raise ValueError(key + ' is not in configuration')
        else:
            return self.default[key]

class Single:
    want_skip = False
    commend_sent = False
    now_time = 0
    config = Config('SinglePlayerSleep', DEFAULT_CONFIG)


single = Single()


def on_info(server, info):
    global single
    if single.commend_sent:
        parse_time_info(info.content)


def on_load(server: ServerInterface, old):
    global single

    @new_thread('SinglePlayerSleep')
    def sleep(src):
        get_time(src.get_server())
        if single.now_time >= 12542:
            fall_asleep = src.get_server().get_plugin_instance(
                'minecraft_data_api').get_player_info(src.player, 'SleepTimer')
            if fall_asleep != 100:
                return src.reply(single.config['not_fall_asleep'])
        else:
            return src.reply(single.config['is_daytime'])
        single.want_skip = True
        need_skip_time = 24000 - single.now_time
        for i in range(single.config['wait_before_skip'], 0, -1):
            if not single.want_skip:
                return
            msg = RText(
                single.config['waiting_for_skip'].format(src.player, i)).c(
                RAction.run_command, '!!sleep cancel'
            )
            src.get_server().say(msg)
            time.sleep(1)
        for i in range(0, single.config['skip_wait_time']):
            if not single.want_skip:
                return
            jump_times = int(need_skip_time / single.config['skip_wait_time'])
            if src.get_server().is_rcon_running():
                src.get_server().rcon_query(f'time add {jump_times}')
            else:
                src.get_server().execute(f'time add {jump_times}')
            time.sleep(1)
        single.want_skip = False

    def cancel(src):
        if single.want_skip:
            single.want_skip = False
            src.reply(single.config['skip_abort'])
        else:
            src.reply(single.config['no_one_sleeping'])

    single = Single()
    server.register_help_message('!!sleep', RText(
        'SinglePlayerSleep to skip the night').c(RAction.run_command, '!!sleep').h('CLICK me to skip the night'))
    server.register_help_message('!!sleep cancel', 'SKIPPING NIGHT CANCELED')
    server.register_command(
        Literal('!!sleep').
            runs(sleep).
            then(
            Literal('cancel').
                runs(cancel)
        )
    )


def on_unload(server):
    global single
    if single.want_skip:
        server.say(single.config['skip_abort'])
        single.want_skip = False


def get_time(server):
    if server.is_rcon_running():
        parse_time_info(server.rcon_query('time query daytime'))
    else:
        server.execute('time query daytime')
        single.commend_sent = True


def parse_time_info(msg):
    global single
    if re.match(r'The time is .*', msg):
        single.now_time = int(msg.split('is ')[-1])
