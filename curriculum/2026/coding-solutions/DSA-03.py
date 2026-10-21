def product_except_self(nums: list[int]) -> list[int]:
    """Return products of all other elements using prefix and suffix passes."""
    out = [1] * len(nums)
    prefix = 1
    for i in range(len(nums)):
        out[i] = prefix
        prefix *= nums[i]
    suffix = 1
    for i in range(len(nums) - 1, -1, -1):
        out[i] *= suffix
        suffix *= nums[i]
    return out
