from oslo_config import cfg

opts = [
    cfg.StrOpt("username", default="admin", help="Username for login"),
    cfg.IntOpt("timeout", default=30, help="Timeout in seconds"),
    cfg.BoolOpt("debug", default=False, help="Enable debug mode"),
]

CONF = cfg.CONF
CONF.register_opts(opts)

print(CONF.username)
print(CONF.timeout)
print(CONF.debug)

group = cfg.OptGroup(name="database", title="Database Options")
db_opts = [cfg.StrOpt("host", default="localhost"), cfg.IntOpt("port", default=3306)]

CONF.register_group(group)
CONF.register_opts(db_opts, group=group)

print(CONF.database.host)

CONF(default_config_files=["foo.conf"])
print(CONF.database.host)
