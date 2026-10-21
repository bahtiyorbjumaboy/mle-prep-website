def course_order(num_courses: int, prerequisites: list[list[int]]) -> list[int]:
    """Return one valid order to take all courses, or `[]` if that is impossible.

    Target O(V + E).

    Args:
        num_courses: Courses are labelled `0..num_courses-1`.
        prerequisites: Pairs `[course, prereq]` meaning `prereq` must be taken before
            `course`; pairs may repeat.

    Returns:
        A list containing every course exactly once with each prerequisite before the
        courses that need it, or `[]` if the prerequisites contain a cycle.
    """
    raise NotImplementedError("TODO: implement DSA-22")
