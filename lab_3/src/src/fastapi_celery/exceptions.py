class BaseException(Exception):
    """Base exception"""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

###########################
#     RS232 EXCEPTIONS    #
###########################


class Rs232ExceptionBase(BaseException):
    """
    Base class for exceptions in Device RS232 module,
    which is responsible for executing of RS232 commands on DUT
    """
    pass


class Rs232Exception(Rs232ExceptionBase):
    def __init__(self, message: str):
        super().__init__(message, status_code=500)

#########################
#     SSH EXCEPTIONS    #
#########################


class SshExceptionBase(BaseException):
    """
    Base class for exceptions in Device SSH module,
    which is responsible for executing of SSH commands on DUT
    """
    pass


class ReceivingPasswordError(SshExceptionBase):
    """Raised when external service for password receive returned error"""

    def __init__(self, message: str):
        super().__init__(message, status_code=500)


###########################
#     IMAGE EXCEPTIONS    #
###########################


class ImageExceptionBase(BaseException):
    """
    Base class for exceptions in Image module,
    which is responsible for receiving and deleting images
    """
    pass


class ImageFileNotFoundError(ImageExceptionBase):
    """Raised when file with image not found"""

    def __init__(self, message: str):
        super().__init__(message, status_code=404)


class ImageNotFoundInDatabaseError(ImageExceptionBase):
    """Raised when image was not found in database"""

    def __init__(self, message: str):
        super().__init__(message, status_code=404)


class UnspecifiedDeviceHostnameError(ImageExceptionBase):
    """Raised when device hostname is not defined in image service"""

    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class EmptyFileExtensionError(ImageExceptionBase):
    """Raised when image does not have extension"""

    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class InvalidFileExtensionError(ImageExceptionBase):
    """Raised when image does not have extension"""

    def __init__(self, message: str):
        super().__init__(message, status_code=400)


############################
#     DEVICE EXCEPTIONS    #
############################


class DeviceDataExceptionBase(BaseException):
    """
    Base class for exceptions in Device Data module
    """
    pass


class DeviceNotFoundError(DeviceDataExceptionBase):
    """Raised when device is not found in database"""

    def __init__(self, message: str):
        super().__init__(message, status_code=404)


class DeviceHasNoImageError(DeviceDataExceptionBase):
    """Raised when device db model does not have related image"""

    def __init__(self, message: str):
        super().__init__(message, status_code=404)

####################################
#     DEVICE RESERVE EXCEPTIONS    #
####################################


class DeviceReserveExceptionBase(BaseException):
    """
    Base class for exceptions in Device Reserve module
    """
    pass


class NotEnoughDevicesError(DeviceReserveExceptionBase):
    """Raised when not enough devices to make reserve request"""

    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class NotEnoughAvailableDevicesError(DeviceReserveExceptionBase):
    """Raised when not enough available devices in database at the moment of request"""

    def __init__(self, message: str):
        super().__init__(message, status_code=500)


class ReservationNotFoundError(DeviceReserveExceptionBase):
    """Raised when reservation not found in database"""

    def __init__(self, message: str):
        super().__init__(message, status_code=500)


###########################
#     BOLID EXCEPTIONS    #
###########################


class BolidExceptionBase(BaseException):
    """
    Base class for exceptions in Bolid module
    """
    pass


class BolidNotFoundError(BolidExceptionBase):
    """Raised when bolid not found in database"""

    def __init__(self, message: str):
        super().__init__(message, status_code=500)


###############################
#     BOLID PIN EXCEPTIONS    #
###############################


class BolidPinExceptionBase(BaseException):
    """
    Base class for exceptions in Bolid Pin module
    """
    pass


class BolidPinNotFoundError(BolidPinExceptionBase):
    """Raised when bolid pin not found in database"""

    def __init__(self, message: str):
        super().__init__(message, status_code=500)


class BolidPinLimitExceededError(BolidPinExceptionBase):
    """Raised when trying to create more pins than a limit"""

    def __init__(self, message: str):
        super().__init__(message, status_code=500)
