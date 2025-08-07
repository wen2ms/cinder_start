import logging


LOG = logging.getLogger(__name__)


class BinderException(Exception):
    message = "An unknown exception occurred."
    code = 500
    safe = False

    def __init__(self, message = None, **kwargs):
        self.kwargs = kwargs
        if message is not None:
            self.message = message
        else:
            try:
                self.message = self.message % kwargs
            except Exception:
                self._log_exception()
                self.message = self.message

        super().__init__(self.message)

    def _log_exception(self):
        LOG.exception("Exception in string format operation:")
        for name, value in self.kwargs.items():
            LOG.error("%(name)s: %(value)s", {"name": name, "value": value})


class Invalid(BinderException):
    message = "Unacceptable parameters."
    code = 400


class InvalidInput(Invalid):
    message = "Invalid input received: %(reason)s"
