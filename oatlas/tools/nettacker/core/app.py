import copy
import json
import os
import socket
from threading import Thread
from types import SimpleNamespace
from typing import List, Optional

import multiprocess

from oatlas.config import Database, Config
from oatlas.logger import get_logger

# Database functions have been moved to the main database manager
from oatlas.tools.nettacker.core.database import (
    mysql_create_tables,
    mysql_create_database,
    sqlite_create_tables,
    postgres_create_database,
)
from oatlas.tools.nettacker.core.database.database import find_events, remove_old_logs

# Commenting this to remind me about this
# from nettacker.core.graph import create_report
from oatlas.tools.nettacker.core.ip import (
    get_ip_range,
    generate_ip_range,
    is_single_ipv4,
    is_ipv4_range,
    is_ipv4_cidr,
    is_single_ipv6,
    is_ipv6_range,
    is_ipv6_cidr,
)

# Will let the messages logic stay cause its not hurting me at this moment
from oatlas.tools.nettacker.core.messages import messages as _
from oatlas.tools.nettacker.core.module import Module
from oatlas.tools.nettacker.core.socks_proxy import set_socks_proxy

# We'll let its own common file as it is, because its big!
from oatlas.tools.nettacker.core.utils import common as common_utils
from oatlas.tools.nettacker.core.utils.common import wait_for_threads_to_finish
from oatlas.utils.die import die_failure

log = get_logger()


