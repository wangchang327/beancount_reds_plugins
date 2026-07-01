import unittest

from beancount import loader
from beancount.parser import cmptest


class DafMirrorPluginTest(cmptest.TestCase):
    @loader.load_doc()
    def test_mirrors_transactions_for_matching_asset_prefix(
        self, entries, errors, options_map
    ):
        """
        plugin "daf_mirror" "Assets:DAF:Brokerage-DAF"

        2020-01-01 open Assets:DAF:Brokerage-DAF:VTI
        2020-01-01 open Assets:DAF:Brokerage-DAF:USD
        2020-01-01 open Liabilities:DAF:Brokerage-DAF:VTI
        2020-01-01 open Liabilities:DAF:Brokerage-DAF:USD
        2020-01-01 open Income:Investments:Tax-Free:Capital-Gains:DAF:Brokerage-DAF:VTI

        2020-01-15 * "Sell" "xxx"
          Assets:DAF:Brokerage-DAF:VTI                            -20 VTI {20.00 USD}
          Income:Investments:Tax-Free:Capital-Gains:DAF:Brokerage-DAF:VTI   0 USD
          Assets:DAF:Brokerage-DAF:USD                             400 USD
        """
        self.assertFalse(errors)
        self.assertEqualEntries(
            """
            2020-01-01 open Assets:DAF:Brokerage-DAF:VTI
            2020-01-01 open Assets:DAF:Brokerage-DAF:USD
            2020-01-01 open Liabilities:DAF:Brokerage-DAF:VTI
            2020-01-01 open Liabilities:DAF:Brokerage-DAF:USD
            2020-01-01 open Income:Investments:Tax-Free:Capital-Gains:DAF:Brokerage-DAF:VTI

            2020-01-15 * "Sell" "xxx"
              Assets:DAF:Brokerage-DAF:VTI                          -20 VTI {20.00 USD, 2020-01-15}
              Income:Investments:Tax-Free:Capital-Gains:DAF:Brokerage-DAF:VTI   0 USD
              Assets:DAF:Brokerage-DAF:USD                           400 USD

            2020-01-15 * "Mirror Sell" "xxx"
              daf_mirror_generated: TRUE
              Liabilities:DAF:Brokerage-DAF:VTI                      20 VTI {20.00 USD, 2020-01-15}
              Income:Investments:Tax-Free:Capital-Gains:DAF:Brokerage-DAF:VTI   0 USD
              Liabilities:DAF:Brokerage-DAF:USD                     -400 USD
            """,
            entries,
        )

    @loader.load_doc()
    def test_skips_transactions_with_other_asset_accounts(
        self, entries, errors, options_map
    ):
        """
        plugin "daf_mirror" "Assets:DAF:Brokerage-DAF"

        2020-01-01 open Assets:DAF:Brokerage-DAF:VTI
        2020-01-01 open Assets:DAF:Brokerage-DAF:USD
        2020-01-01 open Assets:Brokerage:Cash
        2020-01-01 open Income:Investments:Tax-Free:Capital-Gains:DAF:Brokerage-DAF:VTI

        2020-01-15 * "Sell" "xxx"
          Assets:DAF:Brokerage-DAF:VTI                            -20 VTI {20.00 USD}
          Income:Investments:Tax-Free:Capital-Gains:DAF:Brokerage-DAF:VTI  -1.00 USD
          Assets:DAF:Brokerage-DAF:USD                             400 USD
          Assets:Brokerage:Cash                                    1.00 USD
        """
        self.assertFalse(errors)
        self.assertEqualEntries(
            """
            2020-01-01 open Assets:DAF:Brokerage-DAF:VTI
            2020-01-01 open Assets:DAF:Brokerage-DAF:USD
            2020-01-01 open Assets:Brokerage:Cash
            2020-01-01 open Income:Investments:Tax-Free:Capital-Gains:DAF:Brokerage-DAF:VTI

            2020-01-15 * "Sell" "xxx"
              Assets:DAF:Brokerage-DAF:VTI                          -20 VTI {20.00 USD, 2020-01-15}
              Income:Investments:Tax-Free:Capital-Gains:DAF:Brokerage-DAF:VTI  -1.00 USD
              Assets:DAF:Brokerage-DAF:USD                           400 USD
              Assets:Brokerage:Cash                                  1.00 USD
            """,
            entries,
        )


if __name__ == "__main__":
    unittest.main()
