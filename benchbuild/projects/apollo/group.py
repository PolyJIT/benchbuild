from benchbuild.project import Project


class ApolloGroup(Project):
    GROUP = 'apollo'

    path_suffix = "src"

    def __init__(self, exp):
        super(ApolloGroup, self).__init__(exp, self.GROUP)
