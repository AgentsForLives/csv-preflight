"""Run the two fixed-scope services on approved local input files."""
import argparse
import csv
import io
import json
from pathlib import Path

MAX_BYTES = 256 * 1024


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate object key")
        result[key] = value
    return result


def reject_constant(_constant):
    raise ValueError("Non-finite numeric literal")


def validate_json(source):
    try:
        json.loads(source, object_pairs_hook=unique_object, parse_constant=reject_constant)
    except json.JSONDecodeError as error:
        return {"valid": False, "error": error.msg, "line": error.lineno, "column": error.colno}
    except RecursionError:
        return {"valid": False, "error": "JSON nesting exceeds the parser limit"}
    except ValueError as error:
        return {"valid": False, "error": str(error)}
    return {"valid": True}


def write_excel(source, output):
    from openpyxl import Workbook

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Data"
    width = None
    for row_number, row in enumerate(csv.reader(io.StringIO(source, newline=""), strict=True), 1):
        if width is None:
            width = len(row)
        if not width or len(row) != width or width > 100 or row_number > 5000:
            raise ValueError("CSV exceeds sheet limits or has inconsistent row widths")
        for column, value in enumerate(row, 1):
            if len(value) > 32767:
                raise ValueError("Cell exceeds the Excel text limit")
            sheet.cell(row=row_number, column=column, value=value).data_type = "s"
    if width is None:
        raise ValueError("CSV is empty")
    with output.open("xb") as stream:
        try:
            workbook.save(stream)
        except Exception:
            stream.close()
            output.unlink()
            raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("service", choices=["json-validation", "data-to-excel"])
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        with args.source.open("rb") as stream:
            data = stream.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise ValueError("File exceeds the 256 KiB limit")
        if args.service == "json-validation":
            result = validate_json(data.decode("utf-8"))
            with args.output.open("x", encoding="utf-8") as stream:
                json.dump(result, stream)
                stream.write("\n")
        else:
            write_excel(data.decode("utf-8-sig"), args.output)
    except (OSError, ValueError, csv.Error) as error:
        parser.exit(2, f"Error: {error}\n")


if __name__ == "__main__":
    main()
