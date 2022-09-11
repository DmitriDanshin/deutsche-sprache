class Error:
    def __init__(
            self, exception: str,
            module: str, url: str,
            msg: str, status_code: int
    ):
        """
        :param exception: An exception
        :param module: A module where an exception occurred
        :param url: A url of parsed resource
        :param msg: A message with additional information
        :param status_code: A status code of request
        """

        self.exception = exception
        self.module = module
        self.msg = msg
        self.url = url
        self.status_code = status_code

    def json(self, ) -> dict[str, str]:
        return {
            "msg": self.msg,
            "type": self.exception,
            "module": self.module,
            "url": self.url,
            "status_code": self.status_code
        }
