
import json
from pathlib import Path

DEMOGRAPHIC_KEY = "demographic_data"
AIH_KEY = "hospitalisation"
APAC_KEY = "outpatient_high_complexity_procedures"


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def sorted_json_files(folder):

    return sorted(
        Path(folder).glob("*.json"),
        key=lambda x: x.name
    )


def merge_dataset(
    demographic_dir,
    aih_dir,
    apac_dir,
    output_dir
):

    demographic_files = sorted_json_files(
        demographic_dir
    )

    aih_files = sorted_json_files(
        aih_dir
    )

    apac_files = sorted_json_files(
        apac_dir
    )

    max_records = max(
        len(demographic_files),
        len(aih_files),
        len(apac_files)
    )

    output_dir = Path(output_dir)

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    merged_count = 0

    for idx in range(max_records):

        demographic_doc = (
            load_json(demographic_files[idx])
            if idx < len(demographic_files)
            else None
        )

        aih_doc = (
            load_json(aih_files[idx])
            if idx < len(aih_files)
            else None
        )

        apac_doc = (
            load_json(apac_files[idx])
            if idx < len(apac_files)
            else None
        )

        merged_record = {
            "_record_id": idx + 1,

            DEMOGRAPHIC_KEY: demographic_doc,

            AIH_KEY: aih_doc,

            APAC_KEY: apac_doc
        }

        output_file = (
            output_dir
            / f"merged_{idx+1:06d}.json"
        )

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                merged_record,
                f,
                indent=2,
                ensure_ascii=False
            )

        merged_count += 1

    print(
        f"[OK] Created {merged_count} merged records"
    )


if __name__ == "__main__":

    merge_dataset(
        demographic_dir="dataset/demographic",
        aih_dir="dataset/aih",
        apac_dir="dataset/apac",
        output_dir="dataset/merged"
    )
