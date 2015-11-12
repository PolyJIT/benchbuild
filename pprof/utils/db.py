"""Database support module for the pprof study."""
from pprof.settings import config


def create_run(cmd, prj, exp, grp):
    """
    Create a new 'run' in the database.

    This creates a new transaction in the database and creates a new
    run in this transaction. Afterwards we return both the transaction as
    well as the run itself. The user is responsible for committing it when
    the time comes.

    :cmd: The command that has been executed.
    :prj: The project this run belongs to.
    :exp: The experiment this run belongs to.
    :grp: The run_group (uuid) we blong to.
    :returns:
        A serial identifier for the new run and the session opened with
        the new run. Don't forget to commit it at some point.

    """
    from pprof.utils import schema as s

    session = s.Session()
    run = s.Run(command=str(cmd), project_name=prj, experiment_name=exp,
                run_group=str(grp), experiment_group=str(config["experiment"]))
    session.add(run)
    session.flush()

    return (run, session)


def create_run_group(prj):
    """
    Create a new 'run_group' in the database.

    This creates a new transaction in the database and creates a new run_group
    within this transaction. Afterwards we return both the transaction as well
    as the run_group itself. The user is responsible for committing it when the
    time comes.

    Args:
        prj - The project for which we open the run_group.

    Returns:
        A tuple (group, session) containing both the newly created run_group and
        the transaction object.
    """
    from pprof.utils import schema
    from pprof.settings import config

    session = schema.Session()
    group = schema.RunGroup(id=prj.run_uuid, project=prj.name,
                            experiment=config["experiment"])
    session.add(group)
    session.flush()

    return (group, session)


def persist_project(project):
    """ Persist this project in the pprof database. """
    from pprof.utils import schema
    session = schema.Session()
    p = session.query(schema.Project).filter(
        schema.Project.name == project.name).first()
    if p is None:
        p = schema.Project()
    p.name = project.name
    p.description = project.__doc__
    try:
        p.src_url = project.src_uri
    except AttributeError:
        p.src_url = 'unknown'

    p.domain = project.domain
    p.group_name = project.group_name
    session.add(p)
    session.commit()


def persist_experiment(experiment):
    """ Persist this experiment in the pprof database. """
    from pprof.utils import schema

    session = schema.Session()

    e = session.query(schema.Experiment).filter(
        schema.Experiment.id == config['experiment']).first()
    if e is None:
        e = schema.Experiment()
    e.name = experiment.name
    e.description = config["experiment_description"]
    e.id = config['experiment']

    session.add(e)
    session.commit()
    return (e, session)


def persist_likwid(run, session, measurements):
    """ Persist all likwid results. """
    from pprof.utils import schema as s

    for (region, name, core, value) in measurements:
        m = s.Likwid(metric=name, region=region, value=value, core=core,
                     run_id=run.id)
        session.add(m)
    session.commit()


def persist_time(run, session, timings):
    """ Persist the run results in the database."""
    from pprof.utils import schema as s

    for timing in timings:
        session.add(s.Metric(name="time.user_s", value=timing[0],
                             run_id=run.id))
        session.add(s.Metric(name="time.system_s", value=timing[1],
                             run_id=run.id))
        session.add(s.Metric(name="time.real_s", value=timing[2],
                             run_id=run.id))
    session.commit()


def persist_perf(run, session, svg_path):
    """ Persist the flamegraph in the database."""
    from pprof.utils import schema as s

    with open(svg_path, 'r') as svg_file:
        svg_data = svg_file.read()
        session.add(s.Metadata(name="perf.flamegraph", value=svg_data,
                               run_id=run.id))
    session.commit()


def persist_compilestats(run, session, stats):
    """ Persist the run results in the database."""
    for stat in stats:
        stat.run_id = run.id
        session.add(stat)
    session.commit()


def persist_config(run, session, cfg):
    """ Persist the configuration in as key-value pairs."""
    from pprof.utils import schema as s

    for c in cfg:
        session.add(s.Config(name=c, value=cfg[c], run_id=run.id))
    session.commit()
