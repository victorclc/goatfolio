class NationalTaxIdUtils:
    @staticmethod
    def is_valid(tax_id):
        clean_tax_id = [int(digit) for digit in tax_id if digit.isdigit()]

        if len(clean_tax_id) != 11 or len(set(clean_tax_id)) == 1:
            return False

        sum_of_products = sum(a * b for a, b in zip(clean_tax_id[0:9], range(10, 1, -1)))
        expected_digit = (sum_of_products * 10 % 11) % 10
        if clean_tax_id[9] != expected_digit:
            return False

        sum_of_products = sum(a * b for a, b in zip(clean_tax_id[0:10], range(11, 1, -1)))
        expected_digit = (sum_of_products * 10 % 11) % 10
        if clean_tax_id[10] != expected_digit:
            return False
        return True
