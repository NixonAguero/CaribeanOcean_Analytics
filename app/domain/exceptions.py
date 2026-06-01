class DomainException(Exception):
    pass


class InvalidDateRangeError(DomainException):
    def __init__(self):
        super().__init__("start_date debe ser menor o igual a end_date")


class EmptyResultError(DomainException):
    def __init__(self, resource: str):
        super().__init__(f"Theres no data for: {resource}")
        self.resource = resource
