import math
import random

from quick_sort import quick_sort

bytes_example = [random.randint(1024**3, 5000**3) for _ in range(10)]


class BytePairing:
    def __init__(self, _bytes: list[int]) -> None:
        self._bytes = _bytes

    def divider(self) -> dict[str, list]:
        self._bytes = quick_sort(self._bytes)
        self.mid_point = math.ceil(len(self._bytes) / 2)
        bigger_half, smaller_half = list(self._bytes[self.mid_point :]), list(
            self._bytes[: self.mid_point]
        )

        return {"smaller_half": smaller_half, "bigger_half": bigger_half[::-1]}

    def parallelize(self):
        self.byte_dict = self.divider()
        self.new_arr = []
        for _ in range(self.mid_point):
            self.new_arr.append(self.byte_dict["smaller_half"][_])
            self.new_arr.append(self.byte_dict["bigger_half"][_])
        return self.new_arr
