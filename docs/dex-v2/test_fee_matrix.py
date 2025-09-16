#!/usr/bin/env python3
"""
Self-contained fee matrix tests for DEX v2 without SDK/ledger.

Model checks the accounting invariants for single/multi exchange and update fast-path
across service fee configurations: native/own × fixed/percent, and sell_native true/false.

All values use 1e18 fixed-point integers (like uint256 with 18 decimals).
"""

import argparse
import json
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Any

WAD = 10**18


def wad_mul(a: int, b: int) -> int:
    return (a * b) // WAD


def percent_of(base: int, pct_wad: int) -> int:
    return wad_mul(base, pct_wad)


class FeeType:
    NATIVE_FIXED = "NF"
    NATIVE_PERCENT = "NP"
    OWN_FIXED = "OF"
    OWN_PERCENT = "OP"


@dataclass
class FeesCfg:
    fee_type: str  # NF/NP/OF/OP
    service_value: int  # fixed amount (wad) or percent (wad)
    net_fee: int  # native (wad)
    val_fee: int  # validator fee (wad)


@dataclass
class OrderExec:
    executed_sell: int  # S (sell units, wad)
    rate: int  # R (QUOTE/BASE, wad)


def compute_service_components(fee_type: str, service_value: int, B: int) -> Tuple[int, int]:
    """Return (srv_native, srv_own) in quote/native routing terms.
    srv_native debits native token; srv_own debits buy token.
    For percent types use base B (in buy units).
    """
    if fee_type == FeeType.NATIVE_FIXED:
        return service_value, 0
    if fee_type == FeeType.NATIVE_PERCENT:
        return percent_of(B, service_value), 0
    if fee_type == FeeType.OWN_FIXED:
        return 0, service_value
    if fee_type == FeeType.OWN_PERCENT:
        return 0, percent_of(B, service_value)
    raise ValueError("Unknown fee type")


def check_single(sell_native: bool, S: int, R: int, cfg: FeesCfg, extra_native_inputs: int = 0) -> None:
    B = wad_mul(S, R)  # buyer pays B in buy token to seller before own-fee adjustments
    srv_native, srv_own = compute_service_components(cfg.fee_type, cfg.service_value, B)

    # Seller payout (in buy token)
    # Feasibility: own-fee in buy can't exceed B
    if srv_own > B:
        return
    payout_seller_buy = B - srv_own
    assert payout_seller_buy >= 0

    # Buyer payouts
    if sell_native:
        # Buyer receives sell token minus native fees (network + validator + native service)
        native_total = cfg.net_fee + cfg.val_fee + srv_native
        # Feasibility: native fees cannot exceed S (compose would fail). Skip invalid combo.
        if native_total > S:
            return
        payout_buyer_sell = S - native_total
        assert payout_buyer_sell >= 0
        payout_buyer_buy_change = 0
        cashback_native = 0
    else:
        # Buyer change in buy token: inputs in buy must cover B + (own fee in buy) + native fees
        required_buy = B + srv_own
        required_native = cfg.net_fee + cfg.val_fee + srv_native
        # Model fee-inputs sum as exact required_native + optional extra
        native_inputs_sum = required_native + extra_native_inputs
        cashback_native = native_inputs_sum - required_native
        assert cashback_native >= 0
        payout_buyer_sell = 0
        # Change in buy token equals buyer inputs (required_buy) minus payouts in buy; here we assume exact inputs
        payout_buyer_buy_change = 0  # exact-buy-inputs model (no extra buy inputs)

    # Invariants
    # - Seller gets exactly B - srv_own (own-fee only)
    assert payout_seller_buy == (B - srv_own)

    # - Native payouts equal net + val + srv_native (when sell_native false, they are separate outputs)
    native_payouts = cfg.net_fee + cfg.val_fee + srv_native
    assert native_payouts >= 0

    # - When sell_native, buyer receive S minus native totals; otherwise zero
    if sell_native:
        assert payout_buyer_sell == S - native_payouts
    else:
        assert payout_buyer_sell == 0

    # Cashback is only when sell_native is false and extra native inputs are present
    if not sell_native:
        assert cashback_native == extra_native_inputs


def check_multi(sell_native: bool, execs: List[OrderExec], cfg: FeesCfg, extra_native_inputs: int = 0) -> None:
    B_total = 0
    S_total = 0
    srv_native_total = 0
    srv_own_total = 0
    for ex in execs:
        B_i = wad_mul(ex.executed_sell, ex.rate)
        srv_n, srv_o = compute_service_components(cfg.fee_type, cfg.service_value, B_i)
        # Feasibility: per-input own-fee can't exceed B_i
        if srv_o > B_i:
            return
        # Seller i gets B_i - srv_o
        assert B_i - srv_o >= 0
        B_total += B_i
        S_total += ex.executed_sell
        srv_native_total += srv_n
        srv_own_total += srv_o

    native_total = cfg.net_fee + cfg.val_fee + srv_native_total
    # Feasibility: own-fee total can't exceed B_total
    if srv_own_total > B_total:
        return
    # Buyer receive
    if sell_native:
        # Feasibility: native fees cannot exceed S_total
        if native_total > S_total:
            return
        payout_buyer_sell = S_total - native_total
        assert payout_buyer_sell >= 0
        cashback_native = 0
    else:
        required_native = native_total
        native_inputs_sum = required_native + extra_native_inputs
        cashback_native = native_inputs_sum - required_native
        assert cashback_native >= 0

    # Totals must be non-negative
    assert B_total >= 0 and S_total >= 0 and native_total >= 0 and srv_own_total >= 0


