"""Topic 10 — GitOps reconcile + budget hard-cap (STARTER).

Your job: implement `reconcile()` (make live match desired, prune extras) and the
`BudgetGuard.record` deny (at 100% of budget, flip `denied` so the LLM can't be called).
`self_heal` and `can_invoke_llm` are wired to call your code.
"""
from __future__ import annotations

from dataclasses import dataclass


def reconcile(desired: dict, live: dict) -> list:
    # TODO (Topic 10): for each key in desired, if live differs, sync it (record the
    #   action). Then prune keys in live that aren't in desired. Return the actions.
    return []     # placeholder: no reconciliation yet


def self_heal(desired: dict, live: dict, drift: dict) -> list:
    live.update(drift)                    # someone ran `kubectl edit`
    return reconcile(desired, live)       # your reconcile() reverts it


@dataclass
class BudgetGuard:
    limit_usd: float
    spend_usd: float = 0.0
    denied: bool = False

    def record(self, usd: float) -> None:
        self.spend_usd += usd
        # TODO (Topic 10): at 100% of limit_usd, set self.denied = True
        #   (attach the deny IAM policy — stop the spend, don't just alarm).

    def can_invoke_llm(self) -> bool:
        return not self.denied
