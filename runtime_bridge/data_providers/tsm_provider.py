import re
import os
import time
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
        # Find TradeSkillMasterDB table
        start = content.find('TradeSkillMasterDB = {')
        if start == -1:
            return {}
        start += len('TradeSkillMasterDB = {')
        brace_count = 1
        end = start
        while end < len(content) and brace_count > 0:
            if content[end] == '{':
                brace_count += 1
            elif content[end] == '}':
                brace_count -= 1
            end += 1
        block = content[start:end-1]
        log_info(f"Block len: {len(block)} chars")
        tsm_data = self._parse_lua_table(block)
        log_info(f"Parsed {len(tsm_data)} TSM keys")
        # Extract structured data
        accounting = {}
        inventory = {}
        groups = {}
        operations = {}
        accounting_entries = 0
        inventory_items = 0
        for key, value in tsm_data.items():
            parts = key.split('@', 1)
            if len(parts) < 2:
                continue
            scope_prefix = parts[0]
            path = parts[1]
            realm = path.split('@')[0] if '@' in path else ''
            scope_key = f"{scope_prefix}@{realm}"
            if 'internalData@csv' in path:
                csv_type = path.split('@')[-1]
                if csv_type in ['csvSales', 'csvBuys', 'csvIncome', 'csvExpense', 'csvCancelled', 'csvExpired']:
                    if scope_key not in accounting:
                        accounting[scope_key] = {}
                    parsed = self.parse_csv(value) if isinstance(value, str) else []
                    accounting[scope_key][csv_type] = parsed
                    accounting_entries += len(parsed)
            elif 'internalData@' in path and 'Quantity' in path:
                qty_type = path.split('@')[-1]
                if qty_type in ['bagQuantity', 'bankQuantity', 'mailQuantity', 'auctionQuantity']:
                    if scope_key not in inventory:
                        inventory[scope_key] = {}
                    inventory[scope_key][qty_type] = value
                    inventory_items += len(value) if isinstance(value, dict) else 1
            elif 'groupsManagementGroupTree' in path:
                groups[scope_key] = value
            elif 'shoppingOptions' in path or 'craftingOptions' in path:
                operations[scope_key] = value
        self.data = {'accounting': accounting, 'inventory': inventory, 'groups': groups, 'operations': operations}
        region_account = len([k for k in accounting if k.startswith('r@')])
        realm_account = len(accounting) - region_account
        log_info(f"TSM data loaded: {accounting_entries} accounting entries, {inventory_items} inventory items, {len(groups)} groups, {len(operations)} operations | Region {region_account} realm {realm_account}")
        self.load_auction_data()
        return self.data

    def _parse_lua_table(self, block):
        data = {}
        matches = re.findall(r'\["([^"]+)"\]\s*=\s*(.*?)(?=,\s*\["[^"]*"\]|})', block, re.DOTALL)
        for key, val_str in matches:
            data[key] = self._parse_lua_value(val_str.strip())
        return data

    def _parse_lua_value(self, s):
        s = s.strip()
        if s.startswith('"') and s.endswith('"'):
            return s[1:-1]
        if s.isdigit():
            return int(s)
        if '.' in s and s.replace('.', '').replace('-', '').isdigit():
            return float(s)
        if s == 'true':
            return True
        if s == 'false':
            return False
        if s == 'nil':
            return None
        if s.startswith('{') and s.endswith('}'):
            return self._parse_lua_table(s[1:-1])
        return s  # fallback

    def parse_csv(self, csv_str):
        if not csv_str:
            return []
        lines = csv_str.split('\n')
        result = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            parts = line.split(',')
            if len(parts) >= 8:
                result.append({
                    'itemString': parts[0],
                    'stackSize': int(parts[1]) if parts[1].isdigit() else 0,
                    'quantity': int(parts[2]) if parts[2].isdigit() else 0,
                    'price': int(parts[3]) if parts[3].isdigit() else 0,
                    'otherPlayer': parts[4],
                    'player': parts[5],
                    'time': parts[6],
                    'source': parts[7]
                })
        return result

    def get_data(self, query):
        if self.data is None:
            self.load_data()
        if not self.data:
            return "No TSM data loaded"
        if query == 'all':
            return self.data
        # Filter accounting by itemString
        filtered = {'accounting': {}, 'inventory': self.data['inventory'], 'groups': self.data['groups'], 'operations': self.data['operations']}
        for scope, csvs in self.data['accounting'].items():
            for csv_type, entries in csvs.items():
                if isinstance(entries, list):
                    filtered_entries = [e for e in entries if query.lower() in e.get('itemString', '').lower()]
                    if filtered_entries:
                        if scope not in filtered['accounting']:
                            filtered['accounting'][scope] = {}
                        filtered['accounting'][scope][csv_type] = filtered_entries
        return filtered if any(filtered.values()) else "No matching items found"

    def load_auction_data(self):
        auction_path = self.tsm_path.replace('TradeSkillMaster.lua', 'auctionDB.lua')
        if not os.path.exists(auction_path):
            log_info("auctionDB.lua not found, skipping price data")
            return
        with open(auction_path, 'r', encoding='utf-8') as f:
            content = f.read()
        start = content.find('auctionDB = {')
        if start == -1:
            log_info("auctionDB block not found")
            return
        start += len('auctionDB = {')
        brace_count = 1
        end = start
        while end < len(content) and brace_count > 0:
            if content[end] == '{':
                brace_count += 1
            elif content[end] == '}':
                brace_count -= 1
            end += 1
        block = content[start:end-1]
        log_info(f"AuctionDB block len: {len(block)} chars")
        start_time = time.time()
        auction_data = self._parse_lua_table(block)
        log_info(f"AuctionDB parse took {time.time()-start_time:.2f} seconds")
        prices = {}
        relevant_items = set()
        for scope, group_data in self.data.get('groups', {}).items():
            if isinstance(group_data, dict) and 'collapsed' in group_data:
                relevant_items.update(group_data['collapsed'].keys())
        for scope, inv_data in self.data.get('inventory', {}).items():
            if isinstance(inv_data, dict):
                for qty_type, qty_dict in inv_data.items():
                    if isinstance(qty_dict, dict):
                        relevant_items.update(qty_dict.keys())
        for key, value in auction_data.items():
            parts = key.split('@', 1)
            if len(parts) < 2:
                continue
            scope_prefix = parts[0]
            path = parts[1]
            realm = path.split('@')[0] if '@' in path else ''
            scope_key = f"{scope_prefix}@{realm}"
            if 'internalData@auctionDB' in path:
                if isinstance(value, dict):
                    for item, item_data in value.items():
                        if item in relevant_items and isinstance(item_data, dict):
                            if scope_key not in prices:
                                prices[scope_key] = {}
                            prices[scope_key][item] = {
                                'dbmarket': item_data.get('dbmarket', 0),
                                'historicMedian': item_data.get('historicMedian', 0),
                                'recentAvg': item_data.get('recentAvg', 0),
                                'minBuyout': item_data.get('minBuyout', 0),
                                'numScans': item_data.get('numScans', 0)
                            }
        self.data['prices'] = prices
        count = sum(1 for scope in prices for item in prices[scope] if prices[scope][item].get('dbmarket', 0) > 0)
        log_info(f"AuctionDB loaded: {count} items with price data")