class NettackerEngine:
    """
    Functions for nettacker. We're only exposing the run function with a bunch of options.
    """

    def __init__(self):
        self.handle_dependencies()

    def handle_dependencies(self):
        if Database.engine == "sqlite":
            try:
                if not Config.path.database_file.exists():
                    sqlite_create_tables()
            except PermissionError:
                die_failure("cannot access the database directory!")
        elif Database.engine == "mysql":
            try:
                mysql_create_database()
                mysql_create_tables()
            except Exception:
                die_failure("Database connection to MySQL failed!")
        elif Database.engine == "postgres":
            try:
                postgres_create_database()
            except Exception:
                die_failure("Database connection to PostgreSQL failed!")
        else:
            die_failure("Database not yet supported (or invalid)")

    @classmethod
    def expand_targets(cls, options, scan_id):
        targets = []
        base_path = ""
        if isinstance(options.targets, str):
            options.targets = options.targets.split(
                ","
            )  # Now it should be a list and we can accept comma seperated values
        for target in options.targets:
            if "://" in target:
                try:
                    if not target.split("://")[1].split("/")[1]:
                        base_path = ""
                    else:
                        base_path = "/".join(target.split("://")[1].split("/")[1:])
                        if base_path[-1] != "/":
                            base_path += "/"
                except IndexError:
                    base_path = ""
                target = target.split("://")[1].split("/")[0].split(":")[0]
                targets.append(target)
            elif is_single_ipv4(target) or is_single_ipv6(target):
                if options.scan_ip_range:
                    targets += get_ip_range(target)
                else:
                    targets.append(target)
            elif (
                is_ipv4_range(target)
                or is_ipv6_range(target)
                or is_ipv4_cidr(target)
                or is_ipv6_cidr(target)
            ):
                targets += generate_ip_range(target)
            else:
                targets.append(target)
        options.targets = targets
        options.url_base_path = base_path

        # subdomain_scan
        if options.scan_subdomains:
            selected_modules = options.selected_modules
            options.selected_modules = ["subdomain_scan"]
            NettackerEngine.start_scan(options, scan_id)
            options.selected_modules = selected_modules
            if "subdomain_scan" in options.selected_modules:
                options.selected_modules.remove("subdomain_scan")

            for target in copy.deepcopy(options.targets):
                for row in find_events(target, "subdomain_scan", scan_id):
                    for sub_domain in json.loads(row.json_event)["response"]["conditions_results"][
                        "content"
                    ]:
                        if sub_domain not in options.targets:
                            options.targets.append(sub_domain)

        # icmp_scan
        if options.ping_before_scan:
            if os.geteuid() == 0:
                selected_modules = options.selected_modules
                options.selected_modules = ["icmp_scan"]
                NettackerEngine.start_scan(options, scan_id)
                options.selected_modules = selected_modules
                if "icmp_scan" in options.selected_modules:
                    options.selected_modules.remove("icmp_scan")
                options.targets = NettackerEngine.filter_target_by_event(
                    targets, scan_id, "icmp_scan"
                )
            else:
                log.warn(_("icmp_need_root_access"))
                if "icmp_scan" in options.selected_modules:
                    options.selected_modules.remove("icmp_scan")

        # port_scan
        if not options.skip_service_discovery:
            options.skip_service_discovery = True
            selected_modules = options.selected_modules
            options.selected_modules = ["port_scan"]
            NettackerEngine.start_scan(options, scan_id)
            options.selected_modules = selected_modules
            if "port_scan" in options.selected_modules:
                options.selected_modules.remove("port_scan")
            options.targets = NettackerEngine.filter_target_by_event(targets, scan_id, "port_scan")
            options.skip_service_discovery = False

        return list(set(options.targets))

    @classmethod
    def filter_target_by_event(cls, targets, scan_id, module_name):
        for target in copy.deepcopy(targets):
            if not find_events(target, module_name, scan_id):
                targets.remove(target)
        return targets

    # Keeping only this as a staticmethod because of my architecture
    @staticmethod
    def nettacker_run(
        # The targets and selected modules are something we need for sure
        targets: List[str],
        selected_modules: List[str],
        targets_list: Optional[str] = None,
        profiles: Optional[str] = None,
        excluded_modules: Optional[List[str]] = None,
        excluded_ports: Optional[List[str]] = None,
        usernames: Optional[List[str]] = None,
        usernames_list: Optional[str] = None,
        passwords: Optional[List[str]] = None,
        passwords_list: Optional[str] = None,
        ports: Optional[List[str]] = None,
        user_agent: Optional[str] = "Nettacker 0.4.0 QUIN",  # The default nettacker useragent
        timeout: float = 3.0,
        time_sleep_between_requests: float = 0.0,
        scan_ip_range: bool = False,
        scan_subdomains: bool = False,
        skip_service_discovery: bool = True,  # Set this to True when you don't want to do a port scan
        thread_per_host: int = 100,
        parallel_module_scan: int = 1,
        set_hardware_usage: int = 21,
        socks_proxy: Optional[str] = None,
        retries: int = 1,
        ping_before_scan: bool = False,
        read_from_file: Optional[str] = None,
        http_header: Optional[List[str]] = None,
    ):
        """
        Public static entry point for Nettacker. This is derived from the CLI arguments that
        Nettacker expected from ArgParser. This is a complete port of the same.

        It comes at the price of maintaining this sepearately and adding new modules to this
        on my own but its the latest version (we don't get the latest version from pypi) and
        its now custom integrated into the software so I can change its return types and play
        around with it!

        For example, this implementation cannot do any comparisions (undoing all the GSoC work
        done in 2023) because its not very useful for me. Also, there is absolutely no bloat,
        everything is there for a reason. There is no Web server, no frontend scripts, no pretty
        graphs only hardcore usage. I have tried to strip the code as much as I can!

        This is the main run function. Enjoy.
        """
        # Build options object dynamically from arguments
        options = SimpleNamespace(
            targets=targets or [],
            targets_list=targets_list,
            selected_modules=selected_modules or [],
            profiles=profiles,
            excluded_modules=excluded_modules or [],
            excluded_ports=excluded_ports or [],
            usernames=usernames or [],
            usernames_list=usernames_list,
            passwords=passwords or [],
            passwords_list=passwords_list,
            ports=ports or [],
            user_agent=user_agent,
            timeout=timeout,
            time_sleep_between_requests=time_sleep_between_requests,
            scan_ip_range=scan_ip_range,
            scan_subdomains=scan_subdomains,
            skip_service_discovery=skip_service_discovery,
            thread_per_host=thread_per_host,
            parallel_module_scan=parallel_module_scan,
            set_hardware_usage=set_hardware_usage,
            socks_proxy=socks_proxy,
            retries=retries,
            ping_before_scan=ping_before_scan,
            read_from_file=read_from_file,
            http_header=http_header or [],
            # Runtime only
            url_base_path="",
        )

        if isinstance(options.selected_modules, str):
            options.selected_modules = options.selected_modules.split(
                ","
            )  # Again same thing as target

        scan_id = common_utils.generate_random_token(32)
        log.info(f"ScanID: {scan_id}")
        log.info(_("regrouping_targets"))

        options.targets = NettackerEngine.expand_targets(options, scan_id)
        if not options.targets:
            log.error("No targets selected to scan!")
            return True

        exit_code = NettackerEngine.start_scan(options, scan_id)
        log.info(f"ScanID: {scan_id} " + _("done"))
        return exit_code

    @classmethod
    def start_scan(cls, options, scan_id):
        target_groups = common_utils.generate_target_groups(
            options.targets, options.set_hardware_usage
        )
        log.info(_("removing_old_db_records"))

        for target_group in target_groups:
            for target in target_group:
                for module_name in options.selected_modules:
                    remove_old_logs(
                        {
                            "target": target,
                            "module_name": module_name,
                            "scan_id": scan_id,
                        }
                    )

        for _i in range(target_groups.count([])):
            target_groups.remove([])

        log.info(_("start_multi_process").format(len(options.targets), len(target_groups)))
        active_processes = []
        for t_id, target_group in enumerate(target_groups):
            process = multiprocess.Process(
                target=NettackerEngine.scan_target_group,
                args=(options, target_group, scan_id, t_id),
            )
            process.start()
            active_processes.append(process)

        return wait_for_threads_to_finish(active_processes, sub_process=True)

    @classmethod
    def scan_target(
        cls,
        options,
        target,
        module_name,
        scan_id,
        process_number,
        thread_number,
        total_number_threads,
    ):
        # Each thread needs its own copy of the options
        thread_options = copy.deepcopy(options)

        socket.socket, socket.getaddrinfo = set_socks_proxy(thread_options.socks_proxy)
        module = Module(
            module_name,
            thread_options,
            target,
            scan_id,
            process_number,
            thread_number,
            total_number_threads,
        )
        module.load()
        module.generate_loops()
        module.sort_loops()
        module.start()

        log.verbose_event_info(
            _("finished_parallel_module_scan").format(
                process_number, module_name, target, thread_number, total_number_threads
            )
        )

        return os.EX_OK

    @classmethod
    def scan_target_group(cls, options, targets, scan_id, process_number):
        active_threads = []
        log.verbose_event_info(_("single_process_started").format(process_number))
        total_number_of_modules = len(targets) * len(options.selected_modules)
        total_number_of_modules_counter = 1

        for target in targets:
            for module_name in options.selected_modules:
                thread = Thread(
                    target=NettackerEngine.scan_target,
                    args=(
                        options,
                        target,
                        module_name,
                        scan_id,
                        process_number,
                        total_number_of_modules_counter,
                        total_number_of_modules,
                    ),
                )
                thread.name = f"{target} -> {module_name}"
                thread.start()
                log.verbose_event_info(
                    _("start_parallel_module_scan").format(
                        process_number,
                        module_name,
                        target,
                        total_number_of_modules_counter,
                        total_number_of_modules,
                    )
                )
                total_number_of_modules_counter += 1
                active_threads.append(thread)
                if not wait_for_threads_to_finish(
                    active_threads, options.parallel_module_scan, True
                ):
                    return False
        wait_for_threads_to_finish(active_threads, maximum=None, terminable=True)
        return True
