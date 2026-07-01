"""Generate mirrored liability transactions for a configured DAF asset prefix."""

from __future__ import annotations

from ast import literal_eval
from typing import Optional

from beancount.core import amount, data

__plugins__ = ("mirror_daf_transactions",)

META_GENERATED = "daf_mirror_generated"
DEFAULT_ACCOUNT_PREFIX = "Assets:DAF"
DEFAULT_PAYEE_PREFIX = "Mirror "


def mirror_daf_transactions(entries, options_map, config_str=None):
    """Insert mirrored transactions for entries that touch the configured asset prefix."""
    del options_map

    config = _parse_config(config_str)
    account_prefix = config["account_prefix"]
    payee_prefix = config["payee_prefix"]

    errors = []
    new_entries = []
    for entry in entries:
        new_entries.append(entry)
        if _should_mirror(entry, account_prefix):
            mirrored_entry = _mirror_transaction(entry, account_prefix, payee_prefix)
            if mirrored_entry is not None:
                new_entries.append(mirrored_entry)
    return new_entries, errors


def _parse_config(config_str: Optional[str]) -> dict[str, str]:
    if not config_str:
        return {
            "account_prefix": DEFAULT_ACCOUNT_PREFIX,
            "payee_prefix": DEFAULT_PAYEE_PREFIX,
        }

    try:
        parsed = literal_eval(config_str)
    except (SyntaxError, ValueError):
        parsed = config_str

    if isinstance(parsed, dict):
        account_prefix = parsed.get("account_prefix", DEFAULT_ACCOUNT_PREFIX)
        payee_prefix = parsed.get("payee_prefix", DEFAULT_PAYEE_PREFIX)
    else:
        account_prefix = str(parsed)
        payee_prefix = DEFAULT_PAYEE_PREFIX

    return {
        "account_prefix": account_prefix.strip() or DEFAULT_ACCOUNT_PREFIX,
        "payee_prefix": payee_prefix,
    }


def _should_mirror(entry, account_prefix: str) -> bool:
    return (
        isinstance(entry, data.Transaction)
        and not entry.meta.get(META_GENERATED)
        and any(
            posting.account.startswith(account_prefix) for posting in entry.postings
        )
        and not any(
            posting.account.startswith("Assets:")
            and not posting.account.startswith(account_prefix)
            for posting in entry.postings
        )
    )


def _mirror_transaction(
    entry: data.Transaction, account_prefix: str, payee_prefix: str
) -> Optional[data.Transaction]:
    meta = dict(entry.meta)
    meta[META_GENERATED] = True

    payee = entry.payee
    narration = entry.narration
    if payee:
        payee = f"{payee_prefix}{payee}"
    elif narration:
        narration = f"{payee_prefix}{narration}"

    del account_prefix

    postings = [_mirror_posting(posting) for posting in entry.postings]
    if not postings:
        return None

    return entry._replace(
        meta=meta, payee=payee, narration=narration, postings=postings
    )


def _mirror_posting(posting: data.Posting) -> data.Posting:
    return posting._replace(
        account=_mirror_account(posting.account),
        units=_negate_amount(posting.units),
        cost=posting.cost,
        price=posting.price,
    )


def _mirror_account(account_name: str) -> str:
    if account_name.startswith("Assets:"):
        return "Liabilities:" + account_name[len("Assets:") :]
    if account_name.startswith("Liabilities:"):
        return "Assets:" + account_name[len("Liabilities:") :]
    return account_name


def _negate_amount(value: Optional[amount.Amount]) -> Optional[amount.Amount]:
    if value is None:
        return None
    return amount.Amount(-value.number, value.currency)
