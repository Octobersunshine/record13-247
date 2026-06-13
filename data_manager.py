import json
import os
from typing import Dict, Optional, Tuple


class LotteryDataManager:
    def __init__(self, data_file: str = "lottery_data.json"):
        self.data_file = data_file
        self.winning_codes: Dict[str, Dict] = {}
        self._load_data()

    def _load_data(self) -> None:
        if os.path.exists(self.data_file):
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.winning_codes = data.get("winning_codes", {})
        else:
            self._init_sample_data()
            self._save_data()

    def _save_data(self) -> None:
        data = {"winning_codes": self.winning_codes}
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _init_sample_data(self) -> None:
        sample_winners = {
            "2024001001": {
                "code": "2024001001",
                "name": "张三",
                "plate_number": "京A12345",
                "lottery_round": "2024年第1期",
                "win_date": "2024-01-15"
            },
            "2024001002": {
                "code": "2024001002",
                "name": "李四",
                "plate_number": "京A67890",
                "lottery_round": "2024年第1期",
                "win_date": "2024-01-15"
            },
            "2024002001": {
                "code": "2024002001",
                "name": "王五",
                "plate_number": "京B11111",
                "lottery_round": "2024年第2期",
                "win_date": "2024-02-15"
            },
            "2024002002": {
                "code": "2024002002",
                "name": "赵六",
                "plate_number": "京B22222",
                "lottery_round": "2024年第2期",
                "win_date": "2024-02-15"
            },
            "2024003001": {
                "code": "2024003001",
                "name": "孙七",
                "plate_number": "京C33333",
                "lottery_round": "2024年第3期",
                "win_date": "2024-03-15"
            }
        }
        self.winning_codes = sample_winners

    def query(self, code: str) -> Tuple[bool, Optional[Dict]]:
        code = code.strip()
        if code in self.winning_codes:
            return True, self.winning_codes[code]
        return False, None

    def add_winner(self, code: str, name: str, plate_number: str, 
                   lottery_round: str, win_date: str) -> bool:
        code = code.strip()
        if code in self.winning_codes:
            return False
        self.winning_codes[code] = {
            "code": code,
            "name": name,
            "plate_number": plate_number,
            "lottery_round": lottery_round,
            "win_date": win_date
        }
        self._save_data()
        return True

    def get_all_winners(self) -> Dict[str, Dict]:
        return self.winning_codes

    def remove_winner(self, code: str) -> bool:
        code = code.strip()
        if code in self.winning_codes:
            del self.winning_codes[code]
            self._save_data()
            return True
        return False
