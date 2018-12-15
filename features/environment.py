import behave

from features.support import with_aws_lambda_environment_variables


def before_all(context):
    behave.use_fixture(with_aws_lambda_environment_variables, context)
