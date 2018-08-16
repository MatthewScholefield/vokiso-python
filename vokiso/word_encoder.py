from os.path import dirname, abspath, join

root = abspath(join(dirname(abspath(__file__)), '..'))


def load_words():
    with open(join(root, 'words.txt')) as f:
        return f.read().strip().split('\n')


def to_base_n(num, n):
    digits = []
    while num > 0:
        num, digit = divmod(num, n)
        digits.insert(0, digit)
    return digits


def to_word_indices(address):
    ip, port = address.split(':')
    nums = [int(i) for i in ip.split('.') + [port]]
    return to_base_n(as_single_number(nums, [256, 256, 256, 256, 65536]), 1000)


def as_single_number(nums, max_nums):
    combined = 0
    place = 1
    for num, max_num in reversed(list(zip(nums, max_nums))):
        combined += num * place
        place *= max_num
    return combined


def to_pairing_code(address):
    words = load_words()
    return ' '.join(words[i] for i in to_word_indices(address))


def as_multiple_numbers(combined, max_nums):
    nums = []
    for max_num in reversed(max_nums):
        combined, num = divmod(combined, max_num)
        nums.append(num)
    if combined > 0:
        raise ValueError('Invalid combined number: ' + str(combined))
    return nums


def from_pairing_code(word_digits):
    words = load_words()
    nums = [words.index(word) for word in word_digits.split()]
    combined = as_single_number(nums, [len(words)] * len(nums))
    nums = reversed(as_multiple_numbers(combined, [256, 256, 256, 256, 65536]))
    return '{}.{}.{}.{}:{}'.format(*nums)
