import json
from pathlib import Path

import seaborn as sns
import matplotlib.pyplot as plt


def main() -> None:
    registry_responses = Path("entries").glob("**/registry_response.json")
    registrar_counts: dict[str, int] = {}
    for response in registry_responses:
        data: dict = json.loads(response.read_text())
        entity: dict = data.get("entities")[0]
        assert entity.get("roles")[0] == "registrar"
        vcard = entity.get("vcardArray")[1]
        fn = vcard[1]
        assert fn[0] == "fn"
        registrar_name = fn[3]
        if registrar_name not in registrar_counts:
            registrar_counts[registrar_name] = 0
        registrar_counts[registrar_name] += 1

    sns.barplot(registrar_counts)
    plt.show()


if __name__ == "__main__":
    main()
