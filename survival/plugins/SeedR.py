from mcdreforged.api.types import ServerInterface
from mcdreforged.api.command import Literal
from mcdreforged.api.rtext import RTextBase, RText, RTextTranslation, RTextList, RColor, RAction

PLUGIN_METADATA = {
    'id': 'seed_reforged',
    'version': '1.0.3',
    'name': 'SeedR',
    'description': 'For non-op, use command "!!seed" to get seed of server',
    'author': 'Charlie_NI',
    'dependencies': {
        'mcdreforged': '>=1.0.0',
    }
}

NAME = PLUGIN_METADATA['name']


def get_seed(server: ServerInterface) -> RTextBase:
    try:
        seed = server.rcon_query('/seed').split('[')[1].split(']')[0]
        return RTextList(
            RTextTranslation('commands.seed.success'),
            '[', RText(seed, RColor.green)
            .c(RAction.copy_to_clipboard, seed)
            .h(RTextTranslation('chat.copy.click')), ']'
        )
    except Exception:
        warning = RText(
            f'§cPlugin {NAME} §lCANNOT§c get server seed by §lRCON§c, please checkout config of §lMCDR§c!'
        ).c(RAction.open_url, LINK).h(f'§lDocs§r: §n{LINK}§r')
        server.logger.warning(warning.to_plain_text())
        return RText(warning)


def on_load(server: ServerInterface, prev):
    server.register_help_message('!!seed', 'Get seed of server')
    server.register_command(
        Literal('!!seed').runs(lambda src: src.reply(get_seed(server)))
    )
