from invoke import task

DEFAULT_TAG= ' latest'
decrypted_file = '.env'
encrypted_file = '.env.encrypted'

# Database / ORM commands
@task
def python_shell(ctx):
    """
    Open a python shell on the local web instance
    """
    ctx.run('docker-compose exec api ./manage.py shell_plus', pty=True)


@task
def db_shell(ctx):
    """
    Open a database shell on the local db instance"
    """
    ctx.run('docker-compose exec db psql -U starterkit -d starterkit', pty=True)


@task
def db_wait(ctx):
    """
    Wait for database to start accepting connections and exit
    """
    with ctx.cd('starterkit/'):
        ctx.run("docker-compose exec api ./wait-for-db.sh echo 'database is ready'", pty=True)


# Application commands
@task
def up(ctx):
    """
    Start local instance of api
    """
    ctx.run("docker-compose up")


@task
def up_debug(ctx):
    """
    Start local instance of api with debugging enabled
    """
    ctx.run("docker-compose run --service-ports web")


@task
def up_silent(ctx):
    """
    Start local instance of api silently
    """
    ctx.run("docker-compose up -d")


@task
def stop(ctx):
    """
    Stop local instance of api
    """
    ctx.run("docker-compose stop")


@task
def clean_test(ctx):
    """
    Clean the test environment
    """
    ctx.run("docker-compose -f docker-compose-test.yml down")


@task(clean_test)
def build_test(ctx):
    """
    Build the test environment
    """
    ctx.run("docker-compose -f docker-compose-test.yml build")


@task(clean_test)
def test(ctx, test_label=""):
    """
    Run tests for api
    """
    with ctx.cd('starterkit/'):
        ctx.run("test_label={0} docker-compose -f ../docker-compose-test.yml up --always-recreate-deps --exit-code-from test".format(test_label), pty=True)


@task
def logs(ctx, follow=True):
    """
    Follow logs from api instances
    """
    arg = '-f' if follow else ''
    ctx.run("docker-compose logs {0}".format(arg))


@task
def new_app(ctx, app_label=""):
    """
    Create a new Django application within the Starerkit project
    """
    with ctx.cd('starterkit/'):
        ctx.run("docker-compose exec api ./manage.py startapp {0}".format(app_label), pty=True)


# Database migration commands
@task(db_wait)
def db_loaddata(ctx, color=True):
    """
    Load all fixtures for local development
    """
    with ctx.cd('starterkit/'):
        ctx.run('docker-compose exec api ./manage.py loaddata starterkit/fixtures/*.json', pty=True)


@task(db_wait)
def db_migrate(ctx, app_label="", migration_label=""):
    """
    Run any migrations that are needed
    """
    with ctx.cd('starterkit/'):
        ctx.run("docker-compose exec api ./manage.py migrate {0} {1}".format(app_label, migration_label), pty=True)


@task(db_wait)
def db_makemigrations(ctx, app_label=""):
    """
    Make migration files for the specific app
    """
    with ctx.cd('starterkit/'):
        ctx.run("docker-compose exec api ./manage.py makemigrations {0}".format(app_label), pty=True)


@task(pre=[up_silent], post=[db_migrate, db_loaddata, logs])
def db_create(ctx):
    """
    Create local database for api
    """
    pass


@task(pre=[stop], post=[db_create])
def db_reset(ctx):
    """
    Delete and recreate local database for api
    """
    ctx.run("docker-compose rm db")


@task(pre=[db_wait])
def create_keys(ctx, local_flag=False):
    """
    Create or regenerate API keys. Add -l to create local keys
    """
    local_param = 'local' if local_flag else ''
    ctx.run("docker-compose exec api ./manage.py create_keys {0}".format(local_param), pty=True)


@task()
def show_keys(ctx):
    """
    Display local API keys stored in fixture files
    """
    ctx.run("docker-compose exec api ./manage.py show_keys", pty=True)


# Restarting environment commands
@task(pre=[stop], post=[up_silent])
def images_rebuild(ctx):
    """
    Rebuild api images. Stops and starts api containers.
    """
    ctx.run("docker-compose build")


@task
def encrypt_env(ctx):
    """
    Encrypt .env file that stores environment secrets
    """
    ctx.run("openssl enc -aes256 -base64 -in {0} -out {1}".format(decrypted_file, encrypted_file))


@task
def decrypt_env(ctx, marker=""):
    """
    Decrypt .env.encrypted file
    """
    ctx.run("openssl enc -d -aes256 -base64 -in {0} -out {1}".format(encrypted_file, decrypted_file))


@task
def clean_containers(ctx):
    """
    Delete api containers
    """
    ctx.run("docker-compose down")


@task
def clean_sources(ctx):
    """
    Clean up compiled sources
    """
    ctx.run("find . -name \*.pyc -delete")


@task(pre=[clean_containers, clean_sources])
def clean_all(ctx):
    """
    Run all clean tasks
    """
    pass


@task(pre=[clean_all], post=[images_rebuild, db_reset])
def build(ctx):
    """
    Stop, clean and build everything
    """
    pass


@task(pre=[images_rebuild, up_silent, db_migrate, db_loaddata], post=[logs])
def start(ctx):
    """
    Shortcut to non-destructively update the api: env, images, migrations and fixtures
    """
    ctx.run("docker-compose logs -f")
