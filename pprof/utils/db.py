"""Database support module for the pprof study."""
import logging
from pprof.settings import CFG

logger = logging.getLogger(__name__)

def create_run(cmd, prj, exp, grp):
    """
    Create a new 'run' in the database.

    This creates a new transaction in the database and creates a new
    run in this transaction. Afterwards we return both the transaction as
    well as the run itself. The user is responsible for committing it when
    the time comes.

    Args:
        cmd: The command that has been executed.
        prj: The project this run belongs to.
        exp: The experiment this run belongs to.
        grp: The run_group (uuid) we blong to.

    Returns:
        The inserted tuple representing the run and the session opened with
        the new run. Don't forget to commit it at some point.
    """
    from pprof.utils import schema as s

    session = s.Session()
    run = s.Run(command=str(cmd),
                project_name=prj,
                experiment_name=exp,
                run_group=str(grp),
                experiment_group=str(CFG["experiment"]))
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

    session = schema.Session()
    group = schema.RunGroup(id=prj.run_uuid,
                            project=prj.name,
                            experiment=str(CFG["experiment"]))
    session.add(group)
    session.flush()

    return (group, session)


def persist_project(project):
    """
    Persist this project in the pprof database.

    Args:
        project: The project we want to persist.
    """
    from pprof.utils import schema
    session = schema.Session()
    db_project = session.query(schema.Project).filter(schema.Project.name ==
                                                      project.name).first()
    new_project = db_project is None
    if new_project:
        db_project = schema.Project()
    db_project.name = project.name
    db_project.description = project.__doc__
    try:
        db_project.src_url = project.src_uri
    except AttributeError:
        db_project.src_url = 'unknown'

    db_project.domain = project.domain
    db_project.group_name = project.group_name
    session.add(db_project)
    session.commit()
    if new_project:
        logger.debug("New project: %s", db_project)


def persist_experiment(experiment):
    """
    Persist this experiment in the pprof database.

    Args:
        experiment: The experiment we want to persist.
    """
    from pprof.utils import schema

    session = schema.Session()

    cfg_exp = str(CFG['experiment'])
    db_exp = session.query(schema.Experiment).filter(schema.Experiment.id ==
                                                     cfg_exp).first()
    desc = CFG["experiment_description"].value()
    name = db_exp.name = experiment.name

    if db_exp is None:
        db_exp = schema.Experiment()
        db_exp.name = name
        db_exp.description = desc
        session.add(db_exp)
        logger.debug("New experiment: %s", db_exp)
    else:
        db_exp.update({db_exp.name: name, db_exp.description: desc})
    session.commit()

    return (db_exp, session)


def persist_likwid(run, session, measurements):
    """
    Persist all likwid results.

    Args:
        run: The run we attach our measurements to.
        session: The db transaction we belong to.
        measurements: The likwid measurements we want to store.
    """
    from pprof.utils import schema as s

    for (region, name, core, value) in measurements:
        db_measurement = s.Likwid(metric=name,
                                  region=region,
                                  value=value,
                                  core=core,
                                  run_id=run.id)
        session.add(db_measurement)
    session.commit()


def persist_time(run, session, timings):
    """
    Persist the run results in the database.

    Args:
        run: The run we attach this timing results to.
        session: The db transaction we belong to.
        timings: The timing measurements we want to store.
    """
    from pprof.utils import schema as s

    for timing in timings:
        session.add(s.Metric(name="time.user_s",
                             value=timing[0],
                             run_id=run.id))
        session.add(s.Metric(name="time.system_s",
                             value=timing[1],
                             run_id=run.id))
        session.add(s.Metric(name="time.real_s",
                             value=timing[2],
                             run_id=run.id))
    session.commit()


def persist_perf(run, session, svg_path):
    """
    Persist the flamegraph in the database.

    The flamegraph exists as a SVG image on disk until we persist it in the
    database.

    Args:
        run: The run we attach these perf measurements to.
        session: The db transaction we belong to.
        svg_path: The path to the SVG file we want to store.
    """
    from pprof.utils import schema as s

    with open(svg_path, 'r') as svg_file:
        svg_data = svg_file.read()
        session.add(s.Metadata(name="perf.flamegraph",
                               value=svg_data,
                               run_id=run.id))
    session.commit()


def persist_compilestats(run, session, stats):
    """
    Persist the run results in the database.

    Args:
        run: The run we attach the compilestats to.
        session: The db transaction we belong to.
        stats: The stats we want to store in the database.
    """
    for stat in stats:
        stat.run_id = run.id
        session.add(stat)
    session.commit()


def persist_config(run, session, cfg):
    """
    Persist the configuration in as key-value pairs.

    Args:
        run: The run we attach the config to.
        session: The db transaction we belong to.
        cfg: The configuration we want to persist.
    """
    from pprof.utils import schema as s

    for cfg_elem in cfg:
        session.add(s.Config(name=cfg_elem,
                             value=cfg[cfg_elem],
                             run_id=run.id))
    session.commit()
