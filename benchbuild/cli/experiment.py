"""Subcommand for experiment handling."""
import sqlalchemy as sa
import urwid
from plumbum import cli

from benchbuild import experiment, experiments
from benchbuild.cli.main import BenchBuild
from benchbuild.utils import schema


@BenchBuild.subcommand("experiment")
class BBExperiment(cli.Application):
    """Manage BenchBuild's known experiments."""

    def main(self):
        if not self.nested_command:
            self.help()


@BBExperiment.subcommand("view")
class BBExperimentView(cli.Application):
    """View available experiments."""

    def main(self):
        experiments.discover()
        all_exps = experiment.ExperimentRegistry.experiments
        for exp_cls in all_exps.values():
            print(exp_cls.NAME)
            docstring = exp_cls.__doc__ or "-- no docstring --"
            print(("    " + docstring))


class MenuButton(urwid.Button):
    def __init__(self, caption, callback):
        super(MenuButton, self).__init__("")
        urwid.connect_signal(self, 'click', callback)
        self._w = urwid.AttrMap(
            urwid.SelectableIcon([u'  \N{BULLET} ', caption], 2), None,
            'selected')


class SubMenu(urwid.WidgetWrap):
    def __init__(self, caption, choices, top):
        super(SubMenu, self).__init__(
            MenuButton([caption, "\N{HORIZONTAL ELLIPSIS}"], self.open_menu))
        line = urwid.Divider('\N{LOWER ONE QUARTER BLOCK}')
        listbox = urwid.ListBox(
            urwid.SimpleFocusListWalker([
                urwid.AttrMap(urwid.Text(["\n  ", caption]), 'heading'),
                urwid.AttrMap(line, 'line'),
                urwid.Divider()
            ] + choices + [urwid.Divider()]))
        self.menu = urwid.AttrMap(listbox, 'options')
        self.top = top

    def open_menu(self, _):
        self.top.open_box(self.menu)


class Choice(urwid.WidgetWrap):
    def __init__(self, caption, payload, top):
        super(Choice, self).__init__(MenuButton(caption, self.item_chosen))
        self.caption = caption
        self.top = top
        self.payload = payload

    def item_chosen(self, _):
        session = schema.Session()
        session.delete(self.payload)

        def confirm(_):
            session.commit()
            self.top.clear()
            self.top.open_box(refresh_root_window(self.top))

        def cancel(_):
            session.rollback()
            self.top.clear()
            self.top.open_box(refresh_root_window(self.top))

        response = urwid.Text([
            'Really delete: {name} {desc}?'.format(
                name=self.payload.name, desc=self.payload.description), '\n'
        ])
        done = MenuButton('Ok', confirm)
        cancel = MenuButton('Cancel', cancel)
        response_box = urwid.Filler(urwid.Pile([response, done, cancel]))
        self.top.open_box(urwid.AttrMap(response_box, 'options'))


class HorizontalBoxes(urwid.Columns):
    def __init__(self):
        super(HorizontalBoxes, self).__init__([], dividechars=1)

    def clear(self):
        self.contents = []

    def open_box(self, box):
        focus_map = {
            'heading': 'focus heading',
            'options': 'focus options',
            'line': 'focus line'
        }
        if self.contents:
            del self.contents[self.focus_position + 1:]
        self.contents.append((urwid.AttrMap(box, 'options', focus_map),
                              self.options('given', 80)))
        self.focus_position = len(self.contents) - 1


@BBExperiment.subcommand("manage")
class BBExperimentShow(cli.Application):
    """Show completed experiments."""

    def main(self):
        def maybe_exit(key):
            if key in ('q', 'Q'):
                raise urwid.ExitMainLoop()

        # yapf: disable
        palette = [(None, 'light gray', 'black'),
                   ('heading', 'black', 'light gray'),
                   ('line', 'black', 'light gray'),
                   ('options', 'dark gray', 'black'),
                   ('focus heading', 'white', 'dark red'),
                   ('focus line', 'black', 'dark red'),
                   ('focus options', 'black', 'light gray'),
                   ('selected', 'white', 'dark blue')]

        # yapf: enable
        top = HorizontalBoxes()
        top.open_box(refresh_root_window(top))
        loop = urwid.MainLoop(
            urwid.Filler(top, 'top', height=48),
            palette=palette,
            unhandled_input=maybe_exit)
        loop.run()


def get_template():
    from jinja2 import Environment, PackageLoader
    env = Environment(
        trim_blocks=True,
        lstrip_blocks=True,
        loader=PackageLoader('benchbuild', 'utils/templates'))
    return env.get_template('experiment_show.txt.inc')


def render_experiment(_experiment):
    template = get_template()
    sess = schema.Session()

    return template.render(
        name=_experiment.name,
        description=_experiment.description,
        start_date=_experiment.begin,
        end_date=_experiment.end,
        id=_experiment.id,
        num_completed_runs=get_completed_runs(sess, _experiment),
        num_failed_runs=get_failed_runs(sess, _experiment))


def refresh_root_window(root):
    session = schema.Session()
    all_db_exps = experiments_from_db(session)
    menu_top = SubMenu(
        'Experiments in database', [
            SubMenu(
                "{name} - {desc}".format(
                    name=elem.name, desc=elem.description), [
                        urwid.Text(render_experiment(elem)),
                        urwid.Divider(),
                        Choice("Delete", top=root, payload=elem)
                    ],
                top=root) for elem in all_db_exps
        ],
        top=root)
    return menu_top.menu


def experiments_from_db(session):
    return session.query(schema.Experiment).all()


def get_completed_runs(session, exp):
    return session.query(sa.func.count(schema.Run.id)).\
        filter(schema.Run.experiment_group == exp.id).\
        filter(schema.Run.status == 'completed').scalar()


def get_failed_runs(session, exp):
    return session.query(sa.func.count(schema.Run.id)).\
        filter(schema.Run.experiment_group == exp.id).\
        filter(schema.Run.status != 'completed').scalar()
