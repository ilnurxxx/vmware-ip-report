#!/usr/bin/env python3
import logging
import argparse
from src.connector import connect
from src.collector import get_properties, collect_portgroups, collect_dvpgs
from src.handler import process_vm
from src.exporter import export_report
from tqdm import tqdm
import os
from pathlib import Path


def setup_logging():
    """
    Настройки логирования
    """
    root_dir = Path(__file__).resolve().parent

    logs_dir = os.path.join(root_dir, "logs_dir")
    reports_dir = os.path.join(root_dir, "reports")
    
    os.makedirs(logs_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        handlers=[
            logging.FileHandler(f"{logs_dir}/report.log", encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
    
    
def main():
    parser = argparse.ArgumentParser(description="VMWare IP Report")

    # режимы экспорта
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--get-excel", action="store_true", help="export to .xlsx")
    group.add_argument("--get-csv", action="store_true", help="export to .csv")
    group.add_argument("--get-json", action="store_true", help="return to stdout json")
    
    # дополнительные опции
    parser.add_argument("--quiet", action="store_true", help="only critical logs")

    args = parser.parse_args()
    
    setup_logging()
    logger = logging.getLogger(__name__)
    root_logger = logging.getLogger()

    if args.quiet:
        root_logger.setLevel(logging.CRITICAL)
        logging.getLogger().critical("--quiet: show only critical errors")
    else:
        root_logger.setLevel(logging.INFO)

    try:
        si = connect()
        content = si.RetrieveContent()

        logger.info("Сбор кэша PortGroups...")
        host_pg_dict = collect_portgroups(content)
        dvpg_dict = collect_dvpgs(content)

        logger.info("Получение списка ВМ...")
        vm_objects = get_properties(content)

        logger.info("Обработка ВМ...")
        results = []
        for vm_obj in tqdm(vm_objects, desc="Обработка ВМ", unit="vm"):
            result = process_vm(vm_obj, host_pg_dict, dvpg_dict)
            if result:
                results.append(result)

        # Export module
        if args.get_excel:
            export_report(results, mode="excel")
        elif args.get_csv:
            export_report(results, mode="csv")
        elif args.get_json:
            export_report(results, mode="json")

    except Exception as e:
        logger.critical(f"Критическая ошибка: {e}")
        raise

if __name__ == "__main__":
    main()