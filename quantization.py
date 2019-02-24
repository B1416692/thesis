import utilities
import numpy as np

class Quantizer:
    def __init__(self, model, parameter_type):
        self.model = model
        self.parameter_type = parameter_type

    def quantize(self, element):
        raise NotImplementedError("I'm still working things out...")

class RangeQuantizer(Quantizer):
    def __init__(self, model, parameter_type, n):
        super().__init__(model, parameter_type)
        self.n = n
        self.quantizationDomain = [0]

    def quantize(self, element):
        return min(self.quantizationDomain, key=lambda x:abs(x-element))

# TODO: For now, values is assumed to contain elments BOTH greater and smaller than 0. Make it universal.
# TODO: Also, values is supposed to be non empthy. Check.
class AsymmetricUniformQuantizer(RangeQuantizer):
    def __init__(self, model, parameter_type, n, outliers_filter=0):
        super().__init__(model, parameter_type, n)
        values = utilities.get(self.model, self.parameter_type)
        min_value = np.percentile(values, 0 + outliers_filter)
        max_value = np.percentile(values, 100 - outliers_filter)
        negative_gap = min_value / ((self.n - 1) / 2)
        positive_gap = max_value / ((self.n - 1) / 2)
        for i in range(1, int((self.n - 1) / 2) + 1):
            self.quantizationDomain.append(i * negative_gap)
            self.quantizationDomain.append(i * positive_gap)

class SymmetricUniformQuantizer(RangeQuantizer):
    def __init__(self, model, parameter_type, n, outliers_filter=0):
        super().__init__(model, parameter_type, n)
        values = utilities.get(self.model, self.parameter_type)
        min_value = np.percentile(values, 0 + outliers_filter)
        max_value = np.percentile(values, 100 - outliers_filter)
        maximum = max(abs(min_value), abs(max_value))
        gap = maximum / ((self.n - 1) / 2)
        for i in range(1, int((self.n - 1) / 2) + 1):
            self.quantizationDomain.append(i * gap)
            self.quantizationDomain.append(-i * gap)

class AsymmetricDensityBasedQuantizer(RangeQuantizer):
    def __init__(self, model, parameter_type, n):
        super().__init__(model, parameter_type, n)
        values = utilities.get(self.model, self.parameter_type)
        negative_values = list(filter((0).__lt__, values))
        negative_values = [abs(value) for value in negative_values]
        positive_values = list(filter((0).__gt__, values))
        percentile_gap = 100 / ((self.n - 1) / 2)
        for i in range(0, int((self.n - 1) / 2)):
            self.quantizationDomain.append(-np.percentile(negative_values, 100 - percentile_gap * i))
            self.quantizationDomain.append(np.percentile(positive_values, 100 - percentile_gap * i))

class SymmetricDensityBasedQuantizer(RangeQuantizer):
    def __init__(self, model, parameter_type, n):
        super().__init__(model, parameter_type, n)
        values = utilities.get(self.model, self.parameter_type)
        negative_values = list(filter((0).__lt__, values))
        negative_values = [abs(value) for value in negative_values]
        positive_values = list(filter((0).__gt__, values))
        maximum_negative = max(negative_values)
        maximum_positive = max(positive_values)
        to_use_values = []
        if maximum_negative > maximum_positive:
            to_use_values = negative_values
        else:
            to_use_values = positive_values
        percentile_gap = 100 / ((self.n - 1) / 2)
        for i in range(0, int((self.n - 1) / 2)):
            self.quantizationDomain.append(-np.percentile(to_use_values, 100 - percentile_gap * i))
            self.quantizationDomain.append(np.percentile(to_use_values, 100 - percentile_gap * i))