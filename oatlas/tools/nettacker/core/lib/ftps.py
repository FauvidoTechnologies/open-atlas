import ftplib

from oatlas.tools.nettacker.core.lib.ftp import FtpEngine, FtpLibrary


class FtpsLibrary(FtpLibrary):
    client = ftplib.FTP_TLS


class FtpsEngine(FtpEngine):
    library = FtpsLibrary
