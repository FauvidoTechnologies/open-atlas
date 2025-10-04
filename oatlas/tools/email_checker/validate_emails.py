# Copyright (c) 2025 Achintya Jai
# This file is part of the Atlas project.
# All rights reserved. Unauthorized use prohibited.

import random
import re
import smtplib

import dns.resolver

from oatlas import logger
from oatlas.config import Config
from oatlas.utils.common import read_from_file


def send_smtp_probes(mx_host, email, valid_codes) -> bool:
    valid_emails = read_from_file(Config.path.emails)
    from_email = random.choice(valid_emails)

    server = smtplib.SMTP(timeout=10)
    server.connect(mx_host, 25)
    server.helo(from_email.split("@")[1])
    server.mail(from_email)
    code, _ = server.rcpt(email)
    server.quit()
    if code in valid_codes:
        return True
    return False


log = logger.get_logger()


class EmailCheckEngine:
    """
    Class to hold all email checking functions. This takes in the email and verifies it using:
    1. regex matching
    2. existence of domain
    3. MX records and SMTP connection
    Args:
            email_address: The email address that needs to be verified
    Returns:
            boolean: True/False
    """

    def __init__(self) -> None:
        log.warn("Email verification via SMTP starting")

    @staticmethod
    def validate_regex(email) -> bool:
        """
        Simple regex matching of the email address

        Returns:
                boolean: True/False
        """
        regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(regex, email) is not None

    @staticmethod
    def validate_domain(email) -> bool:
        """
        Check if the email address domain exists

        Returns:
                boolean: True/False
        """
        try:
            domain = email.split("@")[1]
            dns.resolver.resolve(domain, "MX")
            return True
        except (dns.resolver.NXDOMAIN, dns.name.EmptyLabel):
            return False

    @staticmethod
    def validate_mailbox(email) -> bool:
        """
        Creates an SMTP server and tries to establish communication with the mailbox
        Note:
                Some institutional firewalls block SMTP probes. Make sure your's isn't blocked

        Returns:
                boolean: True/False
        """
        domain = email.split("@")[1]
        valid_codes = (250, 251)

        try:
            mx_records = dns.resolver.resolve(domain, "MX")
            mx_host = str(sorted(mx_records, key=lambda r: r.preference)[0].exchange)

            return send_smtp_probes(mx_host=mx_host, email=email, valid_codes=valid_codes)
        except Exception:
            return False

    @staticmethod
    def verify_email_address(email) -> bool:
        """
        The main function which consolidates all the others

        Returns:
                Boolean: True/False
        """

        log.warn("Make sure you're not behing a firewall!")
        regex_validation_flag = False
        domain_validation_flag = False
        mailbox_validation_flag = False
        if EmailCheckEngine.validate_regex(email):
            regex_validation_flag = True
            if EmailCheckEngine.validate_domain(email):
                domain_validation_flag = True
                if EmailCheckEngine.validate_mailbox(email):
                    mailbox_validation_flag = True
                    return True
        return {
            "is_regex_valid": regex_validation_flag,
            "is_domain_valud": domain_validation_flag,
            "is_mailbox_valid": mailbox_validation_flag,
        }

    @classmethod
    def get_abbr():
        return "ecE"
