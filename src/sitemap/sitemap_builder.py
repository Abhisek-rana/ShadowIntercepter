from src.history.history_store import history


class SiteMapBuilder:
    def build(self):
        """
        History se saare entries leke tree structure banata hai:
        {
            "example.com": {
                "/": {"method": "GET", "status": "200"},
                "/login": {"method": "POST", "status": "302"}
            }
        }
        """
        site_map = {}

        for entry in history.get_all():
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
        """Terminal mein readable tree format print karta hai."""
        site_map = self.build()
        for host, paths in site_map.items():
            print(f"{host}")
            for path, info in paths.items():
                print(f"  └── {path}  [{info['method']}] -> {info['status']}")


sitemap = SiteMapBuilder()