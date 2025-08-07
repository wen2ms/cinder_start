# Cinder Code Start

## 1. 入口

- 基于devstack安装

    ```sh
    sudo systemctl status "devstack@c-*
    
    ● devstack@c-api.service - Devstack devstack@c-api.service
         Loaded: loaded (/etc/systemd/system/devstack@c-api.service; enabled; preset: enabled)
    ```
    
- 查看 .service config

    ```
     ExecStart = /bin/uwsgi --procname-prefix cinder-api --ini /etc/cinder/cinder-api-uwsgi.ini --venv /opt/stack/data/venv
    ```

- 查看/etc/cinder/cinder-api-uwsgi.ini

    ```
    module = cinder.wsgi.api:application
    ```
    

## 2. 代码结构

- 根目录

```sh
.
├── api-ref 
├── bindep.txt
├── cinder # cinder核心代码，包含cinder-api,scheduler, volume manager, driver等模块
├── CONTRIBUTING.rst
├── conversion # 数据库或配置迁移工具
├── doc # 文档
├── driver-requirements.txt
├── etc
├── HACKING.rst
├── LICENSE
├── mypy-files.txt
├── playbooks
├── rally-jobs
├── README.rst
├── releasenotes
├── reno.yaml
├── requirements.txt
├── roles
├── ruff.toml
├── setup.cfg
├── setup.py
├── test-requirements.txt
├── tools
└── tox.ini
```

- cinder/

```sh
.
├── api # REST API的定义
├── backup
├── brick
├── cmd # 服务入口，cinder-api, cinder-volume
├── common
├── compute
├── context.py
├── coordination.py
├── db # 数据库访问层
├── exception.py
├── flow_utils.py
├── group
├── i18n.py
├── image
├── __init__.py
├── interface
├── keymgr
├── locale
├── manager.py
├── message
├── objects
├── opts.py
├── policies
├── policy.py
├── privsep
├── __pycache__
├── quota.py
├── quota_utils.py
├── rpc.py
├── scheduler # 调度器，决定存储后端
├── service_auth.py
├── service.py
├── ssh_utils.py
├── tests # 单元测试，使用tox
├── transfer
├── utils.py
├── version.py
├── volume # 卷管理核心
├── wsgi
└── zonemanager
```

### Create Volume
- 流程

![Create Volume](./create_volume.png)

- 入口

  ``` python
  # cinder.api.v3.volume.VolumeController.create

  # 进入cinder-api层
  def create(self, req, body)

  # 封装了认证信息、project、user、权限等
  context = req.environ['cinder.context']

  # 调用Volume API进行RPC调度转到scheduler
  # self.volume_api = cinder.volume.cinder_volume.API()
  try:
      new_volume = self.volume_api.create(
          context, size, volume.get('display_name'),
          volume.get('display_description'), **kwargs)
  except exception.VolumeTypeDefaultMisconfiguredError as err:
      raise exc.HTTPInternalServerError(explanation=err.msg)

  # 构建response返回给Client
  retval = self._view_builder.detail(req, new_volume)
  return retval
  ```

- 疑似的bug

    ```python
    volume = body['volume']
    kwargs = {}
    
    self.validate_name_and_description(volume, check_length=False)
    ```

    `validate_name_and_description`是用来检查volume的各个属性是否满足一定的条件，它调用的是：
    
    ```python
    # cinder.api.openstack.wsgi
    
    @staticmethod
    def validate_name_and_description(body, check_length=True):
        for attribute in ['name', 'description',
                          'display_name', 'display_description']:
            value = body.get(attribute)
            if value is not None:
                if isinstance(value, str):
                    # 疑似bug
                    body[attribute] = value.strip()
                if check_length:
                    try:
                        utils.check_string_length(body[attribute], attribute,
                                                  min_length=0, max_length=255)
                    except exception.InvalidInput as error:
                        raise webob.exc.HTTPBadRequest(explanation=error.msg)
    ```
    
    核心函数在`cinder.utils`：
    
    ```python
    def check_string_length(value: str, name: str, min_length: int = 0,
                        max_length: Optional[int] = None,
                        allow_all_spaces: bool = True) -> None:
    try:
        # oslo_utils.strutils
        strutils.check_string_length(value, name=name,
                                     min_length=min_length,
                                     max_length=max_length)
    except (ValueError, TypeError) as exc:
        raise exception.InvalidInput(reason=exc)
    
    # 疑似bug
    if not allow_all_spaces and value.isspace():
        msg = _('%(name)s cannot be all spaces.')
        raise exception.InvalidInput(reason=msg)
    ```
    

    - 如果一个字符串是空格串，例如`"     "`，那么经过`value.strip`后字符串会变成`""`，长度为0，那么`value.isspace()`为`False`。

    - 如果`check_length`为`Flase`那么就不会检查`value`是否为空格串了。

- 异常类的分析

    ```python
    class CinderException(Exception):
        def __init__(self, message: Optional[Union[str, tuple]] = None, **kwargs):
            self.kwargs = kwargs
            self.kwargs['message'] = message
            
            if self._should_format():
                try:
                    message = self.message % kwargs
                except Exception:
                    self._log_exception()
                    message = self.message
            elif isinstance(message, Exception):
                message = str(message)
    
    class Invalid(CinderException):
        message = "Unacceptable parameters."
        code = 400
        
    class InvalidInput(Invalid):
        message = "Invalid input received: %(reason)s"
    ```

    通过`message = self.message % kwargs`得到格式化后的字符串，例如当校验数据过长时：
    
    ```
    "Invalid input received: %(reason)s" % {"reason": "Failed: Invalid input received: name has 4496 characters, more than 255."}
    ```