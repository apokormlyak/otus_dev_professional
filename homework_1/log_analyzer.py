import gzip
import argparse
import json
from itertools import groupby
from pathlib import Path
import logging
import re
from string import Template
import os.path

# !/usr/bin/env python
# -*- coding: utf-8 -*-


# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';
FORMAT = "[%(asctime)s] %(levelname).1s %(message)s"
logging.basicConfig(format=FORMAT, filename="", level=logging.INFO)

config = {"REPORT_SIZE": 1000, "REPORT_DIR": "./reports", "LOG_DIR": "./log"}
FILE_DIR = os.path.dirname(__file__)
parser = argparse.ArgumentParser(description="Log parser")
parser.add_argument("--config", dest="config", default=config, help="Path to config")
args = parser.parse_args()

LOGGER = logging.getLogger(__name__)


def get_config():
    if args.config != config:
        with open(args.config, "r") as f:
            data = json.load(f)
            return {**config, **data}
    else:
        return config


def grouper(item):
    return item["url"]


def get_log_file():
    result_config = get_config()
    path = Path(result_config["LOG_DIR"])
    logs = [file for file in path.glob("*") if str(file).find("nginx-access-ui.log-")]
    log_file = max(logs)
    date = str(log_file).split("-")[-1].split(".")[0]
    LOGGER.info(f"Последний файл с логами {max(logs)}")
    return log_file, date


def log_reader(file):
    try:
        reader = gzip.open if str(file).endswith(".gz") else open
        with reader(file, "rt", encoding="utf-8") as f:
            for line in f:
                yield line
    except TypeError:
        LOGGER.error("Файл с логами не передан")
        return None
    except IOError:
        LOGGER.error("Файл с логами не найден")
        return None


def log_finder(file):
    exeptions_counter = 0
    line_counter = 0
    for line in log_reader(file):
        try:
            url = re.search(r" /(.*) H", line).group().strip().split(" ")[0]
            request_time = re.search(r"([0-9][.])?[0-9]+$", line).group()
            line_counter += 1
            yield url, request_time
        except AttributeError:
            exeptions_counter += 1
            LOGGER.exception(AttributeError)
        if not check_errors_percent(line_counter, exeptions_counter):
            LOGGER.exception("Большую часть анализируемого лога не удалось распарсить")
            LOGGER.exception("Прерываю")
            break
    return None


def check_errors_percent(lines, exeptions_counter):
    try:
        if (exeptions_counter / lines) * 100 > 50:
            return False
        return True
    except ZeroDivisionError:
        LOGGER.error("lines == 0")
        return None


def log_analyzer(file):
    try:
        table_json = []
        report = []
        total_requests_num = 0
        total_requests_time = float(0)
        for line in log_finder(file):
            total_requests_num += 1
            total_requests_time += float(line[1])
            line_data = {"url": line[0], "count": 1, "time_sum": float(line[1])}
            table_json.append(line_data)
        LOGGER.info("Файл считан. Запускаю анализ")
        table_json = sorted(table_json, key=grouper)
        for key, group_items in groupby(table_json, key=grouper):
            grouped_items = [item for item in group_items]
            request_time = [item["time_sum"] for item in grouped_items]
            count = len(grouped_items)
            time_sum = round(sum(request_time), 3)
            line_data = {
                "url": key,
                "count": count,
                "count_perc": get_count_perc(count, total_requests_num),
                "time_sum": time_sum,
                "time_perc": get_time_perc(time_sum, total_requests_time),
                "time_avg": round(time_sum / count, 3),
                "time_max": max(request_time),
                "time_med": get_mediana(request_time),
            }
            report.append(line_data)
        with open("table_json.json", "w") as f:
            json.dump(report, f, indent=4)
            LOGGER.info("Файл table_json.json сформирован")
    except TypeError:
        LOGGER.error("Файл с логами не передан")
        LOGGER.error("Прерываю")


def get_mediana(request_time):
    LOGGER.debug("Считаем медиану")
    try:
        index = int(len(request_time) / 2)
        if len(request_time) % 2 == 0:
            return round((request_time[index - 1] + request_time[index]) / 2, 3)
        else:
            return request_time[index]
    except TypeError:
        LOGGER.error("Передан недопустимый тип данных")
        return None


def get_count_perc(count, total_requests_num):
    LOGGER.debug("Считаем процент запросов на url")
    try:
        return round(count / total_requests_num * 100, 3)
    except ZeroDivisionError:
        LOGGER.error("total_requests_num == 0")
        return None


def get_time_perc(time_sum, total_requests_time):
    LOGGER.debug("Считаем процент времени запросов на url")
    try:
        return round(time_sum / total_requests_time * 100, 3)
    except ZeroDivisionError:
        LOGGER.error("total_requests_num == 0")
        return None


def render_report(date):
    LOGGER.info("Начинаю сборку отчета")
    try:
        with open("report.html", "r") as f:
            data = f.read()
            template = Template(data)
            with open("table_json.json", "r") as json_f:
                table_json = json.load(json_f)
        report_name = "report-" + date + ".html"
    except IOError:
        LOGGER.error("Во время работы с файлом table_json.json возникла ошибка")
        LOGGER.error(IOError)
        return None
    try:
        with open(report_name, "w+", encoding="UTF-8", errors="replace") as html_output:
            html_output.write(template.safe_substitute(table_json=table_json))
            # html_output.truncate()
            LOGGER.info(f"Отчет {report_name} готов")
    except IOError:
        LOGGER.error(f"Во время записи отчета {report_name} возникла ошибка")
        LOGGER.error(IOError)
        return None


def main():
    file, date = get_log_file()
    log_analyzer(file)
    render_report(date)


if __name__ == "__main__":
    main()
