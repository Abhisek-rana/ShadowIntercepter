from src.history.history_store import history


class SiteMapBuilder:
    def __init__(self):
        self.session_start_id = self._get_max_id()

    def _get_max_id(self):
        entries = history.get_all()
        if not entries:
            return 0
        return max(e["id"] for e in entries)

    def reset_session(self):
        self.session_start_id = self._get_max_id()

    def build(self):
        site_map = {}

        for entry in history.get_all():
            if entry["id"] <= self.session_start_id:
                continue

            req = entry["request"]
            resp = entry.get("response")

            host = req.get("host", "unknown")
            path = req.get("path", "/")
            method = req.get("method", "")
            status = resp.get("status_code", "N/A") if resp else "N/A"

            if host not in site_map:
                site_map[host] = {}

            site_map[host][path] = {
                "method": method,
                "status": status,
            }

        return site_map

    def print_tree(self):
        site_map = self.build()
        for host, paths in site_map.items():
            print(f"{host}")
            for path, info in paths.items():
                print(f"  └── {path}  [{info['method']}] -> {info['status']}")


sitemap = SiteMapBuilder()