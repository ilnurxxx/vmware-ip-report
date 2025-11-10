import pandas as pd
from datetime import datetime
import json
import logging
import os
from pathlib import Path

# Setup logger
logger = logging.getLogger(__name__)


def get_timestamp():
    """
    Получение текущего времени
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def export_report(data, mode):
    """
    Экспорт отчета в зависимости от аргумента
    """
    output_dir = os.path.join(Path(__file__).parent.parent, "reports")
    os.makedirs(output_dir, exist_ok=True)
    df = pd.DataFrame(data)
    timestamp = get_timestamp()

    if mode == "excel":
        path = os.path.join(output_dir, f"vmware_report_{timestamp}.xlsx")
        df.to_excel(path, index=False)
        logger.info(f"Excel сохранен: {path}")

    elif mode == "csv":
        path = os.path.join(output_dir, f"vmware_report_{timestamp}.csv")
        df.to_csv(path, index=False)
        logger.info(f"CSV сохранен: {path}")
    
    elif mode == "json":
        json_output = df.to_json(orient="records", force_ascii=False, indent=2)
        print(json_output)
        logger.info(f"JSON выведен в stdout")

    elif mode == "json-n8n":
        json_output = df.to_dict(orient="records")
        output = {"status": True, "data": json_output}
        print(json.dumps(output, ensure_ascii=False, indent=2))
        logger.info(f"JSON выведен в stdout")

    else:
        raise ValueError(f"Некорректный аргумент: {mode}")