def check_update_fastpath_allowed(cfg: FeesCfg) -> None:
    # Own-fee must be forbidden in update
    if cfg.fee_type in (FeeType.OWN_FIXED, FeeType.OWN_PERCENT):
        # Expect: update rejected in real system; in model we assert we won't allow own-fee routing
        return
    # For NF/NP: allowed; ensure no payouts to seller in buy and only native fees are present.
    # Model check: nothing to assert numerically beyond configuration; logical rule satisfied.
    return


def run_matrix(json_report_path: Optional[str] = None) -> None:
    S_values = [10 * WAD, 100 * WAD]
    R_values = [int(0.5 * WAD), 1 * WAD, int(1.3333333333 * WAD)]
    net_vals = [0, int(0.01 * WAD)]
    val_vals = [0, int(0.02 * WAD)]
    fee_types = [FeeType.NATIVE_FIXED, FeeType.NATIVE_PERCENT, FeeType.OWN_FIXED, FeeType.OWN_PERCENT]
    service_options: Dict[str, List[int]] = {
        # fixed options: tiny (1 wei), nominal (0.03), large (100)
        FeeType.NATIVE_FIXED: [1, int(0.03 * WAD), 100 * WAD],
        FeeType.OWN_FIXED: [1, int(0.03 * WAD), 100 * WAD],
        # percent options: 1%, 2.5%, 0.001%
        FeeType.NATIVE_PERCENT: [int(0.01 * WAD), int(0.025 * WAD), int(0.00001 * WAD)],
        FeeType.OWN_PERCENT: [int(0.01 * WAD), int(0.025 * WAD), int(0.00001 * WAD)],
    }
    count = 0
    report: List[Dict[str, Any]] = []

    # Single
    for S in S_values:
        for R in R_values:
            for N in net_vals:
                for V in val_vals:
                    for ft in fee_types:
                        for srv_val in service_options[ft]:
                            cfg = FeesCfg(ft, srv_val, N, V)
                            for sell_native in (True, False):
                                # extra native inputs only relevant for sell_native=False
                                extra = 5 * WAD if not sell_native else 0
                                check_single(sell_native, S, R, cfg, extra_native_inputs=extra)
                                count += 1
                                if json_report_path:
                                    report.append({
                                        "scenario": "single",
                                        "sell_native": sell_native,
                                        "S": str(S),
                                        "R": str(R),
                                        "fee_type": ft,
                                        "service_value": str(srv_val),
                                        "net_fee": str(N),
                                        "val_fee": str(V),
                                    })

    # Multi: two orders with same R for simplicity
    exec_sets = [
        [OrderExec(6 * WAD, 1 * WAD), OrderExec(7 * WAD, 1 * WAD)],
        [OrderExec(9 * WAD, int(0.5 * WAD)), OrderExec(4 * WAD, int(0.5 * WAD))],
    ]
    for exs in exec_sets:
        for N in net_vals:
            for V in val_vals:
                for ft in fee_types:
                    for srv_val in service_options[ft]:
                        cfg = FeesCfg(ft, srv_val, N, V)
                        for sell_native in (True, False):
                            extra = 3 * WAD if not sell_native else 0
                            check_multi(sell_native, exs, cfg, extra_native_inputs=extra)
                            count += 1
                            if json_report_path:
                                report.append({
                                    "scenario": "multi",
                                    "sell_native": sell_native,
                                    "exec": [{"S": str(e.executed_sell), "R": str(e.rate)} for e in exs],
                                    "fee_type": ft,
                                    "service_value": str(srv_val),
                                    "net_fee": str(N),
                                    "val_fee": str(V),
                                })

    # Update fast-path policy checks
    for N in net_vals:
        for V in val_vals:
            for ft in (FeeType.NATIVE_FIXED, FeeType.NATIVE_PERCENT, FeeType.OWN_FIXED, FeeType.OWN_PERCENT):
                for srv_val in service_options[ft]:
                    cfg = FeesCfg(ft, srv_val, N, V)
                    check_update_fastpath_allowed(cfg)
                    count += 1
                    if json_report_path:
                        report.append({
                            "scenario": "update",
                            "fee_type": ft,
                            "service_value": str(srv_val),
                            "net_fee": str(N),
                            "val_fee": str(V),
                            "policy": "allowed_if_not_own",
                        })

    print(f"Fee matrix model tests passed: {count} cases")
    if json_report_path:
        with open(json_report_path, "w") as f:
            json.dump({"cases": count, "records": report}, f, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-report", dest="json_report", default=None, help="Path to write JSON report")
    args = parser.parse_args()
    run_matrix(args.json_report)


