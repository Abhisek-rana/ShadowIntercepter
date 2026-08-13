import itertools

MARKER = "§"


def split_template(template: str):
    return template.split(MARKER)


def get_position_count(template: str):
    parts = split_template(template)
    return (len(parts) - 1) // 2


def build_request(parts, payloads):
    result = parts[0]
    for i, payload in enumerate(payloads):
        result += payload + parts[2 * i + 2]
    return result


def sniper_combinations(parts, payload_list):
    num_positions = (len(parts) - 1) // 2
    originals = [parts[2 * i + 1] for i in range(num_positions)]

    combos = []
    for pos in range(num_positions):
        for payload in payload_list:
            values = list(originals)
            values[pos] = payload
            combos.append(values)
    return combos


def battering_ram_combinations(parts, payload_list):
    num_positions = (len(parts) - 1) // 2
    combos = []
    for payload in payload_list:
        combos.append([payload] * num_positions)
    return combos


def pitchfork_combinations(parts, payload_lists):
    min_len = min(len(lst) for lst in payload_lists)
    combos = []
    for i in range(min_len):
        combos.append([payload_lists[p][i] for p in range(len(payload_lists))])
    return combos


def cluster_bomb_combinations(parts, payload_lists):
    combos = [list(combo) for combo in itertools.product(*payload_lists)]
    return combos


def generate_requests(template, attack_type, payload_list1, payload_list2=None):
    parts = split_template(template)

    if attack_type == "sniper":
        combos = sniper_combinations(parts, payload_list1)
    elif attack_type == "battering_ram":
        combos = battering_ram_combinations(parts, payload_list1)
    elif attack_type == "pitchfork":
        combos = pitchfork_combinations(parts, [payload_list1, payload_list2])
    elif attack_type == "cluster_bomb":
        combos = cluster_bomb_combinations(parts, [payload_list1, payload_list2])
    else:
        combos = []

    results = []
    for combo in combos:
        req_string = build_request(parts, combo)
        results.append((combo, req_string))

    return results