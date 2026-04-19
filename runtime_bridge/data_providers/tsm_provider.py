import re
import os
from .base_provider import BaseProvider
from utils import log_info

class TSMProvider(BaseProvider):
    def __init__(self, config):
        self.config = config
        self.tsm_path = config.get('tsm_path', 'TradeSkillMaster.lua')
        self.data = None

    def load_data(self):
        if not os.path.exists(self.tsm_path):
            return {}
        with open(self.tsm_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # Simple parser for TSM.db.global.marketData
        # Find marketData table
        match = re.search(r'marketData\s*=\s*\{(.*?)\}', content, re.DOTALL)
        if not match:
            return {}
        table_str = match.group(1)
        # Parse nested tables
        data = self._parse_lua_table(table_str)
        self.data = data
        # Logging
        total_items = len(data)
        region_count = sum(1 for scopes in data.values() if 'region' in scopes)
        realm_count = sum(1 for scopes in data.values() if 'realm' in scopes)
        log_info(f"TSM data loaded: {total_items} items ({region_count} with region data, {realm_count} with realm data)")
        return data

    def _parse_lua_table(self, table_str):
        # Very basic parser for TSM marketData
        # Assumes format ["item:id"] = {regionMarket={...}, realmMarket={...}}
        data = {}
        # Split by ["item:id"]
        items = re.findall(r'\["(item:\d+)"\]\s*=\s*\{(.*?)\}', table_str, re.DOTALL)
        for item_id, item_data in items:
            item_dict = {}
            # Parse regionMarket and realmMarket
            region_match = re.search(r'regionMarket\s*=\s*\{(.*?)\}', item_data, re.DOTALL)
            if region_match:
                item_dict['region'] = self._parse_market_data(region_match.group(1))
            realm_match = re.search(r'realmMarket\s*=\s*\{(.*?)\}', item_data, re.DOTALL)
            if realm_match:
                item_dict['realm'] = self._parse_market_data(realm_match.group(1))
            data[item_id] = item_dict
        return data

    def _parse_market_data(self, data_str):
        # Parse key=value pairs
        market = {}
        pairs = re.findall(r'(\w+)\s*=\s*([^,\}]+)', data_str)
        for key, value in pairs:
            value = value.strip()
            if value.isdigit():
                market[key] = int(value)
            elif '.' in value and value.replace('.', '').isdigit():
                market[key] = float(value)
            else:
                market[key] = value.strip('"')
        return market

    def get_data(self, query):
        if self.data is None:
            self.load_data()
        if not self.data:
            return "No TSM data loaded"
        if query == 'all':
            return self.data
        # Filter by query (item name or id)
        results = {}
        for item_id, scopes in self.data.items():
            if query.lower() in item_id.lower():
                results[item_id] = scopes
        return results if results else "No matching items found"
