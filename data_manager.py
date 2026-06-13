import json
import os
from typing import Dict, Optional, Tuple, List, Set


class LotteryDataManager:
    def __init__(self, data_file: str = "lottery_data.json"):
        self.data_file = data_file
        self.rounds: Dict[str, Dict[str, Dict]] = {}
        self._load_data()
        self._validate_data_integrity()

    def _load_data(self) -> None:
        if os.path.exists(self.data_file):
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "rounds" in data:
                    self.rounds = data.get("rounds", {})
                else:
                    self._migrate_old_format(data)
                    self._save_data()
        else:
            self._init_sample_data()
            self._save_data()

    def _validate_data_integrity(self) -> None:
        issues = []
        fixed = False

        for round_name, round_data in self.rounds.items():
            if not isinstance(round_data, dict):
                issues.append(f"期数 {round_name} 数据格式错误，已重置为空")
                self.rounds[round_name] = {}
                fixed = True
                continue

            codes_in_round = set()
            codes_to_remove = []

            for code, info in round_data.items():
                if not isinstance(info, dict):
                    codes_to_remove.append(code)
                    issues.append(f"期数 {round_name} 中编码 {code} 数据格式错误，已移除")
                    continue

                if code in codes_in_round:
                    codes_to_remove.append(code)
                    issues.append(f"期数 {round_name} 中发现重复编码 {code}，已移除重复项")
                    continue

                codes_in_round.add(code)

                info_code = info.get("code", "")
                if info_code != code:
                    info["code"] = code
                    issues.append(f"期数 {round_name} 中编码 {code} 内部数据不一致，已修复")
                    fixed = True

            for code in codes_to_remove:
                del round_data[code]
                fixed = True

            if not round_data:
                del self.rounds[round_name]
                fixed = True

        if fixed:
            self._save_data()
            print(f"⚠️  数据完整性检查发现 {len(issues)} 个问题，已自动修复")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print(f"✅ 数据完整性检查通过，共 {len(self.rounds)} 期数据")

    def _migrate_old_format(self, old_data: Dict) -> None:
        old_winners = old_data.get("winning_codes", {})
        self.rounds = {}
        for code, info in old_winners.items():
            lottery_round = info.get("lottery_round", "未知期数")
            if lottery_round not in self.rounds:
                self.rounds[lottery_round] = {}
            if code not in self.rounds[lottery_round]:
                self.rounds[lottery_round][code] = info
        print(f"数据迁移完成，共迁移 {len(old_winners)} 条记录到 {len(self.rounds)} 个期数")

    def _save_data(self) -> None:
        data = {"rounds": self.rounds}
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _init_sample_data(self) -> None:
        self.rounds = {
            "2024年第1期": {
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
                }
            },
            "2024年第2期": {
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
                }
            },
            "2024年第3期": {
                "2024003001": {
                    "code": "2024003001",
                    "name": "孙七",
                    "plate_number": "京C33333",
                    "lottery_round": "2024年第3期",
                    "win_date": "2024-03-15"
                }
            }
        }

    def query(self, code: str, lottery_round: Optional[str] = None) -> Tuple[bool, List[Dict]]:
        code = code.strip()
        results = []

        if lottery_round:
            lottery_round = lottery_round.strip()
            if lottery_round in self.rounds:
                if code in self.rounds[lottery_round]:
                    results.append(self.rounds[lottery_round][code])
        else:
            for round_data in self.rounds.values():
                if code in round_data:
                    results.append(round_data[code])

        return len(results) > 0, results

    def add_winner(self, code: str, name: str, plate_number: str,
                   lottery_round: str, win_date: str) -> Tuple[bool, str]:
        code = code.strip()
        lottery_round = lottery_round.strip()

        if lottery_round not in self.rounds:
            self.rounds[lottery_round] = {}

        if code in self.rounds[lottery_round]:
            return False, f"编码 {code} 在 {lottery_round} 中已存在"

        self.rounds[lottery_round][code] = {
            "code": code,
            "name": name,
            "plate_number": plate_number,
            "lottery_round": lottery_round,
            "win_date": win_date
        }
        self._save_data()
        return True, "添加成功"

    def get_all_winners(self) -> List[Dict]:
        winners = []
        for round_data in self.rounds.values():
            winners.extend(round_data.values())
        return winners

    def get_rounds(self) -> List[str]:
        return sorted(self.rounds.keys())

    def get_winners_by_round(self, lottery_round: str) -> List[Dict]:
        lottery_round = lottery_round.strip()
        if lottery_round in self.rounds:
            return list(self.rounds[lottery_round].values())
        return []

    def remove_winner(self, code: str, lottery_round: Optional[str] = None) -> Tuple[bool, str]:
        code = code.strip()

        if lottery_round:
            lottery_round = lottery_round.strip()
            if lottery_round in self.rounds and code in self.rounds[lottery_round]:
                del self.rounds[lottery_round][code]
                if not self.rounds[lottery_round]:
                    del self.rounds[lottery_round]
                self._save_data()
                return True, "删除成功"
            return False, f"在 {lottery_round} 中未找到编码 {code}"
        else:
            deleted = False
            for round_name in list(self.rounds.keys()):
                if code in self.rounds[round_name]:
                    del self.rounds[round_name][code]
                    if not self.rounds[round_name]:
                        del self.rounds[round_name]
                    deleted = True
            if deleted:
                self._save_data()
                return True, "删除成功"
            return False, f"未找到编码 {code}"

    def check_duplicate(self, code: str, lottery_round: str) -> bool:
        code = code.strip()
        lottery_round = lottery_round.strip()
        if lottery_round in self.rounds and code in self.rounds[lottery_round]:
            return True
        return False

    def batch_add_winners(self, winners: List[Dict], skip_duplicates: bool = True) -> Dict:
        results = {
            "success": True,
            "added": 0,
            "skipped": 0,
            "failed": 0,
            "details": []
        }

        added_count = 0
        skipped_count = 0
        failed_count = 0

        for winner in winners:
            try:
                code = winner.get("code", "").strip()
                name = winner.get("name", "").strip()
                plate_number = winner.get("plate_number", "").strip()
                lottery_round = winner.get("lottery_round", "").strip()
                win_date = winner.get("win_date", "").strip()

                if not all([code, name, plate_number, lottery_round, win_date]):
                    failed_count += 1
                    results["details"].append({
                    "code": code,
                    "status": "failed",
                    "reason": "缺少必要字段"
                })
                    continue

                if self.check_duplicate(code, lottery_round):
                    if skip_duplicates:
                        skipped_count += 1
                        results["details"].append({
                            "code": code,
                            "status": "skipped",
                            "reason": f"编码在 {lottery_round} 中已存在"
                        })
                    else:
                        failed_count += 1
                        results["details"].append({
                            "code": code,
                            "status": "failed",
                            "reason": f"编码在 {lottery_round} 中已存在"
                        })
                    continue

                if lottery_round not in self.rounds:
                    self.rounds[lottery_round] = {}

                self.rounds[lottery_round][code] = {
                    "code": code,
                    "name": name,
                    "plate_number": plate_number,
                    "lottery_round": lottery_round,
                    "win_date": win_date
                }
                added_count += 1
                results["details"].append({
                    "code": code,
                    "status": "added",
                    "reason": "添加成功"
                })

            except Exception as e:
                failed_count += 1
                results["details"].append({
                    "code": winner.get("code", "unknown"),
                    "status": "failed",
                    "reason": str(e)
                })

        results["added"] = added_count
        results["skipped"] = skipped_count
        results["failed"] = failed_count

        if added_count > 0:
            self._save_data()

        if failed_count > 0 and not skip_duplicates:
            results["success"] = False

        return results

    def get_stats(self) -> Dict:
        total_winners = 0
        round_stats = {}

        for round_name, round_data in self.rounds.items():
            count = len(round_data)
            total_winners += count
            round_stats[round_name] = count

        return {
            "total_rounds": len(self.rounds),
            "total_winners": total_winners,
            "rounds": sorted(round_stats)
        }

    def query_detailed(self, code: str, lottery_round: Optional[str] = None) -> Dict:
        code = code.strip()
        results = []

        if lottery_round:
            lottery_round = lottery_round.strip()
            if lottery_round in self.rounds:
                if code in self.rounds[lottery_round]:
                    results.append(self.rounds[lottery_round][code])
        else:
            for round_name, round_data in sorted(self.rounds.items()):
                if code in round_data:
                    results.append(round_data[code])

        return {
            "code": code,
            "lottery_round": lottery_round,
            "won": len(results) > 0,
            "count": len(results),
            "winners": results,
            "is_duplicate_across_rounds": len(results) > 1
        }
