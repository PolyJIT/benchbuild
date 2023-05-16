"""Database support module for the benchbuild study."""
import logging

from benchbuild.settings import CFG

LOG = logging.getLogger(__name__)


def validate(func):

    def validate_run_func(run, session, *args, **kwargs):
        if run.status == 'failed':
            LOG.debug("Run failed. Execution of '%s' cancelled", str(func))
            return None

        return func(run, session, *args, **kwargs)

    return validate_run_func


def create_run(cmd, project, exp, grp):
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
    # pylint: disable=import-outside-toplevel
    from benchbuild.utils import schema as s

    session = s.Session()
    run = s.Run(
        command=str(cmd),
        project_name=project.name,
        project_group=project.group,
        experiment_name=exp.name,
        run_group=str(grp),
        experiment_group=exp.id
    )
    session.add(run)
    session.commit()

    return (run, session)


def create_run_group(prj, experiment):
    """
    Create a new 'run_group' in the database.

    This creates a new transaction in the database and creates a new run_group
    within this transaction. Afterwards we return both the transaction as well
    as the run_group itself. The user is responsible for committing it when the
    time comes.

    Args:
        prj - The project for which we open the run_group.
        experiment - The experiment this group belongs to.

    Returns:
        A tuple (group, session) containing both the newly created run_group and
        the transaction object.
    """
    # pylint: disable=import-outside-toplevel
    from benchbuild.utils import schema as s

    session = s.Session()
    group = s.RunGroup(id=prj.run_uuid, experiment=experiment.id)
    session.add(group)
    session.commit()

    return (group, session)


def persist_project(project):
    """
    Persist this project in the benchbuild database.

    Args:
        project: The project we want to persist.
    """
    from benchbuild.utils.schema import Project, Session
    session = Session()
    projects = session.query(Project) \
        .filter(Project.name == project.name) \
        .filter(Project.group_name == project.group)

    name = project.name
    desc = project.__doc__
    domain = str(project.domain)
    group_name = str(project.group)
    version = str(project.revision)
    try:
        src_url = project.src_uri
    except AttributeError:
        src_url = 'unknown'

    if projects.count() == 0:
        newp = Project()
        newp.name = name
        newp.description = desc
        newp.src_url = src_url
        newp.domain = domain
        newp.group_name = group_name
        newp.version = version
        session.add(newp)
    else:
        newp_value = {
            "name": name,
            "description": desc,
            "src_url": src_url,
            "domain": domain,
            "group_name": group_name,
            "version": version
        }
        projects.update(newp_value)

    session.commit()
    return (projects, session)


def persist_experiment(experiment):
    """
    Persist this experiment in the benchbuild database.

    Args:
        experiment: The experiment we want to persist.
    """
    # pylint: disable=import-outside-toplevel
    from sqlalchemy.exc import IntegrityError

    from benchbuild.utils.schema import Experiment, Session

    session = Session()

    cfg_exp = experiment.id
    LOG.debug("Using experiment ID stored in config: %s", cfg_exp)
    exps = session.query(Experiment).filter(Experiment.id == cfg_exp)
    desc = str(CFG["experiment_description"])
    name = experiment.name

    if exps.count() == 0:
        newe = Experiment()
        newe.id = cfg_exp
        newe.name = name
        newe.description = desc
        session.add(newe)
        ret = newe
    else:
        exps.update({'name': name, 'description': desc})
        ret = exps.first()

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        persist_experiment(experiment)

    return (ret, session)


@validate
def persist_time(run, session, timings):
    """
    Persist the run results in the database.

    Args:
        run: The run we attach this timing results to.
        session: The db transaction we belong to.
        timings: The timing measurements we want to store.
    """
    # pylint: disable=import-outside-toplevel
    from benchbuild.utils import schema as s

    for timing in timings:
        session.add(
            s.Metric(name="time.user_s", value=timing[0], run_id=run.id)
        )
        session.add(
            s.Metric(name="time.system_s", value=timing[1], run_id=run.id)
        )
        session.add(
            s.Metric(name="time.real_s", value=timing[2], run_id=run.id)
        )


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
    # pylint: disable=import-outside-toplevel
    from benchbuild.utils import schema as s

    with open(svg_path, 'r') as svg_file:
        svg_data = svg_file.read()
        session.add(
            s.Metadata(name="perf.flamegraph", value=svg_data, run_id=run.id)
        )


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


def persist_config(run, session, cfg):
    """
    Persist the configuration in as key-value pairs.

    Args:
        run: The run we attach the config to.
        session: The db transaction we belong to.
        cfg: The configuration we want to persist.
    """
    # pylint: disable=import-outside-toplevel
    from benchbuild.utils import schema as s

    for cfg_elem in cfg:
        session.add(s.Config(name=cfg_elem, value=cfg[cfg_elem], run_id=run.id))
