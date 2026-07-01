# DAF Mirror Plugin

This Beancount plugin generates a mirrored transaction for entries that touch a configured `Assets:` account prefix.

The mirrored transaction:
- includes all original postings, with mirrored signs and account types
- changes mirrored `Assets:` accounts to `Liabilities:`
- changes mirrored `Liabilities:` accounts to `Assets:`
- negates each mirrored posting amount
- preserves cost and price annotations
- marks generated entries with `daf_mirror_generated: TRUE`

Transactions are skipped entirely if they contain any other `Assets:*` posting outside the configured prefix.

## Usage

Put `daf_mirror.py` somewhere on your Beancount `PYTHONPATH`, then load it from your ledger:

```beancount
plugin "daf_mirror" "Assets:DAF:Brokerage-DAF"
```

## Sample Config

You can pass either a plain account prefix string:

```beancount
plugin "daf_mirror" "Assets:DAF:Brokerage-DAF"
```

Or a small config dict:

```beancount
plugin "daf_mirror" "{'account_prefix': 'Assets:DAF:Brokerage-DAF', 'payee_prefix': 'Mirror '}"
```

## Example

Input transaction:

```beancount
2020-01-15 * "Sell" "xxx"
  Assets:DAF:Brokerage-DAF:VTI                           -20 VTI {20 USD}
  Income:Investments:Tax-Free:Capital-Gains:DAF:Brokerage-DAF:VTI
  Assets:DAF:Brokerage-DAF:USD                            1000 USD
```

Generated mirror:

```beancount
2020-01-15 * "Mirror Sell" "xxx"
  daf_mirror_generated: TRUE
  Liabilities:DAF:Brokerage-DAF:VTI                      20 VTI {20 USD}
  Income:Investments:Tax-Free:Capital-Gains:DAF:Brokerage-DAF:VTI
  Liabilities:DAF:Brokerage-DAF:USD                     -1000 USD
```
